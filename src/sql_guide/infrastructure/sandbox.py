"""PostgreSQL sandbox: one schema per attempt, then a full rollback."""

from collections.abc import Sequence
from urllib.parse import urlparse
from uuid import uuid4

import psycopg
from psycopg import sql

from sql_guide.domain.errors import SandboxQueryFailed, SandboxSetupFailed
from sql_guide.domain.sandbox import QueryResult

SANDBOX_DATABASE = "sql_guide_sandbox"
SANDBOX_ROLE = "sql_guide_sandbox"
_SANDBOX_PASSWORD = "sql_guide_sandbox"
_ROW_LIMIT = 500


def psycopg_url(url: str) -> str:
    """Convert a SQLAlchemy PostgreSQL URL into a psycopg URL.

    Args:
        url: URL that may use the ``postgresql+psycopg`` driver prefix.

    Returns:
        A URL psycopg can open.
    """
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


class PostgresSandbox:
    """Executes learner SQL as a role that cannot reach the application database."""

    def __init__(self, database_url: str, role: str = SANDBOX_ROLE) -> None:
        """Store the sandbox connection and the role used for learner SQL.

        Args:
            database_url: Connection string for the sandbox database.
            role: Login role assumed before the learner statement.
        """
        if not role.isidentifier():
            raise SandboxSetupFailed("Sandbox role name is not an identifier")
        self._url = psycopg_url(database_url)
        self._role = role

    async def execute(
        self,
        setup: Sequence[str],
        statement: str,
        *,
        probe: str | None = None,
    ) -> QueryResult:
        """Run setup and one statement, then roll the schema back.

        Args:
            setup: Trusted statements executed before the role switch.
            statement: Learner statement already accepted by the policy.
            probe: Optional statement whose rows are returned after ``statement``.

        Returns:
            Columns and rows from the learner statement, or from the probe.

        Raises:
            SandboxSetupFailed: Setup SQL or the sandbox connection failed.
            SandboxQueryFailed: The database rejected the learner statement.
        """
        schema = f"attempt_{uuid4().hex}"
        connection = await psycopg.AsyncConnection.connect(self._url)
        try:
            result = await self._run(connection, schema, setup, statement, probe)
        finally:
            await connection.rollback()
            await connection.close()
        return result

    async def _run(
        self,
        connection: psycopg.AsyncConnection,
        schema: str,
        setup: Sequence[str],
        statement: str,
        probe: str | None,
    ) -> QueryResult:
        await _owner(
            connection,
            sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)),
        )
        await _owner(
            connection,
            sql.SQL("SET LOCAL search_path TO {}, pg_catalog").format(
                sql.Identifier(schema)
            ),
        )
        await _owner(connection, "SET LOCAL statement_timeout = '2000ms'")
        await _owner(connection, "SET LOCAL lock_timeout = '1000ms'")
        for item in setup:
            await _setup(connection, item)
        await _owner(
            connection,
            sql.SQL("GRANT USAGE, CREATE ON SCHEMA {} TO {}").format(
                sql.Identifier(schema),
                sql.Identifier(self._role),
            ),
        )
        await _hand_schema_to_learner(connection, schema, self._role)
        await _owner(
            connection,
            sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(self._role)),
        )
        if probe is None:
            return await _learner(connection, statement)
        await _learner(connection, statement)
        return await _learner(connection, probe)


async def ensure_sandbox(admin_url: str) -> None:
    """Create the sandbox database and role when they are missing.

    The sandbox role can connect only to its own database. The application
    role keeps access. Existing volumes that skipped the init script are
    repaired here.

    Args:
        admin_url: Superuser URL for the application database.

    Raises:
        SandboxSetupFailed: A configured name is not a plain identifier.
    """
    owner, app_database = _url_names(admin_url)
    connection = await psycopg.AsyncConnection.connect(
        psycopg_url(admin_url),
        autocommit=True,
    )
    try:
        await _create_role(connection, owner)
        await _create_database(connection)
        await _separate_databases(connection, owner, app_database)
    finally:
        await connection.close()
    sandbox = await psycopg.AsyncConnection.connect(
        _database_url(admin_url, SANDBOX_DATABASE),
        autocommit=True,
    )
    try:
        await sandbox.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC")
    finally:
        await sandbox.close()


