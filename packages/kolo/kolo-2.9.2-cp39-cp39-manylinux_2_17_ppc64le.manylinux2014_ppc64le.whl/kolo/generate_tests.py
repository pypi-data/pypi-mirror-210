from __future__ import annotations

import json
import platform
import re
from ast import literal_eval
from collections import Counter
from datetime import datetime, timedelta
from decimal import Decimal
from functools import lru_cache, total_ordering
from textwrap import dedent
from typing import Dict, List, Set
from urllib.parse import parse_qsl

import sqlglot
from jinja2 import Environment, PackageLoader
from more_itertools import unique_everseen

from .config import load_config
from .db import load_schema_for_commit_sha, load_trace_from_db, setup_db
from .django_schema import get_schema
from .git import COMMIT_SHA
from .version import __version__ as kolo_version


DATABASES = {
    "postgresql": "postgres",
}


class KoloPackageLoader(PackageLoader):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Work around UNC path mishandling:
        # https://github.com/pallets/jinja/issues/1675
        if platform.system() == "Windows":
            unc_prefix = "\\\\?\\"
            if self._template_root.startswith(unc_prefix):  # pragma: no cover
                self._template_root = self._template_root[len(unc_prefix) :]


def maybe_black(rendered):
    try:
        from black import format_file_contents
        from black.mode import Mode
        from black.parsing import InvalidInput
    except ImportError:  # pragma: no cover
        return rendered

    try:
        return format_file_contents(
            rendered, fast=True, mode=Mode(magic_trailing_comma=False)
        )
    except InvalidInput:  # pragma: no cover
        return rendered


env = Environment(loader=KoloPackageLoader("kolo"))


def _format_header(header: str) -> str:
    header = header.upper().replace("-", "_")
    if header in ("CONTENT_LENGTH", "CONTENT_TYPE"):
        return header
    return f"HTTP_{header}"


UUID_REPR_REGEX = re.compile(
    r"UUID\(\'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\'\)"
)
DECIMAL_REPR_REGEX = re.compile(r"Decimal\('(\d+.?\d+?)'\)")
TIMEDELTA_REPR_REGEX = re.compile(
    r"datetime.timedelta\((?:days=(\d+),? ?)?(?:seconds=(\d+),? ?)?(?:microseconds=(\d+))?\)"
)


def parse_value(value, column_schema):
    if column_schema["django_field"] == "django.db.models.fields.UUIDField":
        uuid_match = UUID_REPR_REGEX.match(str(value))
        if uuid_match:
            value = uuid_match[1]
    elif column_schema["django_field"] == "django.db.models.fields.json.JSONField":
        value = json.loads(value)
    elif column_schema["django_field"] == "django.db.models.fields.DecimalField":
        decimal_match = DECIMAL_REPR_REGEX.match(str(value))
        if decimal_match:
            value = Decimal(decimal_match[1])
    elif column_schema["django_field"] == "django.db.models.fields.DurationField":
        if isinstance(value, str):
            timedelta_match = TIMEDELTA_REPR_REGEX.match(value)
            if timedelta_match:  # pragma: no branch
                groups = [int(g) if g else 0 for g in timedelta_match.groups()]
                value = timedelta(
                    days=groups[0], seconds=groups[1], microseconds=groups[2]
                )
        else:
            value = timedelta(microseconds=value)
    return value


class TooComplicatedError(Exception):
    pass


