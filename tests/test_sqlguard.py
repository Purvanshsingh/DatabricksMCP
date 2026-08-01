from __future__ import annotations

import pytest

from databricks_mcp.sqlguard import UnsafeSqlError, validate_read_only_sql

ALLOWED = [
    "SELECT 1",
    "select * from main.default.events where id > 10 limit 5",
    "WITH c AS (SELECT * FROM t) SELECT * FROM c",
    "SELECT a FROM t UNION SELECT b FROM u",
    "(SELECT 1)",
    "SHOW TABLES IN main.default",
    "SHOW CATALOGS",
    "DESCRIBE TABLE main.default.events",
    "DESC main.default.events",
    "EXPLAIN SELECT * FROM t",
    "EXPLAIN EXTENDED SELECT * FROM t",
]

DENIED = [
    "INSERT INTO t VALUES (1)",
    "UPDATE t SET x = 1",
    "DELETE FROM t",
    "MERGE INTO t USING s ON t.id = s.id WHEN MATCHED THEN UPDATE SET x = 1",
    "DROP TABLE t",
    "CREATE TABLE t (a int)",
    "ALTER TABLE t ADD COLUMN b int",
    "TRUNCATE TABLE t",
    "COPY INTO t FROM '/x'",
    "SET spark.sql.shuffle.partitions = 1",
    "USE CATALOG main",
    "GRANT SELECT ON t TO u",
    "REFRESH TABLE t",
    "OPTIMIZE t",
    "VACUUM t",
    # Injection / bypass attempts.
    "SELECT * FROM t; DROP TABLE t",
    "SELECT * FROM t; SELECT * FROM u",
    "EXPLAIN DROP TABLE t",
    "EXPLAIN INSERT INTO t VALUES (1)",
    # Not a statement.
    "",
    "   ",
    "this is not sql !!!",
]


@pytest.mark.parametrize("sql", ALLOWED)
def test_read_only_statements_are_allowed(sql: str) -> None:
    assert validate_read_only_sql(sql) == sql.strip()


@pytest.mark.parametrize("sql", DENIED)
def test_unsafe_statements_are_rejected(sql: str) -> None:
    with pytest.raises(UnsafeSqlError):
        validate_read_only_sql(sql)
