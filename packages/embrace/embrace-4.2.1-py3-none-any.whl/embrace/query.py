#  Copyright 2020 Oliver Cope
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from collections import namedtuple
from dataclasses import dataclass
from dataclasses import InitVar
from functools import partial
from itertools import chain
from itertools import islice
from itertools import zip_longest
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Union
from typing import Tuple
from typing import Set
from typing import TYPE_CHECKING
from pickle import dumps
from pickle import HIGHEST_PROTOCOL
import sys

from .parsing import compile_bind_parameters
from .parsing import split_statements
from .parsing import compile_includes
from . import exceptions

if TYPE_CHECKING:
    from embrace.module import Module

known_styles: Dict[type, str] = {}

_joinedload = namedtuple("_joinedload", "target attr source arity")
_marker = object()


class NullObjectType:
    pass


NullObject = NullObjectType()


def get_param_style(conn: Any) -> str:

    conncls = conn.__class__
    try:
        return known_styles[conncls]
    except KeyError:
        modname = conncls.__module__
        while modname:
            try:
                style = sys.modules[modname].paramstyle  # type: ignore
                known_styles[conncls] = style
                return style
            except AttributeError:
                if "." in modname:
                    modname = modname.rsplit(".", 1)[0]
                else:
                    break
    raise TypeError(f"Can't find paramstyle for connection {conn!r}")


class Query:

    name: Optional[str]
    source: Optional[str]
    lineno: Optional[int]
    result_type: str
    includes: List[str] = []
    includes_resolved = False
    get_row_mapper: Optional[Callable]

    def __init__(
        self,
        statements: Optional[Union[str, Sequence[str]]] = None,
        result_type: str = "many",
        source: Optional[str] = None,
        lineno: Optional[int] = None,
        name: Optional[str] = None,
    ):
        self.name = name
        self.result_map = None
        if isinstance(statements, str):
            statements = next(stmt for _, stmt in split_statements(statements))
        if statements is None:
            statements = []
        self.statements = statements
        self.source = source
        self.lineno = lineno
        self.result_type = result_type
        self._conn = None
        self.get_row_mapper = None

    def resolve_includes(self, module: "Module") -> bool:
        new_statements = []
        for stmt in self.statements:
            include_names, replace_includes = compile_includes(stmt)
            try:
                queries = [module.queries[n] for n in include_names]
            except KeyError:
                self.includes_resolved = False
                return False
            for q in queries:
                q.resolve_includes(module)

            new_statements.append(replace_includes(queries))
            self.includes = include_names
        self.statements = new_statements
        self.includes_resolved = True
        return True

    def copy(self) -> "Query":
        """
        Return a copy of the query
        """
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__ = self.__dict__.copy()
        return new

    def bind(self, conn) -> "Query":
        """
        Return a copy of the query bound to a database connection
        """
        bound = self.copy()
        bound._conn = conn
        return bound

    def returning(
        self,
        row_spec: Union["mapobject", Callable, Sequence[Union["mapobject", Callable]]],
        joins: Optional[Union[_joinedload, Sequence[_joinedload]]] = None,
        positional=False,
        key_columns: Optional[List[Tuple[str]]] = None,
        split_on=[],
    ) -> "Query":
        """
        Return a copy of the query with a changed result type
        """
        q = self.copy()
        if isinstance(joins, _joinedload):
            joins = [joins]

        row_spec = make_rowspec(row_spec, split_on or [], key_columns or [], positional)
        q.get_row_mapper = partial(make_row_mapper, row_spec, joins)
        return q

    def one(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="one", **kwargs)

    def first(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="first", **kwargs)

    def one_or_none(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="one_or_none", **kwargs)

    def many(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="many", **kwargs)

    def scalar(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="scalar", **kwargs)

    def affected(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="affected", **kwargs)

    def rowcount(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="affected", **kwargs)

    def column(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="column", **kwargs)

    def cursor(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="cursor", **kwargs)

    def resultset(self, conn=None, *, debug=False, **kwargs):
        return self(conn, debug=debug, _result="resultset", **kwargs)

    execute = resultset

    def __call__(
        self,
        conn=None,
        params=None,
        *,
        default=_marker,
        debug=False,
        _result=None,
        **kw,
    ):
        if params is None and isinstance(conn, dict):
            params = conn
            conn = None

        if conn is None:
            conn = self._conn
            if conn is None:
                raise TypeError("Query must be called with a connection argument")
        rt = _result or self.result_type

        paramstyle = get_param_style(conn)
        cursor = conn.cursor()
        if params:
            params.update(kw)
        else:
            params = kw

        prepared = [
            compile_bind_parameters(paramstyle, s, params) for s in self.statements
        ]
        for sqltext, bind_params in prepared:
            if debug:
                import textwrap

                print(
                    f"Executing \n{textwrap.indent(sqltext, '    ')} with {bind_params!r}",
                    file=sys.stderr,
                )
            try:
                cursor.execute(sqltext, bind_params)
            except BaseException:
                _handle_exception(conn, self.source, 1)

        if rt == "cursor":
            return cursor

        elif rt == "affected":
            return cursor.rowcount

        else:
            if self.get_row_mapper:
                row_mapper = self.get_row_mapper(cursor.description)
            else:
                row_mapper = None
            resultset = ResultSet(cursor, row_mapper)
            if rt == "resultset":
                return resultset
            try:
                fn = getattr(resultset, rt)
            except AttributeError:
                raise ValueError(f"Unsupported result type: {rt}")
            if rt == "scalar":
                return fn(default=default)
            else:
                return fn()