@total_ordering
class DjangoField:
    def __init__(self, name, value, schema=None):
        self.name = name
        self.value_repr = repr(value)
        self.raw_value = value
        self.value = repr(value) if isinstance(value, str) else value
        self.schema = schema

    @classmethod
    def from_column(cls, column, value, table_schema):
        field_schema = table_schema["fields"][column.name]
        name = field_schema["field_name"]
        value = parse_value(value, field_schema)
        return cls(name, value, field_schema)

    @classmethod
    def from_identifier(cls, identifier, value, table_schema):
        field_schema = table_schema["fields"][identifier.name]
        if isinstance(value, sqlglot.expressions.Null):
            value = None
        elif isinstance(value, sqlglot.expressions.Boolean):
            value = value.this
        elif isinstance(value, sqlglot.expressions.Cast):
            value = value.name
        elif value.is_string:
            value = value.name
        else:
            value = literal_eval(value.name)
        value = parse_value(value, field_schema)
        return cls(identifier.name, value, field_schema)

    @classmethod
    def from_eq(cls, eq):
        name = eq.left.name
        right = eq.right
        if isinstance(right, sqlglot.expressions.Literal):
            value = right.name
        elif isinstance(right, sqlglot.expressions.Boolean):
            value = right.this
        elif isinstance(right, sqlglot.expressions.Cast):
            value = right.name
            # TODO: Do something reasonable with `right.to`
        elif isinstance(right, sqlglot.expressions.Paren):
            raise TooComplicatedError()
        else:
            raise TooComplicatedError()  # pragma: no cover
        return cls(name, value, {})

    def __eq__(self, other):
        return (self.name, self.value) == (other.name, other.value)

    def __lt__(self, other) -> bool:
        if self.name == other.name:
            return self.value < other.value
        return self.name < other.name

    def __hash__(self):
        return hash((self.name, self.value))

    def __repr__(self):
        return f'DjangoField("{self.name}", {self.value})'

    def assert_equal_template(self, variable_name):
        return f"self.assertEqual({variable_name}.{self.name}, {self.value})"


def find_pk(fields):
    for field in fields:
        if field.schema["primary_key"]:
            return field
    return None  # pragma: no cover


class VariableNames:
    def __init__(self):
        self.counts: Counter = Counter()
        self.names = {}

    def next_variable_name(self, verbose_name, field):
        full_key = verbose_name, field.name, field.value_repr
        try:
            return self.names[full_key]
        except KeyError:
            pass

        key = verbose_name, field.name
        self.counts[key] += 1
        suffix = self.counts[key]
        if suffix == 1:
            name = verbose_name
        else:
            name = f"{verbose_name}_{suffix}"
        self.names[full_key] = name
        return name


def is_auto_now(field):
    django_field = field.schema["django_field"]
    if django_field not in (
        "django.db.models.fields.DateTimeField",
        "django.db.models.fields.DateField",
    ):
        return False
    return field.schema["auto_now"] or field.schema["auto_now_add"]


class DjangoCreate:
    def __init__(
        self,
        table,
        model,
        primary_key,
        values,
        variable_name,
        import_path=None,
        query=None,
    ):
        self.table = table
        self.model = model
        self.primary_key = primary_key
        self.values = values
        self.import_path = import_path
        self.query = query
        self.variable_name = variable_name

    @classmethod
    def from_raw(cls, table, values, query, schema_data, names):
        module = schema_data[table]["model_module"]
        model = schema_data[table]["model_name"]
        values = tuple(values)
        primary_key = find_pk(values)
        verbose_name = schema_data[table]["verbose_name"]
        variable_name = names.next_variable_name(verbose_name, primary_key)
        return cls(
            table,
            f"{module}.{model}",
            primary_key,
            values,
            variable_name,
            f"import {module}",
            query,
        )

    def update_fields(self, names, schema):
        fields = []
        for field in self.values:
            if field.schema["primary_key"]:
                continue
            if field.schema["null"] and field.value is None:
                continue
            if is_auto_now(field):
                continue
            if "default" in field.schema:
                default_schema = field.schema["default"]
                if repr(default_schema["value"]) == field.value_repr:
                    continue
                if "type" in default_schema:
                    field_type = default_schema["type"]
                    value = default_schema["value"]
                    if field_type == "Decimal" and field.value == Decimal(value):
                        continue
                    if (  # pragma: no branch
                        field_type == "timedelta" and field.value == timedelta(**value)
                    ):
                        continue
            if field.schema["is_relation"]:
                related_model = field.schema["related_model"]
                verbose_name = schema[related_model]["verbose_name"]
                related_pk = field.schema["related_pk"]
                try:
                    field.value = names.names[
                        (verbose_name, related_pk, field.value_repr)
                    ]
                except KeyError:
                    field.name = field.schema["field_attname"]
            fields.append(field)
        self.values = tuple(fields)

    def __eq__(self, other):
        return (self.table, self.model, self.values, self.variable_name) == (
            other.table,
            other.model,
            other.values,
            other.variable_name,
        )

    def __hash__(self):
        return hash((self.table, self.model, self.values, self.variable_name))

    def __repr__(self):
        return dedent(
            f"""\
            DjangoCreate(
                "{self.table}",
                "{self.model}",
                {self.primary_key},
                {self.values},
                "{self.variable_name}",
            )"""
        )

    @property
    def template_parts(self):
        yield f"{self.variable_name}, _created = {self.model}.objects.get_or_create("
        for field in self.values:
            yield f"{field.name}={field.value},"
        defaults = {self.primary_key.name: self.primary_key.raw_value}
        yield f"defaults={defaults},"
        yield ")"


