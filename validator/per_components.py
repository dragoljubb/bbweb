import numpy as np
import pandas as pd
from db.connection import get_engine   # 👈 koristiš postojeći
from factor import run_lg_4factor
from vop import run_vop

def mmss_to_minutes(x):
    if pd.isna(x):
        return 0
    m, s = x.split(":")
    return int(m) + int(s) / 60

def get_lg_params(season:str) -> pd.DataFrame:
    engine = get_engine()
    sql = """
         SELECT   g.season_code,
            g.game_date::date AS game_date,
             SUM(b.ft_att) as lg_fta, 
			 SUM(b.ft_made) as lg_ftm, 
             SUM(b.def_rebounds) as lg_dr, 
			 SUM(b.total_rebounds) as lg_tr,
			 SUM(b.fouls_commited) as lg_pf
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
    df["lg_fta_cum"] = df["lg_fta"].cumsum()
    df["lg_ftm_cum"] = df["lg_ftm"].cumsum()
    df["lg_pf_cum"] = df["lg_pf"].cumsum()
    df["lg_dr_cum"] = df["lg_dr"].cumsum()
    df["lg_tr_cum"] = df["lg_tr"].cumsum()
    df["lg_drper"]=df["lg_dr_cum"] /df["lg_tr_cum"]
    return df

def get_team_params(season:str) -> pd.DataFrame:
    engine = get_engine()
    sql = """
         SELECT g.season_code,
         b.team_code,
            g.game_date::date AS game_date,
             SUM(b.assistances) as te_ast, 
			 SUM(b.fg2_made+b.fg3_made) as te_fgm
		 FROM dwh.boxscore_teams b
         INNER JOIN dwh.vw_gamesinfo g
         ON g.season_year = b.season
           AND g.compcode    = b.compcode
           AND g.game_code  = b.gamecode
         WHERE g.season_code = %(season)s
         GROUP BY  g.season_code,
		           b.team_code,
                   g.game_date::date 
         ORDER BY g.game_date::date, b.team_code;
          """
    df = pd.read_sql(sql, engine, params={
        "season": f"{season}"
    })
    df = df.sort_values(["team_code", "game_date"])

    df["te_ast_cum"] = (
        df.groupby("team_code")["te_ast"]
        .cumsum()
    )
    df["te_fgm_cum"] = (
        df.groupby("team_code")["te_fgm"]
        .cumsum()
    )

    return df

def get_player_params(season:str) -> pd.DataFrame:
    engine = get_engine()
    sql = """
         SELECT   g.season_code,
         p.team_code,
            g.game_date::date AS game_date,
			p.player_id as player_code, 
			p.player_name,
			p.fg2_made + p.fg3_made as fgm,
			p.fg2_att + p.fg3_att as fga,
			p.fg3_made as fg3m,
			p.assistances as ast,
			p.ft_made as ftm,
			p.ft_att as fta,
			p.def_rebounds as dr,
			p.off_rebounds as ofr,
			p.turnovers as tov,
			p.steals as st,
			p.blocks_favour as bl,
			p.fouls_commited as pf,
            NULLIF(p.minutes,'DNP') as txtminutes
            FROM dwh.boxscore_players p
                JOIN dwh.vw_gamesinfo g
                  ON g.season_year = p.season
                 AND g.compcode    = p.compcode
                 AND g.game_code  = p.gamecode
                WHERE g.season_code = %(season)s
                ORDER BY g.game_date::date,  p.player_id;
          """


    df = pd.read_sql(sql, engine, params={
        "season": f"{season}"
    })

    df["minutes"] = df["txtminutes"].apply(mmss_to_minutes)
    df = df.sort_values(["player_code", "game_date"])

    df["fgm_cum"] = (
        df.groupby("player_code")["fgm"]
        .cumsum()
    )
    df["fga_cum"] = (
        df.groupby("player_code")["fga"]
        .cumsum()
    )

    df["fg3m_cum"] = (
        df.groupby("player_code")["fg3m"]
        .cumsum()
    )

    df["ast_cum"] = (
        df.groupby("player_code")["ast"]
        .cumsum()
    )
    df["ftm_cum"] = (
        df.groupby("player_code")["ftm"]
        .cumsum()
    )
    df["fta_cum"] = (
        df.groupby("player_code")["fta"]
        .cumsum()
    )

    df["fta_cum"] = (
        df.groupby("player_code")["fta"]
        .cumsum()
    )

    df["dr_cum"] = (
        df.groupby("player_code")["dr"]
        .cumsum()
    )
    df["ofr_cum"] = (
        df.groupby("player_code")["ofr"]
        .cumsum()
    )

    df["tov_cum"] = (
        df.groupby("player_code")["tov"]
        .cumsum()
    )
    df["st_cum"] = (
        df.groupby("player_code")["st"]
        .cumsum()
    )

    df["bl_cum"] = (
        df.groupby("player_code")["bl"]
        .cumsum()
    )

    df["pf_cum"] = (
        df.groupby("player_code")["pf"]
        .cumsum()
    )

    df["minutes_cum"] = (
        df.groupby("player_code")["minutes"]
        .cumsum()
    )



    return df

def calculate_per(pl):
    pl["gper1_until"] = (
            (2 - pl["factor"] * (pl["te_ast_cum"] / pl["te_fgm_cum"]))
            * pl["fgm_cum"]
    )
    pl["gper1_day"] = (
            (2 - pl["factor"] * (pl["te_ast_cum"] / pl["te_fgm_cum"]))
            * pl["fgm"]
    )

    pl["gper2_until"] = (
             pl["fg3m_cum"]
    )
    pl["gper2_day"] = (
           pl["fg3m"]
    )

    pl["gper3_until"] = (
            (2.0 / 3.0) * pl["ast_cum"]
    )
    pl["gper3_day"] = (
            (2.0 / 3.0) * pl["ast"]
    )

    pl["gper4_until"] = (
            0.5 * pl["ftm_cum"] * (1.0 + (1 - (1.0 / 3.0) * pl["te_ast_cum"] / pl["te_fgm_cum"]))
    )
    pl["gper4_day"] = (
            0.5 * pl["ftm"] * (1.0 + (1 - (1.0 / 3.0) * pl["te_ast_cum"] / pl["te_fgm_cum"]))
    )

    pl["gper5_until"] = (
            pl["vop"] * pl["tov_cum"]
    )
    pl["gper5_day"] = (
            pl["vop"] * pl["tov"]
    )

    pl["gper6_until"] = (
            pl["vop"] * pl["lg_drper"] * (pl["fga_cum"] - pl["fgm_cum"])
    )
    pl["gper6_day"] = (
            pl["vop"] * pl["lg_drper"] * (pl["fga"] - pl["fgm"])
    )

    pl["gper7_until"] = (
            pl["vop"] * 0.44 * (0.44 + 0.56 * pl["lg_drper"]) * (pl["fta_cum"] - pl["ftm_cum"])
    )
    pl["gper7_day"] = (
            pl["vop"] * 0.44 * (0.44 + 0.56 * pl["lg_drper"]) * (pl["fta"] - pl["ftm"])
    )

    pl["gper8_until"] = (
            pl["vop"] * (1.0 - pl["lg_drper"]) * pl["dr_cum"]
    )
    pl["gper8_day"] = (
            pl["vop"] * (1.0 - pl["lg_drper"]) * pl["dr"]
    )

    pl["gper9_until"] = (
            pl["vop"] * pl["lg_drper"] * pl["ofr_cum"]
    )
    pl["gper9_day"] = (
            pl["vop"] * pl["lg_drper"] * pl["ofr"]
    )

    pl["gper10_until"] = (
            pl["vop"] * pl["st_cum"]
    )
    pl["gper10_day"] = (
            pl["vop"] * pl["st"]
    )

    pl["gper11_until"] = (
            pl["vop"] * pl["lg_drper"] * pl["bl_cum"]
    )
    pl["gper11_day"] = (
            pl["vop"] * pl["lg_drper"] * pl["bl"]
    )

    pl["gper12_until"] = (
            pl["pf_cum"] * (
                (pl["lg_ftm_cum"] / pl["lg_pf_cum"]) - 0.44 * (pl["lg_fta_cum"] / pl["lg_pf_cum"]) * pl["vop"])
    )
    pl["gper12_day"] = (
            pl["pf"] * (
            (pl["lg_ftm_cum"] / pl["lg_pf_cum"]) - 0.44 * (pl["lg_fta_cum"] / pl["lg_pf_cum"]) * pl["vop"])
    )

    pl["gper_until"] = ((1.0 / pl["minutes_cum"]) * (
                pl["gper1_until"] + pl["gper2_until"] + pl["gper3_until"] + pl["gper4_until"]
                - pl["gper5_until"] - pl["gper6_until"] - pl["gper7_until"]
                + pl["gper8_until"] + pl["gper9_until"] + pl["gper10_until"] + pl["gper11_until"]
                - pl["gper12_until"]))

    pl["gper_day"] = ((1.0 / pl["minutes"]) * (pl["gper1_day"] + pl["gper2_day"] + pl["gper3_day"] + pl["gper4_day"]
                                               - pl["gper5_day"] - pl["gper6_day"] - pl["gper7_day"]
                                               + pl["gper8_day"] + pl["gper9_day"] + pl["gper10_day"] + pl["gper11_day"]
                                               - pl["gper12_day"]))

    df_gper = pl[[
        "season_code",
        "game_date",
        "player_code",
        "player_name",
        "team_code",
        "gper1_day",
        "gper1_until",
        "gper2_day",
        "gper2_until",
        "gper3_day",
        "gper3_until",
        "gper4_day",
        "gper4_until",
        "gper5_day",
        "gper5_until",
        "gper6_day",
        "gper6_until",
        "gper7_day",
        "gper7_until",
        "gper8_day",
        "gper8_until",
        "gper9_day",
        "gper9_until",
        "gper10_day",
        "gper10_until",
        "gper11_day",
        "gper11_until",
        "gper12_day",
        "gper12_until",
        "minutes",
        "minutes_cum",
        "gper_day",
        "gper_until"

    ]].sort_values("game_date")
    return pl

if __name__ == "__main__":
    season_code = "E2025"
    team_code = 'PAR'
    player_code = "006760"
    # player_code = "013667"
    factor_df = run_lg_4factor(season_code)
    vop_df = run_vop(season_code)
    lg_df = get_lg_params(season_code)
    te_df = get_team_params(season_code)
    pl_df = get_player_params(season_code)

    pl = pl_df[pl_df["player_code"] == player_code].copy()
    pl = pl.merge(
        lg_df[[
            "season_code", "game_date",
            "lg_fta_cum", "lg_ftm_cum", "lg_pf_cum", "lg_drper"
        ]],
        on=["season_code", "game_date"],
        how="left"
    )
    pl = pl.merge(
        te_df[[
            "season_code", "game_date", "team_code",
            "te_ast_cum", "te_fgm_cum"
        ]],
        on=["season_code", "game_date", "team_code"],
        how="left"
    )

    pl = pl.merge(
        factor_df[["season_code", "game_date", "factor"]],
        on=["season_code", "game_date"],
        how="left"
    )

    pl = pl.merge(
        vop_df[["season_code", "game_date", "vop"]],
        on=["season_code", "game_date"],
        how="left"
    )
    df_gper=calculate_per(pl)

    print(df_gper.iloc[:, [-4, -3,-2, -1]])

    # print(lg_df.to_string(index=False))
    # print(te_df1.to_string(index=False))
    #print("VOP  | SUM:", round(df["vop"].sum(), 6))
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