def _handle_exception(conn, filename, lineno):
    """
    We have an exception of unknown type, probably raised
    from the dbapi module
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_type and exc_value:
        classes = [exc_type]
        while classes:
            cls = classes.pop()
            clsname = cls.__name__

            if clsname in exceptions.pep_249_exception_names:
                newexc = exceptions.pep_249_exception_names[clsname]()
                newexc.args = getattr(exc_value, "args", tuple())
                newexc = newexc.with_traceback(exc_tb)
                if filename:
                    newlines = "\n" * (lineno - 1)
                    exec(
                        compile(
                            f"{newlines}raise newexc from exc_value", filename, "exec"
                        ),
                        {
                            "__name__": filename,
                            "__file__": filename,
                            "newexc": newexc,
                            "exc_value": exc_value,
                        },
                        {},
                    )
                else:
                    raise newexc from exc_value
            classes.extend(getattr(cls, "__bases__", []))

        raise exc_value.with_traceback(exc_tb) from exc_value


def get_split_points(
    row_spec: Sequence["mapobject"], column_names: List[str]
) -> List[slice]:
    pos = 0
    result = []
    for curr_mo, next_mo in zip_longest(row_spec, row_spec[1:]):
        if curr_mo.column_count:
            pos_ = pos + curr_mo.column_count
        elif next_mo:
            try:
                pos_ = column_names.index(next_mo.split, pos + 1)
            except ValueError as e:
                raise ValueError(
                    f"split_on column {next_mo.split!r} for {next_mo} not found: "
                    f" (columns remaining are {column_names[pos + 1:]})"
                ) from e
        else:
            pos_ = len(column_names)
        result.append(slice(pos, pos_))
        pos = pos_
    return result


def make_row_mapper(row_spec: Sequence["mapobject"], joins, description):

    row_spec = list(row_spec)
    is_multi = len(row_spec) > 1
    column_names: List[str] = [d[0] for d in description]
    split_points = []

    if is_multi:
        split_points = get_split_points(row_spec, column_names)
        mapped_column_names = [tuple(column_names[s]) for s in split_points]
    else:
        mapped_column_names = [tuple(column_names)]

    def _maprows(grouper, maker, rows):
        if not is_multi:
            object_rows = rows
        else:
            object_rows = ([row[s] for s in split_points] for row in rows)
        if is_multi:
            if grouper:
                return grouper(object_rows)
            else:
                return (tuple(map(maker, r)) for r in object_rows)
        else:
            return map(maker, object_rows)

    if joins:
        if not is_multi:
            raise TypeError(
                "joins may only be set when there are multiple return types"
            )
        maker: Optional[Callable] = None
        grouper: Optional[Callable] = partial(
            group_by_and_join, mapped_column_names, row_spec, joins
        )

    else:
        maker = make_object_maker(mapped_column_names, row_spec)
        grouper = None

    return partial(_maprows, grouper, maker)


def group_by_and_join(
    mapped_column_names: List[Tuple[str, ...]],
    row_spec,
    join_spec,
    object_rows: Iterable[List[Tuple]],
    _marker=object(),
    key_columns: Optional[List[Tuple[str]]] = None,
):
    make_object = make_object_maker(mapped_column_names, row_spec)
    join_spec = [_joinedload(*i) if isinstance(i, tuple) else i for i in join_spec]
    indexed_joins = translate_to_column_indexes(row_spec, join_spec)
    join_source_columns = {s_idx for _, _, s_idx, _, _ in indexed_joins}

    last = [_marker] * len(row_spec)

    # Mapping of <column group index>: <currently loaded object>
    cur: Dict[int, Any] = {}

    # List of column group indexes without backlinks: these are the top-level
    # objects we want to return
    return_columns = [n for n in range(len(row_spec)) if n not in join_source_columns]
    single_column = len(return_columns) == 1
    items = None

    multi_join_targets = [
        t_idx for t_idx, _, _, arity, _ in indexed_joins if arity == "*"
    ]
    seen: Set[Tuple[int, int]] = set()
    for irow, items in enumerate(object_rows):

        # When all columns change, emit a new object row (or single item)
        if irow > 0 and all(items[ix] != last[ix] for ix in multi_join_targets):
            if single_column:
                yield cur[0]
            else:
                yield tuple(cur[ix] for ix in return_columns)
            seen.clear()

        # Create objects from column data
        for column_index, item in enumerate(items):
            if column_index in join_source_columns:
                if all(v is None for v in item):
                    cur[column_index] = make_object(NullObject)
                    continue
            ob = make_object(item)
            cur[column_index] = ob

        # Populate joins
        for t_idx, attr, s_idx, arity, join_as_dict in indexed_joins:
            ob = cur[s_idx]
            ob_key = (s_idx, id(ob))
            if ob_key in seen:
                continue

            dest = cur[t_idx]
            if dest is None:
                continue
            if arity == "*":
                if join_as_dict:
                    if attr in dest:
                        attrib = dest[attr]
                    else:
                        attrib = _marker
                else:
                    attrib = getattr(dest, attr, _marker)
                if attrib is _marker:
                    attrib = []
                    if join_as_dict:
                        dest[attr] = attrib
                    else:
                        setattr(dest, attr, attrib)
                if ob is not None:
                    attrib.append(ob)
            else:
                if join_as_dict:
                    dest[attr] = ob
                else:
                    setattr(dest, attr, ob)
            seen.add(ob_key)

        last = items

    if items:
        if single_column:
            yield cur[0]
        else:
            rv: List[Any] = []
            append = rv.append
            for ix in return_columns:
                if ix in cur:
                    append(cur[ix])
                else:
                    append(make_object(items[ix]))
            yield tuple(rv)


def one_to_one(target, attr, source):
    return _joinedload(target, attr, source, "1")


def one_to_many(target, attr, source):
    return _joinedload(target, attr, source, "*")


def translate_to_column_indexes(
    row_spec, join_spec: List[_joinedload]
) -> Sequence[Tuple[int, str, int, str, bool]]:
    row_spec_indexes = {c.label: ix for ix, c in enumerate(row_spec)}

    def map_column(col: Any) -> int:
        if isinstance(col, int):
            return col
        return row_spec_indexes[col]

    result = []
    for j in join_spec:
        t_col = map_column(j.target)
        s_col = map_column(j.source)
        if t_col >= len(row_spec):
            raise ValueError(
                f"Target index {t_col} in join {j} exceeds number of mapped objects"
            )
        if s_col >= len(row_spec):
            raise ValueError(
                f"Source index {s_col} in join {j} exceeds number of mapped objects"
            )
        result.append((t_col, j.attr, s_col, j.arity, row_spec[t_col].join_as_dict))
    return result


def make_object_maker(
    mapped_column_names: List[Tuple[str, ...]],
    row_spec: List[Any],
) -> Callable[[Union[NullObjectType, Tuple]], Any]:
    """
    Return a function that constructs the target type from a group of columns.
    The returned function will cache objects (the same input returns the
    same object) so that object identity may be relied on within the scope of a
    single query.
    """

    key_column_positions: List[List[int]] = []
    row_spec_cols = list(zip(row_spec, mapped_column_names))
    for mo, item_column_names in row_spec_cols:
        key_column_positions.append([])
        for c in mo.key_columns:
            try:
                key_column_positions[-1].append(item_column_names.index(c))
            except ValueError as e:
                import pprint

                mapped_columns_dump = {m.mapped: c for m, c in row_spec_cols}
                raise ValueError(
                    f"{c!r} specified in key_columns does not exist "
                    f"in the returned columns for {mo.mapped!r}. \n"
                    f"Mapped columns are: \n{pprint.pformat(mapped_columns_dump)}"
                ) from e

    def _object_maker():
        object_cache: Dict[Any, Any] = {}
        ob = None
        itemcount = len(row_spec)

        # When loading multiple objects, ensure that proximate items loaded
        # with identical values map to the same object. This makes it possible
        # for joined loads to do the right thing, even if key_columns is not
        # set.
        row_cache: Dict[Union[Sequence[Any], Tuple[int, Any]], Any] = {}
        use_row_cache = len(row_spec) > 1
        mapping_items = [(m.mapped, m.key_columns, m.positional) for m in row_spec]

        i = -1
        rows_since_cache_flush = 0
        cache_hit_this_row = False
        cache_as_pickle_cols = {ix: False for ix in range(itemcount)}
        pickle = partial(dumps, protocol=HIGHEST_PROTOCOL)

        while True:
            data = yield ob
            i = (i + 1) % itemcount
            cache_as_pickle = cache_as_pickle_cols[i]

            # Clear the row_cache once we find a full row with no cache hits.
            if i == 0 and row_cache and not cache_hit_this_row:
                cache_hit_this_row = False
                if rows_since_cache_flush < 2:
                    rows_since_cache_flush += 1
                else:
                    row_cache.clear()
                    rows_since_cache_flush = 0

            if data is NullObject:
                ob = None
                continue

            mapped, key_columns, positional = mapping_items[i]
            if key_columns:
                key = (i, tuple(data[x] for x in key_column_positions[i]))
                if key in object_cache:
                    cache_hit_this_row = True
                    ob = object_cache[key]
                else:
                    ob = object_cache[key] = (
                        mapped(*data)
                        if positional
                        else mapped(**dict(zip(mapped_column_names[i], data)))
                    )
            elif use_row_cache:
                cache_key = pickle((i, data)) if cache_as_pickle else (i, data)
                try:
                    cache_hit = cache_key in row_cache
                except TypeError:
                    if cache_as_pickle:
                        raise
                    # data may contain unhashable types (eg postgresql ARRAY
                    # types), in which case a TypeError is thrown. Work around
                    # this by allowing keys for this column to be pickled.
                    cache_as_pickle_cols[i] = cache_as_pickle = True
                    cache_key = pickle(cache_key)
                    cache_hit = cache_key in row_cache

                if cache_hit:
                    cache_hit_this_row = True
                    ob = row_cache[cache_key]
                else:
                    ob = (
                        mapped(*data)
                        if positional
                        else mapped(**dict(zip(mapped_column_names[i], data)))
                    )
                    row_cache[cache_key] = ob
            else:
                ob = (
                    mapped(*data)
                    if positional
                    else mapped(**dict(zip(mapped_column_names[i], data)))
                )

    func = _object_maker()
    next(func)
    return func.send


def make_rowspec(
    row_spec: Union["mapobject", Callable, Sequence[Union["mapobject", Callable]]],
    split_on: Sequence[str],
    key_columns: Sequence[Tuple[str]],
    positional: bool,
) -> Sequence["mapobject"]:

    if not isinstance(row_spec, Sequence):
        row_spec = (row_spec,)

    if split_on and any(isinstance(i, mapobject) for i in row_spec):
        raise TypeError("Cannot combine mapobject with split_on")

    result = []
    for ix, item in enumerate(row_spec):

        if not isinstance(item, mapobject):
            item = mapobject(item)

            # Enable backwards compatibility for positional, split_on, key_columns
            item.positional = positional
            if 0 < ix < len(split_on) - 1:
                item.split = split_on[ix - 1]
            if ix < len(key_columns):
                item.key_columns = key_columns[ix]

        result.append(item)
    return result


@dataclass
class mapobject:

    mapped: Callable
    key: InitVar[Union[str, Sequence[str]]] = tuple()
    split: str = "id"
    positional: bool = False
    column_count: Optional[int] = None
    join_as_dict: bool = False
    key_columns: Sequence[str] = tuple()
    label: Any = None

    @staticmethod
    def passthrough_mapped(x):
        return x

    def __post_init__(self, key):
        if isinstance(key, str):
            self.key_columns = (key,)
        else:
            self.key_columns = tuple(key)
        if self.label is None:
            self.label = self.mapped

    @classmethod
    def dict(cls, mapped=dict, *args, **kwargs):
        kwargs["join_as_dict"] = True
        return cls(mapped, *args, **kwargs)

    @classmethod
    def passthrough(cls, mapped="ignore", *args, **kwargs):
        kwargs["column_count"] = 1
        kwargs["positional"] = True
        return cls(cls.passthrough_mapped, **kwargs)

    @classmethod
    def namedtuple(cls, *args, **kwargs):
        _nt = None

        def dynamicnamedtuple(**kwargs):
            nonlocal _nt
            if _nt is None:
                _nt = namedtuple(  # type: ignore
                    f"mapobject_namedtuple_{id(dynamicnamedtuple)}", tuple(kwargs)
                )
            return _nt(**kwargs)  # type: ignore

        return cls(mapped=dynamicnamedtuple, **kwargs)


class ResultSet:

    __slots__ = ["cursor", "row_mapper"]

    def __init__(self, cursor, row_mapper):
        self.cursor = cursor
        self.row_mapper = row_mapper

    def __iter__(self):
        return self.many()

    def one(self):
        row = self.cursor.fetchone()
        if row is None:
            raise exceptions.NoResultFound()
        if self.cursor.fetchone() is not None:
            raise exceptions.MultipleResultsFound()
        if self.row_mapper:
            return next(self.row_mapper([row]))
        return row

    def first(self):
        row = self.cursor.fetchone()
        if row and self.row_mapper:
            return next(self.row_mapper([row]))
        return row

    def many(self, method: str = "auto", limit_rows: int = 0, limit_mapped: int = 0):
        """
        Return an iterator over the ResultSet.

        :param method: The cursor method used to fetch results.
                       Must be one of 'auto', 'fetchone', 'fetchmany', or 'fetchall'
                       (default: 'auto'). If ``auto`` is selected, ``fetchall``
                       will be used unless a limit is given, in which case
                       ``fetchmany`` will be used.
        :param limit_rows: Maximum number of rows to fetch.
                           This is based on the number of rows returned. If you
                           are using joins to compose these into objects, this
                           may not correspond with the number of objects yielded.
        :param limit_mapped: Maximum number of mapped objects to generate.
        """
        if method == "auto":
            # Shortcut the default case
            if not limit_mapped and not limit_rows:
                if self.row_mapper:
                    return self.row_mapper(self.cursor.fetchall())
                else:
                    return iter(self.cursor.fetchall())
            method = "fetchmany"

        row_getter = getattr(self, f"many_rows_{method}")
        if self.row_mapper:
            if limit_mapped:

                def limited_rowmapper():

                    count = 0
                    rowcount = 0

                    if method == "fetchmany":

                        def _row_getter():
                            while True:
                                if count == 0:
                                    limit = self.cursor.arraysize
                                else:
                                    remaining = limit_mapped - count
                                    limit = int(((remaining + 1) * rowcount) / count)

                                ix = 0
                                for row in row_getter(limit=limit):
                                    yield row
                                    ix += 1
                                if ix == 0:
                                    return

                        rows = _row_getter()
                    else:
                        rows = row_getter()

                    for ix, mapped in enumerate(self.row_mapper(rows), 1):
                        yield mapped
                        if ix >= limit_mapped:
                            break

                return limited_rowmapper()
            else:
                return self.row_mapper(row_getter(limit=limit_rows))
        else:
            return row_getter(limit=(limit_rows or limit_mapped))

    def many_rows_fetchone(self, limit: int = 0):
        if limit:
            return islice(iter(self.cursor.fetchone, None), limit)
        else:
            return iter(self.cursor.fetchone, None)

    def many_rows_fetchmany(self, limit: int = 0):
        if limit:
            arraysize = self.cursor.arraysize
            fullbatches, remainder = divmod(limit, arraysize)
            for ix in range(fullbatches):
                yield from self.cursor.fetchmany(arraysize)
            if remainder:
                yield from self.cursor.fetchmany(remainder)
        else:
            for batch in iter(self.cursor.fetchmany, []):
                yield from batch

    def many_rows_fetchall(self, limit: int = 0):
        if limit:
            return iter(self.cursor.fetchall()[:limit])
        else:
            return iter(self.cursor.fetchall())

    def one_or_none(self):
        row = self.cursor.fetchone()
        if self.cursor.fetchone() is not None:
            raise exceptions.MultipleResultsFound()
        if row and self.row_mapper:
            return next(self.row_mapper([row]))
        return row

    def scalar(self, default=_marker):
        row = self.cursor.fetchone()
        if row is None:
            if default is not _marker:
                return default
            raise exceptions.NoResultFound()
        if isinstance(row, Mapping):
            value = next(iter(row.values()))
        elif isinstance(row, Sequence):
            value = row[0]
        else:
            raise TypeError(f"Can't find first column for row of type {type(row)}")
        if self.row_mapper:
            return next(self.row_mapper([value]))
        return value

    def column(self):
        first = self.cursor.fetchone()
        if first:
            if isinstance(first, Mapping):
                key = next(iter(first))
            elif isinstance(first, Sequence):
                key = 0
            else:
                raise TypeError(
                    f"Can't find first column for row of type {type(first)}"
                )
            rows = (
                row[key] for row in chain([first], iter(self.cursor.fetchone, None))
            )
            if self.row_mapper:
                return self.row_mapper(rows)
            return rows
        return iter([])

    def affected(self):
        return self.cursor.rowcount

    @property
    def rowcount(self):
        return self.cursor.rowcount
