from db.connection import get_conn
from pipelines.stats_pipeline import run_stats_pipeline

if __name__ == "__main__":
    conn = get_conn()
    run_stats_pipeline(conn, "PAN", "E", 2025)
    conn.close()
