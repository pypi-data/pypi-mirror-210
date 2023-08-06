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

import re
from itertools import count
from functools import partial
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Callable
from typing import List
from typing import Mapping
from typing import Union
from typing import Tuple
from typing import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from embrace.query import Query

import sqlparse

BindParams = Union[Tuple, Mapping]
Metadata = Dict[str, Union[str, int]]
Tokens = List[Tuple]

DEFAULT_RESULT_TYPE = "resultset"

result_types = [
    ("first", ["first"]),
    ("one", ["one", "1"]),
    ("many", ["many", "*"]),
    ("affected", ["affected", "n"]),
    ("exactlyone", ["exactly-one", "=1"]),
    ("one_or_none", ["one-or-none", "?"]),
    ("cursor", ["cursor", "raw"]),
    ("scalar", ["scalar"]),
    ("column", ["column"]),
    ("resultset", ["resultset"]),
]

result_type_pattern = rf"""
    :(?:
        {"|".join(
            f"(?P<{name}>{'|'.join(re.escape(t) for t in toks)})"
            for name, toks in result_types
        )}
    )
"""
name_pattern = re.compile(rf":name\s+(?P<name>\w+)(?:\s+{result_type_pattern})?$", re.X)
result_pattern = re.compile(rf":result\s+{result_type_pattern}$", re.X)
include_pattern = re.compile(r":include:([a-zA-Z_]\w*)")
param_pattern = re.compile(
    r"""
    # Don't match if preceded by backslash (an escape) or ':' (an SQL cast,
    # eg '::INT')
    (?<![:\\])

    # Optional parameter type
    (?:
        :(?P<param_type>
            value|v|value\*|v\*|tuple|t|tuple\*|t\*|identifier|i|raw|r
        )
    )?

    # An identifier
    :(?P<param>[a-zA-Z_]\w*)

    # followed by a non-word char, or end of string
    (?=\W|$)
    """,
    re.X,
)


def parse_comment_metadata(s: str) -> Dict:

    lines = (re.sub(r"^\s*--", "", line).strip() for line in s.split("\n"))
    patterns = [name_pattern, result_pattern]
    result = {}
    for line in lines:
        for p in patterns:
            mo = p.match(line)
            if mo:
                for k, v in mo.groupdict().items():
                    if v is not None:
                        result[k] = v

    if result:
        return {
            "name": result.get("name", None),
            "result": next(
                (rt for rt in [name for name, _ in result_types] if rt in result),
                DEFAULT_RESULT_TYPE,
            ),
        }

    return {}


def quote_ident_ansi(s):
    s = str(s)
    if "\x00" in s:
        raise ValueError(
            "Quoted identifiers can contain any character, "
            "except the character with code zero"
        )
    return f'''"{s.replace('"', '""')}"'''


def compile_includes(
    statement: str,
) -> Tuple[List[str], Callable[[Sequence["Query"]], str]]:
    """
    Parse a statement str, looking for ':include:<name>' patterns. Return the
    list of include names found, and a function that will accept the named
    queries in order and return a modified statement string.
    """

    # Will be [<stmt>, <include_name>, <stmt>, <include_name>, … <stmt>]
    splits = include_pattern.split(statement)

    # List of matched include names
    names = splits[1::2]

    def strip_semicolon(stmt: str) -> str:
        return stmt.rstrip().rstrip(";")

    def replace_includes(includes: Sequence["Query"]) -> str:
        iterincludes = iter(includes)
        return "".join(
            s
            if ix % 2 == 0
            else ";".join(map(strip_semicolon, next(iterincludes).statements))
            for ix, s in enumerate(splits)
        )

    return names, replace_includes


