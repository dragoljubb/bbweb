from db.connection import get_conn
from pipelines.images_pipeline import run_images_pipeline

if __name__ == "__main__":
    conn = get_conn()
    try:
        club_code= "ZAL"
        run_images_pipeline(conn, club_code, 2025)  # primer: Partizan, sezona 2025
    finally:
        conn.close()
        print(f"finished...{club_code}")
