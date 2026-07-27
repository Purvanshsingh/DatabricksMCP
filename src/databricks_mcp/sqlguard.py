"""Read-only SQL validation through sqlglot AST inspection.

The guard parses a statement with the Databricks dialect and permits only
queries that cannot change state: ``SELECT`` (including set operations and
CTEs), ``DESCRIBE``, ``SHOW``, and ``EXPLAIN`` wrapping a permitted query.
Everything else — DML, DDL, session/administrative commands, and multiple
statements — is rejected. Rejection is the default: anything that does not
parse, or that the guard does not positively recognize as read-only, is denied.
"""

from __future__ import annotations

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

DIALECT = "databricks"

# Query-shaped roots that are inherently read-only.
_ALLOWED_QUERY_TYPES: tuple[type[exp.Expression], ...] = (
    exp.Select,
    exp.Union,
    exp.Intersect,
    exp.Except,
    exp.Subquery,
    exp.Describe,
)

# State-changing or privileged nodes rejected anywhere in the tree.
_FORBIDDEN_TYPES: tuple[type[exp.Expression], ...] = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Merge,
    exp.Create,
    exp.Drop,
    exp.Alter,
    exp.TruncateTable,
    exp.Copy,
    exp.Set,
    exp.Use,
    exp.Grant,
    exp.Refresh,
)

# Modifiers that may follow EXPLAIN before the wrapped query.
_EXPLAIN_MODIFIERS = frozenset({"EXTENDED", "FORMATTED", "CODEGEN", "COST", "LOGICAL"})
_MAX_EXPLAIN_DEPTH = 2


class UnsafeSqlError(ValueError):
    """Raised when a statement is not a permitted read-only query."""


def validate_read_only_sql(sql: str) -> str:
    """Return the trimmed statement if it is read-only; raise otherwise."""
    text = sql.strip()
    if not text:
        raise UnsafeSqlError("empty SQL statement")
    statements = _parse(text)
    if len(statements) > 1:
        raise UnsafeSqlError("multiple SQL statements are not allowed")
    _validate_statement(statements[0], depth=0)
    return text


def _parse(text: str) -> list[exp.Expression]:
    try:
        parsed = sqlglot.parse(text, read=DIALECT)
    except ParseError as error:
        raise UnsafeSqlError(f"could not parse SQL: {error}") from error
    statements = [statement for statement in parsed if statement is not None]
    if not statements:
        raise UnsafeSqlError("no SQL statement found")
    return statements


def _validate_statement(node: exp.Expression, *, depth: int) -> None:
    if isinstance(node, exp.Command):
        _validate_command(node, depth=depth)
        return
    if isinstance(node, _ALLOWED_QUERY_TYPES):
        forbidden = next(node.find_all(*_FORBIDDEN_TYPES), None)
        if forbidden is not None:
            raise UnsafeSqlError(f"'{forbidden.key.upper()}' is not permitted in read-only SQL")
        if next(node.find_all(exp.Command), None) is not None:
            raise UnsafeSqlError("nested non-query command is not permitted")
        return
    raise UnsafeSqlError(f"statement type '{node.key.upper()}' is not read-only")


def _validate_command(node: exp.Command, *, depth: int) -> None:
    keyword = str(node.this or "").upper()
    if keyword == "SHOW":
        return
    if keyword == "EXPLAIN":
        if depth >= _MAX_EXPLAIN_DEPTH:
            raise UnsafeSqlError("EXPLAIN is nested too deeply")
        inner = _explain_target(node)
        target = _parse(inner)
        if len(target) != 1:
            raise UnsafeSqlError("EXPLAIN must wrap exactly one query")
        _validate_statement(target[0], depth=depth + 1)
        return
    raise UnsafeSqlError(f"command '{keyword}' is not read-only")


def _explain_target(node: exp.Command) -> str:
    expression = node.args.get("expression")
    remainder = str(expression.this) if isinstance(expression, exp.Literal) else ""
    tokens = remainder.split()
    while tokens and tokens[0].upper() in _EXPLAIN_MODIFIERS:
        tokens = tokens[1:]
    inner = " ".join(tokens)
    if not inner:
        raise UnsafeSqlError("EXPLAIN requires a query")
    return inner
