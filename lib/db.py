from playhouse.pool import PooledPostgresqlExtDatabase

from lib.config import config

PASSWORD = config.get("DB_PASSWORD")
NAME = config.get("DB_NAME")
USER = config.get("DB_USER")
HOST = config.get("DB_HOST")
PORT = 5432  # default postgres port

db = PooledPostgresqlExtDatabase(
    NAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    max_connections=config.get("MAX_DB_CONNECTIONS"),
    stale_timeout=300,  # connections time out after 5 minutes
)