class AssertSelect:
    def __init__(self, model, fields, import_path=None, query=None):
        self.model = model
        self.fields = fields
        self.query = query
        self.import_path = import_path

    @classmethod
    def from_raw(cls, fields, query, table_schema):
        module = table_schema["model_module"]
        model = table_schema["model_name"]
        return cls(f"{module}.{model}", fields, f"import {module}", query)

    def update_fields(self, names, schema):
        fields = []
        for field in self.fields:
            if field.schema["primary_key"]:
                continue
            if field.schema["django_field"] == "django.db.models.fields.DateTimeField":
                continue

            if field.schema["is_relation"]:
                related_model = field.schema["related_model"]
                verbose_name = schema[related_model]["verbose_name"]
                related_pk = field.schema["related_pk"]
                try:
                    field.value = names.names[
                        (verbose_name, related_pk, field.value_repr)
                    ]
                except KeyError:  # pragma: no cover
                    pass
                else:
                    field.name = field.schema["field_name"]
            fields.append(field)
        self.fields = fields

    def __eq__(self, other):
        if not isinstance(other, AssertSelect):
            return NotImplemented  # pragma: no cover
        return (self.model, self.fields) == (other.model, other.fields)

    def __repr__(self):
        return dedent(  # pragma: no cover
            f"""\
            AssertSelect(
                "{self.model}",
                {self.fields},
            )"""
        )

    @property
    def template_parts(self):
        yield f"self.assertTrue({self.model}.objects.filter("
        for field in self.fields:
            yield f"{field.name}={field.value},"
        yield ").exists())"


class AssertInsert:
    def __init__(self, variable_name, model, fields, import_path=None, query=None):
        self.variable_name = variable_name
        self.model = model
        self.fields = fields
        self.query = query
        self.import_path = import_path

    @classmethod
    def from_raw(cls, fields, query, table_schema, names, primary_key):
        module = table_schema["model_module"]
        model = table_schema["model_name"]
        verbose_name = table_schema["verbose_name"]
        variable_name = names.next_variable_name(verbose_name, primary_key)
        return cls(
            variable_name, f"{module}.{model}", fields, f"import {module}", query
        )

    def update_fields(self, names, schema):
        fields = []
        for field in self.fields:
            if field.schema["primary_key"]:
                continue  # pragma: no cover
            if field.schema["django_field"] == "django.db.models.fields.DateTimeField":
                continue  # pragma: no cover

            if field.schema["is_relation"]:
                related_model = field.schema["related_model"]
                verbose_name = schema[related_model]["verbose_name"]
                related_pk = field.schema["related_pk"]
                try:
                    field.value = names.names[
                        (verbose_name, related_pk, field.value_repr)
                    ]
                except KeyError:  # pragma: no cover
                    pass
                else:
                    field.name = field.schema["field_name"]
            fields.append(field)
        self.fields = fields

    def __eq__(self, other):
        if not isinstance(other, AssertInsert):
            return NotImplemented  # pragma: no cover
        return (self.variable_name, self.model, self.fields) == (
            other.variable_name,
            other.model,
            other.fields,
        )

    def __repr__(self):
        return dedent(  # pragma: no cover
            f"""\
            AssertInsert(
                "{self.variable_name}",
                "{self.model}",
                {self.fields},
            )"""
        )

    @property
    def template_parts(self):
        yield f"{self.variable_name} = {self.model}.objects.get("
        for field in self.fields:
            yield f"{field.name}={field.value},"
        yield ")"


