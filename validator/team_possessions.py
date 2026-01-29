import numpy as np
import pandas as pd
from db.connection import get_engine   # 👈 koristiš postojeći
from val_models import *
def run_team_poss(season:str, pteam_code:str) -> pd.DataFrame:
    engine = get_engine()
    sql = """
          SELECT game_code, \
                 game_date, \
                 season_code, \

                 CASE WHEN home_team_code = %(par_team_code)s THEN TRUE ELSE FALSE END                          as is_home, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN home_team_code \
                     ELSE away_team_code END                                                                    as team_code, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN away_team_code \
                     ELSE home_team_code END                                                                    as opp_code, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN home_turnovers \
                     ELSE away_turnovers END                                                                    as team_turnovers, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN home_def_rebounds \
                     ELSE away_def_rebounds END                                                                 as team_def_rebounds, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN home_off_rebounds \
                     ELSE away_off_rebounds END                                                                 as team_off_rebounds, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN home_ft_made \
                     ELSE away_ft_made END                                                                      as team_ftm, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN home_ft_att \
                     ELSE away_ft_att END                                                                       as team_fta, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN (home_fg2_made + home_fg3_made) \
                     ELSE (away_fg2_made + away_fg3_made) END                                                   as team_fgm, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN (home_fg2_att + home_fg3_att) \
                     ELSE (away_fg2_att + away_fg3_att) END                                                     as team_fga, \

                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN away_turnovers \
                     ELSE home_turnovers END                                                                    as opp_turnovers, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN away_def_rebounds \
                     ELSE home_def_rebounds END                                                                 as opp_def_rebounds, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN away_off_rebounds \
                     ELSE home_off_rebounds END                                                                 as opp_off_rebounds, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN away_ft_made \
                     ELSE home_ft_made END                                                                      as opp_ftm, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN away_ft_att \
                     ELSE home_ft_att END                                                                       as opp_fta, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN (away_fg2_made + away_fg3_made) \
                     ELSE (home_fg2_made + home_fg3_made) END                                                   as opp_fgm, \
                 CASE \
                     WHEN home_team_code = %(par_team_code)s THEN (away_fg2_att + away_fg3_att) \
                     ELSE (home_fg2_att + home_fg3_att) END                                                     as opp_fga

          FROM dwh.vw_bs_teams_stat
          WHERE season_code = %(season)s
            AND %(par_team_code)s IN (home_team_code, away_team_code) \
          """

    df = pd.read_sql(sql, engine, params={
        "season": f"{season}", "par_team_code": f"{pteam_code}"
    })


    #
    # df["team_poss"] = (
    #     df["fg_att"]
    #     - df["off_reb"]
    #     + df["turnovers"]
    #     + 0.44 * df["ft_att"]
    # )

    df2 = df.copy()

    # --- TEAM POSS ---
    df["team_poss"] = (
            df["team_fga"]
            + 0.44 * df["team_fta"]
            - 1.07 * (
                    df["team_off_rebounds"] /
                    (df["team_off_rebounds"] + df["opp_def_rebounds"])
            ) * (df["team_fga"] - df["team_fgm"])
            + df["team_turnovers"]
    )

    # --- OPP POSS ---
    df["opp_poss"] = (
            df["opp_fga"]
            + 0.44 * df["opp_fta"]
            - 1.07 * (
                    df["opp_off_rebounds"] /
                    (df["opp_off_rebounds"] + df["team_def_rebounds"])
            ) * (df["opp_fga"] - df["opp_fgm"])
            + df["opp_turnovers"]
    )

    # --- GAME POSS ---
    df["game_poss"] = (df["team_poss"] + df["opp_poss"]) / 2
    df["diff"] = (df["team_poss"] - df["opp_poss"]).abs()

    # kumulativa (posle sort-a!)
    df = df.sort_values("game_date")
    df["team_poss_cum"] = df["team_poss"].cumsum()

    # --- GAME POSS ---
    df["game_poss"] = (df["team_poss"] + df["opp_poss"]) / 2
    df["diff"] = (df["team_poss"] - df["opp_poss"]).abs()



    df["team_poss_cum"] = df["team_poss"].cumsum()


    sum_row = pd.DataFrame([{
        "game_code": "SUM",
        "team_poss": df["team_poss"].sum(),
        "game_poss": df["game_poss"].sum()
    }])

    avg_row = pd.DataFrame([{
        "game_code": "AVG",
        "team_poss": df["team_poss"].mean(),
        "opp_poss": df["opp_poss"].mean(),
        "game_poss": df["game_poss"].mean()
    }])

    df2 = pd.concat([df, sum_row, avg_row], ignore_index=True)

    # brzi check

    # print("\nTOP DIFF:")
    # print(df.sort_values("diff", ascending=False)[
    #           ["game_code", "team_poss", "opp_poss", "diff"]
    #       ].head())


    return df


