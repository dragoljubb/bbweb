import psycopg2
from config.settings import DB
from sqlalchemy import create_engine

def get_conn():
    return psycopg2.connect(**DB)

DB_URI = "postgresql+psycopg2://user:pass@host:5432/dbname"

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        uri = (
            f"postgresql+psycopg2://{DB['user']}:{DB['password']}"
            f"@{DB['host']}:{DB.get('port',5432)}/{DB['dbname']}"
        )
        _engine = create_engine(uri, pool_pre_ping=True)
    return _engine