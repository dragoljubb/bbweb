from db.procedures import call_proc
from api.people_api import fetch_person_bio
from pipelines.helpers import get_people_by_club
import json

def run_bio_pipeline(conn, club_code, season_year):
    people = get_people_by_club(conn, club_code, season_year)

    for person_code, club_code, season_year, image_action in people:
        bio = fetch_person_bio(person_code)
        if bio:
            call_proc(
                conn,
                "imp.load_raw_person_bio",
                [json.dumps(bio), person_code]
            )
