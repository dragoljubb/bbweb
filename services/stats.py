from db.procedures import call_proc
from api.people_api import get_person_stats
from api.session import sleep_safe

def process_stats(conn, person_code, season_code):
    stats = get_person_stats(person_code, season_code)

    call_proc(
        conn,
        "dwh.upsert_person_stats",
        [person_code, season_code, stats]
    )

    sleep_safe()
