import psycopg2
from config.settings import DB

def get_conn():
    return psycopg2.connect(**DB)