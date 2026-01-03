from db.procedures import call_proc
from api.standing_api import fetch_standing

import json

def run_standing_pipeline(conn, round, compcode, season_year):

    standing = fetch_standing(round, compcode, season_year)
    if standing:
            call_proc(
                conn,
                "imp.load_raw_standings",
                [json.dumps(standing), compcode, season_year, round],
            )