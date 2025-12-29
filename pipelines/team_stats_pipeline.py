from db.procedures import call_proc
from api.people_api import fetch_team_stats
from pipelines.helpers import get_players_by_club
import json

def run_team_stats_pipeline(conn, club_code, competition,  season_year):

        team_stats = fetch_team_stats(competition, season_year, club_code)
        print (f"Loadeding team_stats for {club_code}")
        if team_stats:
            call_proc(
                conn,
                "imp.load_raw_team_stats",
                [json.dumps(team_stats),club_code, competition, season_year]
            )
