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
    df = run_team_poss("E2025", "PAR")
    print(df[["game_code", "game_date", "team_code", "opp_code", "team_fga", "team_fgm", "team_fta", "team_off_rebounds",
              "team_def_rebounds", "opp_def_rebounds", "team_turnovers",
              "team_poss", "opp_poss", "game_poss", "team_poss_cum"]].to_string(index=False))

    print("TEAM POSS  | SUM:", round(df["team_poss"].sum(), 2),
         "| AVG:", round(df["team_poss"].mean(), 2))

    print("GAME POSS  | SUM:", round(df["game_poss"].sum(), 2),
          "| AVG:", round(df["game_poss"].mean(), 2))