def games_possesion(season):
    engine = get_engine()
    sql = """
           SELECT
            g.season_code,
            g.game_code,
            g.game_date,

            g.home_team_code AS team_code,
            g.away_team_code AS opp_code,
            TRUE             AS is_home,
            (g.home_fg2_att + g.home_fg3_att) as fga,
                g.home_off_rebounds as or,
                g.away_def_rebounds as opp_dr,
                (g.home_fg2_made + g.home_fg3_made) as fgm,
                g.home_turnovers as to,
                g.home_ft_att as fta   
           FROM dwh.vw_bs_teams_stat g
           WHERE season_code = %(season)s

            UNION ALL
    
            /* =========================
               AWAY TIM
               ========================= */
            SELECT
                g.season_code,
                g.game_code,
                g.game_date,
    
                g.away_team_code AS team_code,
                g.home_team_code AS opp_code,
                FALSE            AS is_home,
                (g.away_fg2_att + g.away_fg3_att) as fga,
                g.away_off_rebounds as or,
                g.home_def_rebounds as opp_dr,
                (g.away_fg2_made + g.away_fg3_made) as fgm,
                g.away_turnovers as to,
                g.away_ft_att as fta
            FROM dwh.vw_bs_teams_stat g
           WHERE season_code = %(season)s
             
          """

    df = pd.read_sql(sql, engine, params={
        "season": f"{season}"
    })
    return df


def minutes_played(season):
    engine = get_engine()
    sql = """
          SELECT  game_code, 
                  team_code, 
                  season_code, 
                  ROUND(minutes,0) as min 
          from  dwh.vw_team_minutes_dec tm       
          WHERE season_code = %(season)s
          """

    df = pd.read_sql(sql, engine, params={
        "season": f"{season}"
    })
    return df