class AssertUpdate:
    def __init__(self, variable_name, fields, query=None):
        self.variable_name = variable_name
        self.fields = fields
        self.query = query

    def __repr__(self):
        return dedent(
            f"""\
            AssertUpdate(
                "{self.variable_name}",
                {self.fields},
            )"""
        )

    def __eq__(self, other):
        if not isinstance(other, AssertUpdate):
            return NotImplemented  # pragma: no cover
        return (self.variable_name, self.fields) == (other.variable_name, other.fields)

    @property
    def template_parts(self):
        yield f"{self.variable_name}.refresh_from_db()"
        for field in self.fields:
            yield field.assert_equal_template(self.variable_name)


class DjangoQuery:
    def __init__(self, table, query):
        self.table = table
        self.query = query

    def __repr__(self):
        return f'DjangoQuery("{self.table}", {self.query})'

    def __eq__(self, other):
        return (self.table, self.query) == (
            other.table,
            other.query,
        )  # pragma: no cover


def make_table_sort_key(schema_data):
    tables = {}
    for table, data in schema_data.items():
        foreign_keys = []
        for field in data["fields"].values():
            if field["is_relation"] and not field["null"]:
                foreign_keys.append(field["related_model"])
        tables[table] = foreign_keys

    @lru_cache(maxsize=None)
    def table_depth(table):
        related_tables = tables[table]

        if len(related_tables) == 0:
            return 0
        return max(table_depth(related) for related in related_tables) + 1

    def sort_key(create):
        return (table_depth(create.table), create.table, create.values)

    return sort_key


def parse_columns(columns, row, schema_data):
    columns_by_table: Dict[str, List[DjangoField]] = {}
    for column, value in zip(columns, row):
        if not isinstance(column, sqlglot.exp.Column):
            continue

        table_schema = schema_data[column.table]
        field = DjangoField.from_column(column, value, table_schema)
        columns_by_table.setdefault(column.table, []).append(field)
    return columns_by_table


def build_update_assert_fields(columns, schema_fields):
    fields = []
    for eq in columns:
        if not isinstance(eq, sqlglot.expressions.EQ):
            continue
        try:
            field = DjangoField.from_eq(eq)
        except TooComplicatedError:
            continue
        django_field = schema_fields[field.name]["django_field"]
        if django_field == "django.db.models.fields.DateTimeField":
            continue
        fields.append(field)
    return fields


def build_insert_assert_fields(columns, table_schema):
    fields = []
    for identifier, value in columns:
        field = DjangoField.from_identifier(identifier, value, table_schema)
        django_field = table_schema["fields"][field.name]["django_field"]
        if django_field == "django.db.models.fields.DateTimeField":
            continue
        fields.append(field)
    return fields


