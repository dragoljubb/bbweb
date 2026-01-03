from db.connection import get_conn
from pipelines.standing_pipeline import run_standing_pipeline

if __name__ == "__main__":
    conn = get_conn()
    round = 19
    compcode= "E"
    season_year = 2025
    run_standing_pipeline(conn, round, compcode, season_year)
    conn.close()