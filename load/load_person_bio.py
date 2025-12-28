from db.connection import get_conn
from pipelines.bio_pipeline import run_bio_pipeline

if __name__ == "__main__":
    conn = get_conn()
    run_bio_pipeline(conn, "BAR", 2025)
    conn.close()
