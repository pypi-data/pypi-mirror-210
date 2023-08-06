from __future__ import annotations
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from os import listdir, chmod
from time import time, perf_counter

import psycopg2
from opentelemetry import trace, context
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind
from psycopg2 import connection, InterfaceError
from psycopg2.extensions import ISOLATION_LEVEL_SERIALIZABLE, ISOLATION_LEVEL_REPEATABLE_READ
from psycopg2.pool import ThreadedConnectionPool

import leanit_mweb
from leanit_mweb.thread import AdvancedThreadPoolExecutor

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


from typing import TYPE_CHECKING, Iterable, Dict, Union

if TYPE_CHECKING:
    pass

local = threading.local()

def _parse_table_name(query: str) -> str:
    """
    This function uses the find method of strings to find the first and second occurrences of double quotes
    in the query. The table name is then extracted as the substring between these two positions.
    """
    start = query.find('"')
    if start == -1:
        return ""
    end = query.find('"', start + 1)
    if end == -1:
        return ""
    return query[start + 1:end]


def _initialize():
    thread_name = threading.current_thread().name
    logger.info(f"[{thread_name}] Initializing YugabyteDB connection pool")

    kwargs = dict(
        dbname=leanit_mweb.config['db']['dbname'],
        host=leanit_mweb.config['db']['host'],
        port=leanit_mweb.config['db']['port'],
        user=leanit_mweb.config['db']['user'],
        password=leanit_mweb.config['db']['password'],
        # load_balance='true',

        # Controls whether client-side TCP keepalives are used. The default value is 1, meaning on, but you can change
        # this to 0, meaning off, if keepalives are not wanted.
        keepalives=1,
        # Controls the number of seconds of inactivity after which TCP should send a keepalive message to the server.
        # A value of zero uses the system default.
        keepalives_idle=10,
        # Controls the number of seconds after which a TCP keepalive message that is not acknowledged by the server
        # should be retransmitted. A value of zero uses the system default.
        keepalives_interval=5,
        # Controls the number of TCP keepalives that can be lost before the client's connection to the server is
        # considered dead. A value of zero uses the system default.
        keepalives_count=2,
    )
    if 'sslmode' in leanit_mweb.config['db']:
        kwargs['sslmode'] = leanit_mweb.config['db']['sslmode']
    if 'sslcert' in leanit_mweb.config['db']:
        sslcert = leanit_mweb.config['db']['sslcert']
        if"BEGIN CERTIFICATE" in sslcert:
            # assume it's a certificate
            sslcert_path = f"/tmp/{kwargs['dbname']}-{thread_name}-sslcert.crt"
            with open(sslcert_path, "w") as f:
                f.write(sslcert.strip())
        else:
            # assume it's a file path
            sslcert_path = sslcert

        kwargs['sslcert'] = sslcert_path
    if 'sslkey' in leanit_mweb.config['db']:
        sslkey = leanit_mweb.config['db']['sslkey']
        if "PRIVATE KEY" in sslkey:
            # assume it's a private key
            sslkey_path = f"/tmp/{kwargs['dbname']}-{thread_name}-sslkey.key"
            with open(sslkey_path, "w") as f:
                chmod(sslkey_path, 0o600)
                f.write(sslkey.strip())
        else:
            # assume it's a file path
            sslkey_path = sslkey

        kwargs['sslkey'] = sslkey_path
    if 'sslrootcert' in leanit_mweb.config['db']:
        sslrootcert = leanit_mweb.config['db']['sslrootcert']
        if "BEGIN CERTIFICATE" in sslrootcert:
            # assume it's a certificate
            sslrootcert_path = f"/tmp/{kwargs['dbname']}-{thread_name}-sslrootcert.crt"
            with open(sslrootcert_path, "w") as f:
                f.write(sslrootcert.strip())

        else:
            # assume it's a file path
            sslrootcert_path = sslrootcert

        kwargs['sslrootcert'] = sslrootcert_path

    try:
        local.conn = psycopg2.connect(**kwargs)
        local.conn.set_isolation_level(ISOLATION_LEVEL_SERIALIZABLE)
        local.conn.autocommit = True
    except Exception as e:
        logger.error(f"[{threading.current_thread().name}] Error initializing YugabyteDB connection pool: {e}")
        raise e

