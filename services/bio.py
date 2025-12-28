from db.procedures import call_proc
from api.people_api import get_person
from api.session import sleep_safe

def process_bio(conn, person_code):
    data = get_person(person_code)

    call_proc(
        conn,
        "dwh.upsert_person_bio",
        [person_code, data]
    )

    sleep_safe()
