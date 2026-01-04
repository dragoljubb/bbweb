from db.connection import get_conn
from pipelines.team_stats_pipeline import run_team_stats_pipeline

if __name__ == "__main__":
    conn = get_conn()
    club_code = "ULK"
    run_team_stats_pipeline(conn, club_code, "E",2025)
    conn.close()
    print(f"finished loading team stats for a club {club_code}")