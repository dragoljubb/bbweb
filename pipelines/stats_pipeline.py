from db.procedures import call_proc
from api.people_api import fetch_person_stats
from pipelines.helpers import get_players_by_club
import json

def run_stats_pipeline(conn, club_code, compcode, season_year):
    players = get_players_by_club(conn, club_code, compcode, season_year)

    for person_code, in players:
        stats = fetch_person_stats(person_code, club_code, compcode, season_year)
        print (f"Loaded stats for {person_code}")
        if stats:
            call_proc(
                conn,
                "imp.load_raw_person_stats",
                [person_code, club_code, compcode, season_year, json.dumps(stats)]
            )
