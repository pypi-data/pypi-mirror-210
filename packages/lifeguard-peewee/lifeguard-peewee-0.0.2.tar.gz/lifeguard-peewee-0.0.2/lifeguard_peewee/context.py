"""
Connection methods implementations
"""

from lifeguard_peewee.settings import (
    LIFEGUARD_PEEWEE_DBMS_NAME,
    LIFEGUARD_PEEWEE_HOST,
    LIFEGUARD_PEEWEE_PORT,
    LIFEGUARD_PEEWEE_USER,
    LIFEGUARD_PEEWEE_PASSWORD,
    LIFEGUARD_PEEWEE_DATABASE,
)

CONTEXT = {}


class DatabaseNotImplementedException(Exception):
    """
    Notify invalid option for DMBS
    """


def connection_factory():
    """
    Return database
    """

    if "database" in CONTEXT:
        return CONTEXT["database"]

    database = None

    if LIFEGUARD_PEEWEE_DBMS_NAME == "mysql":
        from playhouse.pool import PooledMySQLDatabase

        database = PooledMySQLDatabase(
            LIFEGUARD_PEEWEE_DATABASE,
            user=LIFEGUARD_PEEWEE_USER,
            password=LIFEGUARD_PEEWEE_PASSWORD,
            host=LIFEGUARD_PEEWEE_HOST,
            port=LIFEGUARD_PEEWEE_PORT,
            max_connections=15,
            stale_timeout=120,
        )
    else:
        raise DatabaseNotImplementedException(LIFEGUARD_PEEWEE_DBMS_NAME)

    CONTEXT["database"] = database

    return database