def parse_sql_queries(sql_queries, schema_data):
    names = VariableNames()
    # each select needs to become an insert
    inserts = []
    imports = set()
    asserts = []
    seen_mutations: Dict[str, Set[str]] = {}
    for query in sql_queries:
        if query["query_data"] is None:
            continue

        database = query["database"]
        database = DATABASES.get(database, database)
        try:
            parsed_query = sqlglot.parse_one(query["query"], read=database)
        except sqlglot.errors.ParseError as e:  # pragma: no cover
            print("Error parsing query:")
            print(query["query"])
            print(e.errors)
            continue

        if isinstance(parsed_query, sqlglot.exp.Select):
            columns = [column for (_key, column) in parsed_query.iter_expressions()]
            for batch in query["query_data"]:
                # Skip queries with no columns, eg .count(), .exists()
                if not any(
                    isinstance(column, sqlglot.exp.Column) for column in columns
                ):
                    continue
                for row in batch:
                    columns_by_table = parse_columns(columns, row, schema_data)

                    for table, row in columns_by_table.items():
                        pk = find_pk(row)
                        if pk.value_repr in seen_mutations.setdefault(table, set()):
                            asserts.append(
                                AssertSelect.from_raw(row, query, schema_data[table])
                            )
                        else:
                            create = DjangoCreate.from_raw(
                                table, row, query, schema_data, names
                            )
                            inserts.append(create)
                            imports.add(create.import_path)
        else:
            _table = parsed_query.find(sqlglot.exp.Table)
            if _table is None:
                continue  # pragma: no cover
            table_name = _table.name
            table_schema = schema_data[table_name]
            columns = [column for (_key, column) in parsed_query.iter_expressions()]
            if isinstance(parsed_query, sqlglot.expressions.Update):
                where = parsed_query.find(sqlglot.expressions.Where)
                if where is None:
                    continue  # pragma: no cover

                fields = build_update_assert_fields(columns, table_schema["fields"])

                lookup_name = where.this.left.name
                lookup_value = where.this.right.name
                verbose_name = table_schema["verbose_name"]
                variable_name = names.names[(verbose_name, lookup_name, lookup_value)]
                assert_update = AssertUpdate(variable_name, fields, query)
                asserts.append(assert_update)
                if table_schema["fields"][lookup_name][  # pragma: no branch
                    "primary_key"
                ]:
                    seen_mutations.setdefault(table_name, set()).add(lookup_value)
            elif isinstance(  # pragma: no branch
                parsed_query, sqlglot.expressions.Insert
            ):
                sql_schema = parsed_query.find(sqlglot.expressions.Schema)
                sql_values_tuple = parsed_query.find(sqlglot.expressions.Tuple)
                if sql_schema is None or sql_values_tuple is None:
                    continue  # pragma: no cover
                schema_columns = [
                    column
                    for (_key, column) in sql_schema.iter_expressions()
                    if isinstance(column, sqlglot.expressions.Identifier)
                ]
                value_columns = [
                    column for (_key, column) in sql_values_tuple.iter_expressions()
                ]
                zipped_columns = list(zip(schema_columns, value_columns))
                fields = build_insert_assert_fields(zipped_columns, table_schema)
                returning = parsed_query.find(sqlglot.expressions.Returning)
                primary_key = None
                if returning:  # pragma: no branch
                    for field, value in zip(
                        returning.expressions, query["query_data"][0]
                    ):
                        field_schema = table_schema["fields"][field.name]
                        if field_schema["primary_key"]:  # pragma: no branch
                            primary_key = DjangoField(
                                field.this.name, value, field_schema
                            )
                            seen_mutations.setdefault(table_name, set()).add(
                                repr(value)
                            )
                if primary_key is None:  # pragma: no cover
                    continue
                assert_insert = AssertInsert.from_raw(
                    fields, query, table_schema, names, primary_key
                )
                asserts.append(assert_insert)
                imports.add(assert_insert.import_path)

    deduplicated = unique_everseen(inserts)
    sql_fixtures = sorted(deduplicated, key=make_table_sort_key(schema_data))
    for create in sql_fixtures:
        create.update_fields(names, schema_data)
    for assert_ in asserts:
        if isinstance(assert_, (AssertInsert, AssertSelect)):
            assert_.update_fields(names, schema_data)
    return sql_fixtures, imports, asserts


def get_request_headers(request):
    request_headers = {
        _format_header(header): value for header, value in request["headers"].items()
    }
    if "HTTP_COOKIE" in request_headers and request_headers["HTTP_COOKIE"] == "":
        del request_headers["HTTP_COOKIE"]
    if "CONTENT_LENGTH" in request_headers:
        del request_headers["CONTENT_LENGTH"]
    if "HTTP_HOST" in request_headers:
        del request_headers["HTTP_HOST"]
    if "HTTP_X_FORWARDED_FOR" in request_headers:
        del request_headers["HTTP_X_FORWARDED_FOR"]
    if "HTTP_X_FORWARDED_PROTO" in request_headers:
        del request_headers["HTTP_X_FORWARDED_PROTO"]

    if "CONTENT_TYPE" in request_headers:
        # This is a special header, which ends up influencing
        # how the django test client formats different parts of the
        # request. It's provided to the test client as a lowercased
        # argument
        request_headers["content_type"] = request_headers["CONTENT_TYPE"]
        del request_headers["CONTENT_TYPE"]
    return request_headers


