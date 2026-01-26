import numpy as np
import pandas as pd
from db.connection import get_engine   # 👈 koristiš postojeći
from team_possessions import run_team_poss
def run_team_points(season:str, pteam_code:str) -> pd.DataFrame:
    engine = get_engine()
    sql = """
         SELECT season_code, game_code, 
                home_code, 
                CASE WHEN home_code = %(par_team_code)s THEN home_code ELSE away_code END team_code1,       
                CASE WHEN away_code = %(par_team_code)s THEN home_code ELSE away_code END opp_code1, 
                CASE WHEN home_code = %(par_team_code)s THEN home_score ELSE away_score END team_score, 
                CASE WHEN away_code = %(par_team_code)s THEN home_score ELSE away_score END opp_score
         FROM dwh.vw_gamesinfo
            WHERE played AND season_code = %(season)s AND %(par_team_code)s IN (home_code, away_code) 
             ORDER BY game_code ASC
          """

    df = pd.read_sql(sql, engine, params={
        "season": f"{season}", "par_team_code": f"{pteam_code}"
    })
    return df

if __name__ == "__main__":
    season_code = "E2025"
    pteam_code = "BAR"
    points = run_team_points("E2025", pteam_code)
    poss = run_team_poss("E2025",pteam_code)
    df = poss.merge(points, on=["season_code", "game_code"])
    df["def_rat"] =100.0* ( df["opp_score"] /df["game_poss"] )
    df["off_rat"] = 100.0 * (df["team_score"] / df["game_poss"])
    df["def_rat_avg"] = df["def_rat"].expanding().mean()
    df["off_rat_avg"]=df["off_rat"].expanding().mean()
    # print(df[["season_code","team_code", "game_poss", "game_code", "team_code", "opp_code",  "team_code1", "opp_code1", "team_score","opp_score",
    #           "def_rat","off_rat", "def_rat_avg", "off_rat_avg"]].to_string(index=False))

    print(df[["def_rat_avg", "off_rat_avg"]].tail(1))

    # print(df1[["season_code", "game_code",  "home_code", "away_code", "home_score", "away_score"]].to_string(index=False))

    # print("HOME SCORE  | SUM:", round(df1["home_score"].sum(), 2),
    #      "| AVG:", round(df1["home_score"].mean(), 2))
    #
    # print("AWAT SCORE  | SUM:", round(df1["away_score"].sum(), 2),
    #       "| AVG:", round(df1["away_score"].mean(), 2))