async def _create_role(connection: psycopg.AsyncConnection, owner: str) -> None:
    existing = await connection.execute(
        "SELECT 1 FROM pg_roles WHERE rolname = %s",
        (SANDBOX_ROLE,),
    )
    if await existing.fetchone() is None:
        await connection.execute(
            sql.SQL(
                "CREATE ROLE {} LOGIN PASSWORD {} "
                "NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT"
            ).format(sql.Identifier(SANDBOX_ROLE), sql.Literal(_SANDBOX_PASSWORD))
        )
    await connection.execute(
        sql.SQL("GRANT {} TO {}").format(
            sql.Identifier(SANDBOX_ROLE),
            sql.Identifier(owner),
        )
    )


async def _create_database(connection: psycopg.AsyncConnection) -> None:
    existing = await connection.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (SANDBOX_DATABASE,),
    )
    if await existing.fetchone() is None:
        await connection.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(SANDBOX_DATABASE))
        )


async def _separate_databases(
    connection: psycopg.AsyncConnection,
    owner: str,
    app_database: str,
) -> None:
    await connection.execute(
        sql.SQL("REVOKE CONNECT ON DATABASE {} FROM PUBLIC").format(
            sql.Identifier(app_database)
        )
    )
    await connection.execute(
        sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
            sql.Identifier(app_database),
            sql.Identifier(owner),
        )
    )
    await connection.execute(
        sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(
            sql.Identifier(SANDBOX_DATABASE)
        )
    )
    await connection.execute(
        sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
            sql.Identifier(SANDBOX_DATABASE),
            sql.Identifier(owner),
        )
    )
    await connection.execute(
        sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
            sql.Identifier(SANDBOX_DATABASE),
            sql.Identifier(SANDBOX_ROLE),
        )
    )


def _url_names(admin_url: str) -> tuple[str, str]:
    parsed = urlparse(psycopg_url(admin_url))
    owner = parsed.username or ""
    database = parsed.path.removeprefix("/")
    if not owner.isidentifier() or not database.isidentifier():
        raise SandboxSetupFailed("Sandbox admin URL is not usable")
    if not SANDBOX_DATABASE.isidentifier() or not SANDBOX_ROLE.isidentifier():
        raise SandboxSetupFailed("Sandbox name is not an identifier")
    return owner, database


def _database_url(admin_url: str, database: str) -> str:
    base = psycopg_url(admin_url)
    prefix, separator, _current = base.rpartition("/")
    if separator != "/":
        raise SandboxSetupFailed("Sandbox admin URL has no database name")
    return f"{prefix}/{database}"


async def _owner(
    connection: psycopg.AsyncConnection,
    statement: sql.Composed | str,
) -> None:
    try:
        await connection.execute(statement)
    except psycopg.Error as exc:
        raise SandboxSetupFailed(_primary(exc)) from exc


async def _hand_schema_to_learner(
    connection: psycopg.AsyncConnection,
    schema: str,
    role: str,
) -> None:
    """Give the sandbox role the tables of this attempt.

    Args:
        connection: Open transaction that still runs as the schema owner.
        schema: Attempt schema created for this statement.
        role: Login role that will run the learner statement.
    """
    cursor = await connection.execute(
        """
        SELECT c.relname
        FROM pg_class AS c
        JOIN pg_namespace AS n ON n.oid = c.relnamespace
        WHERE n.nspname = %s AND c.relkind = 'r'
        """,
        (schema,),
    )
    names = await cursor.fetchall()
    for (name,) in names:
        await _owner(
            connection,
            sql.SQL("ALTER TABLE {}.{} OWNER TO {}").format(
                sql.Identifier(schema),
                sql.Identifier(name),
                sql.Identifier(role),
            ),
        )


async def _setup(connection: psycopg.AsyncConnection, statement: str) -> None:
    try:
        await connection.execute(statement)
    except psycopg.Error as exc:
        raise SandboxSetupFailed(_primary(exc)) from exc


async def _learner(connection: psycopg.AsyncConnection, statement: str) -> QueryResult:
    try:
        cursor = await connection.execute(statement)
        description = cursor.description
        if description is None:
            return QueryResult((), ())
        fetched = await cursor.fetchmany(_ROW_LIMIT + 1)
    except psycopg.Error as exc:
        raise SandboxQueryFailed(_primary(exc)) from exc
    if len(fetched) > _ROW_LIMIT:
        raise SandboxQueryFailed("Result is too large")
    columns = tuple(column.name for column in description)
    rows = tuple(tuple(row) for row in fetched)
    return QueryResult(columns, rows)


def _primary(exc: psycopg.Error) -> str:
    primary = None if exc.diag is None else exc.diag.message_primary
    if primary is None or primary == "":
        return "The database rejected the statement"
    return primary[:200]
