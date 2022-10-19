from typing import Any, Callable, Dict, Optional, Union

from apscheduler.jobstores.memory import MemoryJobStore as MemoryJobStore  # noqa
from apscheduler.jobstores.mongodb import (
    MongoDBJobStore as APSchedulerMongoDBJobStore,
)  # noqa
from apscheduler.jobstores.redis import (
    RedisJobStore as APSchedulerRedisJobStore,
)  # noqa
from apscheduler.jobstores.rethinkdb import (
    RethinkDBJobStore as APSchedulerRethinkDBJobStore,
)  # noqa
from apscheduler.jobstores.sqlalchemy import (
    SQLAlchemyJobStore as APSchedulerSQLAlchemyJobStore,
)  # noqa
from apscheduler.jobstores.zookeeper import (
    ZooKeeperJobStore as APSchedulerZooKeeperJobStore,
)  # noqa

from esmerald.exceptions import ImproperlyConfigured
from esmerald.utils.helpers import is_class_and_subclass

try:
    from pymongo.mongo_client import MongoClient
except ImportError:
    MongoClient = Any

try:
    from rethinkdb.net import Connection
except ImportError:
    Connection = Any

try:
    from sqlalchemy.engine import Engine
    from sqlalchemy.schema import MetaData
except ImportError:
    Engine = Any
    MetaData = Any

try:
    from kazoo.client import KazooClient
except ImportError:
    KazooClient = Any

DATABASE = "apscheduler"
COLLECTION = "jobs"
TABLE = "jobs"
DATABASE_NUMBER = 0
JOBS_KEY = "apscheduler.jobs"
SQLALCHEMY_TABLE_NAME = "apscheduler_jobs"
RUN_TIMES_KEY = "apscheduler.run_times"
KAZOO_PATH = "/apscheduler"


class MongoDBJobStore(APSchedulerMongoDBJobStore):
    """
    Stores jobs in a MongoDB database. Any leftover keyword arguments are directly passed to
    pymongo's `MongoClient
    <http://api.mongodb.org/python/current/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient>`_.

    Plugin alias: `mongodb`.

    Args:
        database: database name to store jobs in.
        collection: collection string to store the jobs in.
        client: An instance of [pymongo.mongo_client.MongoClient] instance to use instead of
            providing conne:ction arguments.
        pickle_protocol: pickle protocol level (int) to use (for serialization), defaults to thehighest available (5).
    """

    def __init__(
        self,
        database: str = DATABASE,
        collection: str = COLLECTION,
        client: Optional[Union[Callable[[], Any], MongoClient]] = None,
        pickle_protocol: int = ...,
        **connect_args
    ):

        try:
            import pymongo  # noqa
        except ImportError:
            raise ImproperlyConfigured("MemoryJobStore requires pymongo to be installed.")

        if not is_class_and_subclass(client, MongoClient):
            raise ImproperlyConfigured(
                "The client must be a an instance of `pymongo.mongo_client.MongoClient` or subclass."
            )
        super().__init__(database, collection, client, pickle_protocol, **connect_args)


class RedisJobStore(APSchedulerRedisJobStore):
    """
    Stores jobs in a Redis database. Any leftover keyword arguments are directly passed to redis's
    :class:`~redis.StrictRedis`.

    Plugin alias: `redis`.

    Args:
        db: the database number to store jobs in.
        jobs_key: key str to store jobs in.
        run_times_key: key str to store the jobs' run times in.
        pickle_protocol: pickle protocol level (int) to use (for serialization), defaults to the highest available.
    """

    def __init__(
        self,
        db: int = DATABASE_NUMBER,
        jobs_key: str = JOBS_KEY,
        run_times_key: str = RUN_TIMES_KEY,
        pickle_protocol: int = ...,
        **connect_args
    ):
        try:
            import redis  # noqa
        except ImportError:
            raise ImproperlyConfigured("RedisJobStore requires redis to be installed.")

        super().__init__(db, jobs_key, run_times_key, pickle_protocol, **connect_args)