class YugabytedbThreadPool(AdvancedThreadPoolExecutor):
    """
    Usage:
        db = YugabytedbThreadPool(
            min_workers=3,
            max_workers=3
        )

        # in async event loop
        result = await asyncio.get_event_loop().run_in_executor(db, db.submit_sql, "SELECT 1")
    """
    def __init__(self, *args, **kwargs):
        kwargs['initializer'] = _initialize
        kwargs['thread_name_prefix'] = 'yuga'
        super().__init__(*args, **kwargs)

    def execute(self, sql: str, vars: Union[Dict, Iterable]=None, tracing_context=None):
        """
        This function is executed in the main thread (e.g. in async event loop)

        :param sql: might contain %s placeholders (vars=Iterable) or %(name)s placeholders (vars=Dict)
        :param vars: Iterable or Dict
        :return:
        """
        f = self.submit(self.submit_sql, sql, vars, tracing_context)
        return f.result()

    def submit_sql(self, sql: str, vars: Union[Dict, Iterable]=None, tracing_context=None):
        """
        This function is executed in a thread

        :param sql: might contain %s placeholders (vars=Iterable) or %(name)s placeholders (vars=Dict)
        :param vars: Iterable or Dict
        :return:
        """
        # tracing
        if tracing_context:
            context.attach(tracing_context)

        start_time = perf_counter()

        sql_command = sql.split(maxsplit=1)[0].upper()

        while True:

            conn = local.conn # type: connection
            cursor = conn.cursor()

            # logger.debug(f"[{threading.current_thread().name}] Executing SQL: sql={sql}")
            try:
                with tracer.start_as_current_span(f"db.{sql_command} {_parse_table_name(sql)}", kind=SpanKind.INTERNAL) as span:  # type: trace.Span
                    span.set_attribute(SpanAttributes.DB_STATEMENT, sql)
                    span.set_attribute(SpanAttributes.THREAD_NAME, threading.current_thread().name)

                    cursor.execute(sql, vars)

                    result = None
                    if sql_command == 'SELECT':
                        result = cursor.fetchall()

                    # else:
                    #     with tracer.start_as_current_span("db.commit", kind=SpanKind.INTERNAL) as span:  # type: trace.Span
                    #         conn.commit()

                    # everything is fine, break out of the while loop
                    break
            except psycopg2.errors.SerializationFailure as e:
                error_message = " ".join([line.strip() for line in str(e).splitlines()])
                logger.error(f"[{threading.current_thread().name}] Error executing SQL: sql='{sql}' error={e.__class__.__name__} message='{error_message}'")
                try:
                    with tracer.start_as_current_span("db.rollback", kind=SpanKind.INTERNAL) as span:  # type: trace.Span
                        conn.rollback()
                except InterfaceError as e:
                    # connection already closed
                    logger.error(f"[{threading.current_thread().name}] {e.__class__.__name__}: {e}")
                    # reconnect
                    with tracer.start_as_current_span("db.connect", kind=SpanKind.INTERNAL) as span:  # type: trace.Span
                        _initialize()
                    # retry
                    continue

            except Exception as e:
                error_message = " ".join([line.strip() for line in str(e).splitlines()])
                logger.error(f"[{threading.current_thread().name}] Error executing SQL: sql='{sql}' error={e.__class__.__name__} message='{error_message}'")
                try:
                    with tracer.start_as_current_span("db.rollback", kind=SpanKind.INTERNAL) as span:  # type: trace.Span
                        conn.rollback()
                except InterfaceError as e:
                    # connection already closed
                    logger.error(f"[{threading.current_thread().name}] {e.__class__.__name__}: {e}")
                    # reconnect
                    with tracer.start_as_current_span("db.connect", kind=SpanKind.INTERNAL) as span:  # type: trace.Span
                        _initialize()
                    # retry
                    continue

                raise

        end_time = perf_counter()
        logger.debug(f"[{threading.current_thread().name}] Executing SQL: sql='{sql}' time={end_time - start_time:.3f}")

        return result

    def migrate(self, migration_dir: str, migrations_table_name: str = 'migrations'):
        # select the last 20 installed migrations
        sql = f"SELECT * FROM {migrations_table_name} ORDER BY id DESC LIMIT 20"
        try:
            result = self.execute(sql)
        except psycopg2.errors.UndefinedTable as e:
            self._create_migrations_table(migrations_table_name)
            result = self.execute(sql)

        already_applied_migration_ids = [r[0] for r in result]

        logger.debug(f"Last 20 migrations: {already_applied_migration_ids}")

        migration_files = sorted(listdir(migration_dir))
        for migration_file in migration_files:
            if not migration_file.endswith('.sql'):
                continue
            migration_id = migration_file.rsplit('.', maxsplit=1)[0]

            if migration_id in already_applied_migration_ids:
                continue

            logger.info(f"Applying migration {migration_id}")
            with open(f"{migration_dir}/{migration_file}") as f:
                sql = f.read()

            self.execute(sql)

            logger.info(f"Adding migration {migration_id} to {migrations_table_name}")
            sql = f"INSERT INTO {migrations_table_name} (id) VALUES ('{migration_id}')"
            self.execute(sql)


    def _create_migrations_table(self, migrations_table_name: str):
        sql = f"""
        CREATE TABLE {migrations_table_name} (
            id VARCHAR(255) PRIMARY KEY,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute(sql)
