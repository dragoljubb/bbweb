from db.connection import get_conn
from pipelines.careerhighs_pipeline import run_careerhighs_pipeline

if __name__ == "__main__":
    conn = get_conn()
    club_code = "PAN"
    run_careerhighs_pipeline(conn, club_code, "E",2025)
    conn.close()
    print(f"finished loading careerhighs for a club {club_code}")