class RethinkDBJobStore(APSchedulerRethinkDBJobStore):
    """
    Stores jobs in a RethinkDB database. Any leftover keyword arguments are directly passed to
    rethinkdb's `RethinkdbClient <http://www.rethinkdb.com/api/#connect>`_.

    Plugin alias: `rethinkdb`.

    Args:
        database: database str to store jobs in.
        collection: collection str to store jobs in.
        client: an instance of [rethinkdb.net.Connection] to use instead of providing connection arguments.
        pickle_protocol: pickle protocol level (int) to use (for serialization), defaults to the highest available.
    """

    def __init__(
        self,
        database: str = DATABASE,
        table: str = TABLE,
        client: Optional[Union[Callable[[], Any], Connection]] = None,
        pickle_protocol: int = ...,
        **connect_args
    ):
        try:
            import rethinkdb  # noqa
        except ImportError:
            raise ImproperlyConfigured("RethinkDBJobStore requires rethinkdb to be installed.")

        if not is_class_and_subclass(client, Connection):
            raise ImproperlyConfigured(
                "The client must be a an instance of `rethinkdb.net.Connection` or subclass."
            )
        super().__init__(database, table, client, pickle_protocol, **connect_args)


class SQLAlchemyJobStore(APSchedulerSQLAlchemyJobStore):
    """
    Stores jobs in a database table using SQLAlchemy.
    The table will be created if it doesn't exist in the database.

    Plugin alias: `sqlalchemy`.

    Args:
        url: connection string (see ref:`SQLAlchemy documentation <sqlalchemy:database_urls>` on this).
        engine: an SQLAlchemy [sqlalchemy.engine.Engine] instance to use instead of creating a new one based on `url`.
        tablename: name of the table to store jobs in.
        metadata: a [sqlalchemy.schema.MetaData] instance to use instead of creating a new one.
        pickle_protocol: pickle protocol level (int) to use (for serialization), defaults to the highest available.
        tableschema: name of the (existing) schema str in the target database where the table should be.
        engine_options: keyword arguments to function [sqlalchemy.create_engine] (ignored if `engine` is given).
    """

    def __init__(
        self,
        url: Optional[str] = None,
        engine: Optional[Union[Callable[[], Any], Engine]] = None,
        tablename: str = SQLALCHEMY_TABLE_NAME,
        metadata: Optional[Union[Callable[[], Any], MetaData]] = None,
        pickle_protocol: int = ...,
        tableschema: Optional[str] = None,
        engine_options: Optional[Dict[Any, Any]] = None,
    ):
        try:
            import sqlalchemy  # noqa
        except ImportError:
            raise ImproperlyConfigured("SQLAlchemyJobStore requires sqlalchemy to be installed.")

        if not is_class_and_subclass(engine, Engine):
            raise ImproperlyConfigured(
                "The engine must be a an instance of `sqlalchemy.engine.Engine` or subclass."
            )

        super().__init__(
            url,
            engine,
            tablename,
            metadata,
            pickle_protocol,
            tableschema,
            engine_options,
        )


class ZooKeeperJobStore(APSchedulerZooKeeperJobStore):
    """
    Stores jobs in a ZooKeeper tree. Any leftover keyword arguments are directly passed to
    kazoo's KazooClient <http://kazoo.readthedocs.io/en/latest/api/client.html>.

    Plugin alias: `zookeeper`.

    Args:
        path: str path to store jobs in.
        client: a [kazoo.client.KazooClient] instance to use instead of providing connection arguments.
        close_connection_on_exit: a boolean flag to close the connections on exit.
        pickle_protocol: pickle protocol level (int) to use (for serialization), defaults to the highest available.
    """

    def __init__(
        self,
        path: str = KAZOO_PATH,
        client: Optional[Union[Callable[[], Any], KazooClient]] = None,
        close_connection_on_exit: bool = False,
        pickle_protocol: int = ...,
        **connect_args
    ):
        try:
            import kazoo  # noqa
        except ImportError:
            raise ImproperlyConfigured("ZooKeeperJobStore requires sqlalchemy to be installed.")

        if not is_class_and_subclass(client, KazooClient):
            raise ImproperlyConfigured(
                "The client must be a an instance of `kazoo.client.KazooClient` or subclass."
            )
        super().__init__(path, client, close_connection_on_exit, pickle_protocol, **connect_args)
