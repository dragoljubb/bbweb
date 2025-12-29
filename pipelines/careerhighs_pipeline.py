from db.procedures import call_proc
from api.people_api import fetch_person_careerhighs
from pipelines.helpers import get_players_by_club
import json

def run_careerhighs_pipeline(conn, club_code, competition,  season_year):
    players = get_players_by_club(conn, club_code,competition, season_year)

    for person_code, in players:
        careerhighs = fetch_person_careerhighs(person_code, competition)
        print (f"Loaded careerhighs for {person_code}")
        if careerhighs:
            call_proc(
                conn,
                "imp.load_raw_person_careerhighs",
                [json.dumps(careerhighs), person_code, competition]
            )