def get_request_body(request, request_headers):
    request_body = request["body"]
    content_type = request_headers.get("content_type", "")
    if content_type == "application/x-www-form-urlencoded":
        # So: How can we now format the body so that it becomes more readable
        # We can totally cater to just this urlencoded version first...

        # TODO: Eventually need to be able to support multivaluedicts / query params
        # with multiple values per key
        # I couldn't quite get that to work.
        # Custom request body formatting is clearly useful also here again..
        urldecoded_body = parse_qsl(request_body)
        return f"urlencode({urldecoded_body})"
    elif "multipart/form-data" in content_type:
        request_headers.pop("content_type")
        if request["method"] == "POST":
            return str(request["post_data"])
        return ""
    else:
        return f'"{request_body}"'


def get_query_params(request):
    query_params = request["query_params"]
    if query_params:
        return f"{query_params},"
    return ""


def generate_from_trace_id(trace_id: str, test_class: str, test_name: str) -> str:
    config = load_config()
    wal_mode = config.get("wal_mode", True)
    db_path = setup_db(config)
    raw_data = load_trace_from_db(db_path, trace_id, wal_mode=wal_mode)
    data = json.loads(raw_data)
    frames = data["frames_of_interest"]

    served_request_frames = []
    current_served_request = None

    outbound_request_frames = []
    current_outbound_request = None

    sql_queries = []
    for frame in frames:
        if frame["type"] == "django_request":
            current_served_request = {"request": frame, "templates": []}
            served_request_frames.append(current_served_request)
        elif frame["type"] == "django_response":
            assert current_served_request is not None
            current_served_request["response"] = frame
            current_served_request = None
        elif frame["type"] == "django_template_start":
            assert current_served_request is not None
            current_served_request["templates"].append(frame["template"])
        elif frame["type"] == "outbound_http_request":
            if frame["subtype"] == "urllib3":
                # Only support requests from requests for now, to keep this simple
                continue
            assert current_outbound_request is None
            current_outbound_request = {"request": frame}
        elif frame["type"] == "outbound_http_response":
            if frame["subtype"] == "urllib3":
                continue
            assert current_outbound_request is not None
            current_outbound_request["response"] = frame
            outbound_request_frames.append(current_outbound_request)

            current_outbound_request = None
        elif frame["type"] == "end_sql_query":
            sql_queries.append(frame)

    if sql_queries:
        commit_sha = data["current_commit_sha"]
        if commit_sha == COMMIT_SHA:
            schema_data = get_schema()  # pragma: no cover
        else:
            schema_data = load_schema_for_commit_sha(db_path, commit_sha, wal_mode)
        sql_fixtures, imports, asserts = parse_sql_queries(sql_queries, schema_data)
    else:
        sql_fixtures = []
        imports = set()
        asserts = []

    # Figure out further heuristics here..

    # We need to figure out some sort of data model for
    # - Which data gets mutated, which data only gets selected
    # We can't assume that we need to do inserts for a select
    # that happens on a table, after it gets mutated.
    # So let's keep a record of the order of queries, what tables they happen on
    # and if they select or only mutate.
    # Then we can actually tell which tables get mutated and in which ways.

    # This will be useful in the extension too to figure out
    # what were the rows that were created. What were the updates
    # that were actually made.

    # And then in the tests, we can make assertions around certain updates having happened

    request = served_request_frames[0]["request"]
    response = served_request_frames[0]["response"]
    request_headers = get_request_headers(request)
    prettified_request_body = get_request_body(request, request_headers)
    query_params = get_query_params(request)
    request_timestamp = datetime.utcfromtimestamp(request["timestamp"]).isoformat(
        timespec="seconds"
    )

    try:
        from django import __version__ as django_version
    except ImportError:  # pragma: no cover
        django_version = ""

    template = env.get_template("django_request_test.py.j2")
    rendered = template.render(
        asserts=asserts,
        django_version=django_version,
        imports=sorted(imports),
        kolo_version=kolo_version,
        now=datetime.utcnow(),
        outbound_request_frames=outbound_request_frames,
        prettified_request_body=prettified_request_body,
        query_params=query_params,
        request=request,
        request_headers=request_headers,
        request_timestamp=request_timestamp,
        response=response,
        sql_fixtures=sql_fixtures,
        template_names=served_request_frames[0]["templates"],
        test_class=test_class,
        test_name=test_name,
        trace_id=trace_id,
    )
    return maybe_black(rendered)