def get_team_lg_poss_pace(season_code):
    df = games_possesion(season_code)

    df["game_date"] = pd.to_datetime(df["game_date"])

    df_min = minutes_played(season_code)
    df_min = df_min.sort_values(["season_code", "team_code"]).reset_index(drop=True)

    df = df.merge(
        df_min,
        on=["season_code", "game_code", "team_code"],
        how="left"
    )

    # df = df.rename(columns={"team_code_x": "team_code"})

    df = df.sort_values(["season_code", "game_date", "game_code"])

    df = df.sort_values(["season_code", "team_code", "game_date", "game_code"])

    df["fga_cum"] = df.groupby(["season_code", "team_code"])["fga"].cumsum()
    df["fgm_cum"] = df.groupby(["season_code", "team_code"])["fgm"].cumsum()
    df["fta_cum"] = df.groupby(["season_code", "team_code"])["fta"].cumsum()
    df["or_cum"] = df.groupby(["season_code", "team_code"])["or"].cumsum()
    df["opp_dr_cum"] = df.groupby(["season_code", "team_code"])["opp_dr"].cumsum()
    df["to_cum"] = df.groupby(["season_code", "team_code"])["to"].cumsum()
    df["min_cum"] = df.groupby(["season_code", "team_code"])["min"].cumsum()
    df["team_poss_cum"] = (
                df["fga_cum"] + 0.44 * df["fta_cum"] - 1.07 * (df["or"] / (df["or_cum"] + df["opp_dr_cum"])) * (
                    df["fga_cum"] - df["fgm_cum"]) + df["to_cum"])
    df["team_poss_cum_gameavg"] = (
            df["fga_cum"] + 0.44 * df["fta_cum"] - 1.07 * (df["or"] / (df["or_cum"] + df["opp_dr_cum"])) * (
            df["fga_cum"] - df["fgm_cum"]) + df["to_cum"]

    )


    df["team_pace_cum"] = df["team_poss_cum"] * 200 / df["min_cum"]

    cols = ["fga", "fgm", "fta", "or", "opp_dr", "to", "min"]  # dodaj šta ti treba

    df["game_date"] = pd.to_datetime(df["game_date"])

    lg_day = (
        df.groupby(["season_code", "game_date"], as_index=False)[cols]
        .sum()
        .sort_values(["season_code", "game_date"])
    )

    # kumulacija po sezoni
    lg = lg_day.copy()
    lg[[f"lg_{c}" for c in cols]] = (
        lg_day.groupby("season_code")[cols].cumsum()
    )

    # zadrži samo kumulativne kolone + ključeve
    lg = lg[["season_code", "game_date"] + [f"lg_{c}" for c in cols]]

    lg = lg.sort_values(["season_code", "game_date"])

    lg["lg_fga_cum"] = lg.groupby(["season_code", "game_date"])["lg_fga"].cumsum()
    lg["lg_fgm_cum"] = lg.groupby(["season_code", "game_date"])["lg_fgm"].cumsum()
    lg["lg_fta_cum"] = lg.groupby(["season_code", "game_date"])["lg_fta"].cumsum()
    lg["lg_or_cum"] = lg.groupby(["season_code", "game_date"])["lg_or"].cumsum()
    lg["lg_opp_dr_cum"] = lg.groupby(["season_code", "game_date"])["lg_opp_dr"].cumsum()
    lg["lg_to_cum"] = lg.groupby(["season_code", "game_date"])["lg_to"].cumsum()
    lg["lg_min_cum"] = 0.5 * lg.groupby(["season_code", "game_date"])["lg_min"].cumsum()

    lg["lg_poss_cum"] = 0.5 * (
            lg["lg_fga_cum"] + 0.44 * lg["lg_fta_cum"] - 1.07 * (
                lg["lg_or"] / (lg["lg_or_cum"] + lg["lg_opp_dr_cum"])) * (
                    lg["lg_fga_cum"] - lg["lg_fgm_cum"]) + lg["lg_to_cum"])

    lg["lg_pace_cum"] = lg["lg_poss_cum"] * 200 / lg["lg_min_cum"]
    lg = lg.sort_values(["season_code", "game_date"])
    df = df.sort_values(["season_code", "game_date"])

    df = df.merge(
        lg,
        on=["season_code", "game_date"],
        how="left"
    )
    df = df.sort_values(["season_code", "game_date", "game_code"])
    df = df[["season_code", "game_date", "team_code","min_cum","lg_min_cum", "team_poss_cum", "team_pace_cum", "lg_poss_cum",
             "lg_pace_cum"]]



    # merge nazad u originalni df
    # df = df.merge(
    #     lg_cum,
    #     on=["season_code", "game_date"],
    #     how="left"
    # )

    # df_red = df[df["team_code"] == "RED"]
    # print(df_red.columns)
    # print(df_red)
    # print(df_red.iloc[:, [1,2,3, 14,10,-2,-1]])

    #
    # df = run_team_poss("E2025", "RED")
    # print(df[["game_code", "game_date", "team_code", "opp_code", "team_fga", "team_fgm", "team_fta", "team_off_rebounds",
    #           "team_def_rebounds", "opp_def_rebounds", "team_turnovers",
    #           "team_poss", "opp_poss", "game_poss", "team_poss_cum"]].to_string(index=False))
    #
    # print("TEAM POSS  | SUM:", round(df["team_poss"].sum(), 2),
    #      "| AVG:", round(df["team_poss"].mean(), 2))
    #
    # print("GAME POSS  | SUM:", round(df["game_poss"].sum(), 2),
    #       "| AVG:", round(df["game_poss"].mean(), 2))
    return df

def validate_possessions(df):

    df = df.sort_values("game_date").reset_index(drop=True)
    df["diff"] = (df["team_poss"] - df["opp_poss"]).abs()

    team_sum = df["team_poss"].sum()
    team_avg = df["team_poss"].mean()

    game_sum = df["game_poss"].sum()
    game_avg = df["game_poss"].mean()

    print("\n=== POSSESSIONS SUMMARY ===")
    print(f"TEAM poss | SUM: {team_sum:.2f} | AVG: {team_avg:.2f}")
    print(f"GAME poss | SUM: {game_sum:.2f} | AVG: {game_avg:.2f}")

    print("\n=== TOP DIFF GAMES ===")
    print(df.sort_values("diff", ascending=False)[
        ["game_code","team_code","opp_code","team_poss","opp_poss","game_poss","diff"]
    ].head(5).to_string(index=False))

    # ---------- ASSERTS ----------

    # 1. realan opseg
    assert df["team_poss"].between(55, 95).all(), "Unrealistic TEAM poss found"
    assert df["game_poss"].between(55, 95).all(), "Unrealistic GAME poss found"

    # 2. game poss formula check
    assert ((df["game_poss"] - (df["team_poss"] + df["opp_poss"]) / 2).abs() < 0.01).all(), \
        "Game poss formula broken"

    # 3. team vs opp balance
    assert abs(team_sum - df["opp_poss"].sum()) < 5, "Team vs opp poss total mismatch too big"

    # 4. pojedinačne utakmice
    assert df["diff"].max() < 4, "Some games have too big poss difference"

    print("\n✔ POSSESSIONS VALIDATION PASSED")


if __name__ == "__main__":
    season_code = "E2025"
    df = get_team_lg_poss_pace(season_code)
    print(df)




