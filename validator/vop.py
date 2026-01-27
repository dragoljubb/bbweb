import numpy as np
import pandas as pd
from db.connection import get_engine   # 👈 koristiš postojeći
def run_vop(season:str) -> pd.DataFrame:
    engine = get_engine()
    sql = """
         SELECT   g.season_code,
            g.game_date::date AS game_date,
            SUM(b.points)  lg_pts, 
            SUM(b.fg2_att +b.fg3_att ) as lg_fga, 
             SUM(b.ft_att) as lg_fta, 
             SUM(b.off_rebounds) as lg_or,
            SUM(b.turnovers) as lg_to
		 FROM dwh.boxscore_teams b
         INNER JOIN dwh.vw_gamesinfo g
         ON g.season_year = b.season
           AND g.compcode    = b.compcode
           AND g.game_code  = b.gamecode
         WHERE g.season_code = %(season)s
         GROUP BY  g.season_code,
                g.game_date::date 
         ORDER BY g.game_date::date 
          """

    df = pd.read_sql(sql, engine, params={
        "season": f"{season}"
    })
    df["lg_pts_cum"] = df["lg_pts"].cumsum()
    df["lg_fga_cum"] = df["lg_fga"].cumsum()
    df["lg_fta_cum"] = df["lg_fta"].cumsum()
    df["lg_or_cum"] = df["lg_or"].cumsum()
    df["lg_to_cum"] = df["lg_to"].cumsum()
    df["vop"] = (
            df["lg_pts_cum"] / (df["lg_fga_cum"] + 0.44 * df["lg_fta_cum"]
                                - df["lg_or_cum"] + df["lg_to_cum"])

    )
    return df


if __name__ == "__main__":
    season_code = "E2025"
    df = run_vop(season_code)


    print(df.to_string(index=False))
    print("VOP  | SUM:", round(df["vop"].sum(), 6))
    # points = run_team_points("E2025", pteam_code)
    # poss = run_team_poss("E2025",pteam_code)
    # df = poss.merge(points, on=["season_code", "game_code"])
    # df["def_rat"] =100.0* ( df["opp_score"] /df["game_poss"] )
    # df["off_rat"] = 100.0 * (df["team_score"] / df["game_poss"])
    # df["def_rat_avg"] = df["def_rat"].expanding().mean()
    # df["off_rat_avg"]=df["off_rat"].expanding().mean()
    #

    # print(df[["season_code","team_code", "game_poss", "game_code", "team_code", "opp_code",  "team_code1", "opp_code1", "team_score","opp_score",
    #           "def_rat","off_rat", "def_rat_avg", "off_rat_avg"]].to_string(index=False))

    # print(df[["def_rat_avg", "off_rat_avg"]].tail(1))

    # print(df1[["season_code", "game_code",  "home_code", "away_code", "home_score", "away_score"]].to_string(index=False))

    # print("HOME SCORE  | SUM:", round(df1["home_score"].sum(), 2),
    #      "| AVG:", round(df1["home_score"].mean(), 2))
    #
    # print("AWAT SCORE  | SUM:", round(df1["away_score"].sum(), 2),
    #       "| AVG:", round(df1["away_score"].mean(), 2))