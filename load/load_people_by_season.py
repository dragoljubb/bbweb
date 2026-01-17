
from db.connection import get_conn
from api.session import session, sleep_safe
from config.settings import BASE_URL
from db.procedures import call_proc
import json


def fetch_people(compcode:str, season_year: int):
    season_code = f"{compcode}{season_year}"
    url = f"{BASE_URL}/v2/competitions/{compcode}/seasons/{season_code}/people"
    resp = session.get(url, timeout=(5, 15))
    if resp.status_code == 200:
        sleep_safe()
        return resp.json()
    return None

def run_people_pipeline(conn, compcode:str, season_year: int):
    people = fetch_people(compcode, season_year)

    if people:
        call_proc(
            conn,
            "imp.load_raw_people",
            [json.dumps(people), compcode, season_year])

if __name__ == "__main__":
    conn = get_conn()
    compcode = "E"
    season_year = 2025
    run_people_pipeline(conn,  compcode, season_year)
    print(f"Loaded stats for {compcode}{season_year}")
    conn.close()