def compile_bind_parameters(
    target_style: str, sql: str, bind_parameters: Mapping
) -> Tuple[str, BindParams]:
    """
    :param target_style: A DBAPI paramstyle value (eg 'qmark', 'format', etc)
    :param sql: An SQL str
    :bind_parameters: A dict of bind parameters for the query

    :return: tuple of `(sql, bind_parameters)`. ``sql`` will be rewritten with
             the target paramstyle; ``bind_parameters`` will be a tuple or
             dict as required.
    :raises: TypeError, if the bind_parameters do not match the query
    """

    is_positional, param_gen = _param_styles[target_style]

    if target_style[-6:] == "format":
        sql = sql.replace("%", "%%")
    if is_positional:
        positional_params: List[Any] = []
    else:
        dict_params: Dict[str, Any] = {}

    transformed_sql = param_pattern.sub(
        partial(
            replace_placeholder,
            (positional_params if is_positional else dict_params),
            param_gen,
            count(1),
            bind_parameters,
        ),
        sql,
    )
    if is_positional:
        return transformed_sql, tuple(positional_params)
    else:
        return transformed_sql, dict_params


def split_statements(sql: str) -> Iterable[Tuple[Dict, List[str]]]:
    """
    Split an sql string into multiple queries
    """
    sqlchunks = sqlparse.split(sql)
    positions = []
    offset = 0
    for s in sqlchunks:
        offset = sql.index(s, offset)
        positions.append(offset)

    statements = (
        (pos, s) for pos, s in zip(positions, sqlparse.parse(sql)) if str(s).strip()
    )
    current: Tuple[Metadata, List[str]] = ({}, [])

    def starts_new_statement(metadata: Metadata) -> bool:
        return bool(metadata.get("name") or metadata.get("result"))

    def parse_tokens(tokens: Tokens) -> Tuple[Metadata, Tokens]:
        """
        Parse out any metadata from a list of sqlparse tokens
        Return a metadata dict and a new list of tokens with metadata removed
        """
        new_tokens = []
        metadata: Metadata = {}
        for token in statement.tokens:
            if isinstance(token, sqlparse.sql.Comment):
                metadata.update(parse_comment_metadata(str(token)))
            else:
                new_tokens.append(token)
        return metadata, new_tokens

    for pos, statement in statements:
        metadata, tokens = parse_tokens(statement.tokens)
        metadata["lineno"] = sql[:pos].count("\n")
        statement.tokens[:] = tokens

        if starts_new_statement(metadata):
            if current != ({}, []):
                yield current
            current = metadata, [str(statement)]

        else:
            current[0].update(metadata)
            current[1].append(str(statement))

    yield current


def replace_placeholder(
    params: Union[Dict[str, Any], List[Any]],
    param_gen,
    placeholder_counter,
    bind_parameters,
    match,
):
    group = match.groupdict().get
    pt = group("param_type")
    p = group("param")
    if pt in {None, "value", "v"}:
        if isinstance(params, list):
            params.append(bind_parameters[p])
        else:
            params[p] = bind_parameters[p]
        return param_gen(p, next(placeholder_counter))  # type: ignore
    elif pt in {"raw", "r"}:
        return str(bind_parameters[p])
    elif pt in {"identifier", "i"}:
        return quote_ident_ansi(bind_parameters[p])
    elif pt in {"value*", "v*", "tuple", "t"}:
        placeholder = make_sequence_placeholder(
            params, param_gen, placeholder_counter, list(bind_parameters[p])
        )
        if pt in {"tuple", "t"}:
            return f"({placeholder})"
        return placeholder
    elif pt in {"tuple*", "t*"}:
        return ", ".join(
            f"({make_sequence_placeholder(params, param_gen, placeholder_counter, list(items))})"
            for items in bind_parameters[p]
        )
    else:
        raise ValueError(f"Unsupported param_type {pt}")


def make_sequence_placeholder(
    params,
    param_gen,
    placeholder_counter,
    items: List,
) -> str:
    names = [f"_{ix}" for ix in range(1, len(items) + 1)]
    if isinstance(params, list):
        params.extend(items)
    else:
        params.update(zip(names, items))
    return ", ".join(param_gen(n, next(placeholder_counter)) for n in names)  # type: ignore


_param_styles = {
    "qmark": (True, lambda name, c: "?"),
    "numeric": (True, lambda name, c: f":{c}"),
    "format": (True, lambda name, c: "%s"),
    "pyformat": (False, lambda name, c: f"%({name})s"),
    "named": (False, lambda name, c: f":{name}"),
}
