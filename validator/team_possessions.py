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
            ROUND(tm.minutes,0) as team_minutes,
            ROUND(am.minutes,0) as opp_minutes,   
            
            TRUE             AS is_home,
            (g.home_fg2_att + g.home_fg3_att) as fga,
            (g.away_fg2_att + g.away_fg3_att) as opp_fga,
            
            g.home_off_rebounds as or,
            g.away_off_rebounds as opp_or,  
            g.away_def_rebounds as opp_dr,
            g.home_def_rebounds as dr,
            (g.home_fg2_made + g.home_fg3_made) as fgm,
            (g.away_fg2_made + g.away_fg3_made) as opp_fgm,
            g.home_turnovers as to,
            g.away_turnovers as opp_to,
            g.home_ft_att as fta,   
            g.away_ft_att as opp_fta
           FROM dwh.vw_bs_teams_stat g
               INNER JOIN dwh.vw_team_minutes_dec tm
            ON tm.season_code = g.season_code 
               AND tm.team_code = g.home_team_code
               AND tm.game_code = g.game_code
            INNER JOIN dwh.vw_team_minutes_dec am
            ON am.season_code = g.season_code 
               AND am.team_code = g.away_team_code
               AND am.game_code = g.game_code
           WHERE g.season_code = %(season)s

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
                ROUND(am.minutes,0) as team_minutes,
                ROUND(tm.minutes,0) as opp_minutes,
                
                FALSE            AS is_home,
                (g.away_fg2_att + g.away_fg3_att) as fga,
                (g.home_fg2_att + g.home_fg3_att) as fga,
                
                g.away_off_rebounds as or,
                g.home_off_rebounds as opp_or,
                g.home_def_rebounds as opp_dr,
                g.away_def_rebounds as dr,
                (g.away_fg2_made + g.away_fg3_made) as fgm,
                (g.home_fg2_made + g.home_fg3_made) as opp_fgm,
                g.away_turnovers as to,
                g.home_turnovers as opp_to,
                g.away_ft_att as fta,
                g.home_ft_att as opp_fta
            FROM dwh.vw_bs_teams_stat g
               INNER JOIN dwh.vw_team_minutes_dec tm
            ON tm.season_code = g.season_code 
               AND tm.team_code = g.home_team_code
               AND tm.game_code = g.game_code
               INNER JOIN dwh.vw_team_minutes_dec am
            ON am.season_code = g.season_code 
               AND am.team_code = g.away_team_code
               AND am.game_code = g.game_code
           WHERE g.season_code = %(season)s
             
          """

    df = pd.read_sql(sql, engine, params={
        "season": f"{season}"
    })
    return df


def get_team_lg_poss_pace(season_code):
    import pandas as pd  #
    df = games_possesion(season_code)

    df["game_date"] = pd.to_datetime(df["game_date"])


    # df = df.rename(columns={"team_code_x": "team_code"})

    df = df.sort_values(["season_code", "game_date", "game_code"])

    df = df.sort_values(["season_code", "team_code", "game_date", "game_code"])
    #
    # df["fga_cum"] = df.groupby(["season_code", "team_code"])["fga"].cumsum()
    # df["fgm_cum"] = df.groupby(["season_code", "team_code"])["fgm"].cumsum()
    # df["fta_cum"] = df.groupby(["season_code", "team_code"])["fta"].cumsum()
    # df["or_cum"] = df.groupby(["season_code", "team_code"])["or"].cumsum()
    # df["opp_dr_cum"] = df.groupby(["season_code", "team_code"])["opp_dr"].cumsum()
    # df["to_cum"] = df.groupby(["season_code", "team_code"])["to"].cumsum()
    #
    #
    # df["opp_fga_cum"] = df.groupby(["season_code", "team_code"])["opp_fga"].cumsum()
    # df["opp_fgm_cum"] = df.groupby(["season_code", "team_code"])["fgm"].cumsum()
    # df["opp_fta_cum"] = df.groupby(["season_code", "team_code"])["fta"].cumsum()
    # df["opp_or_cum"] = df.groupby(["season_code", "team_code"])["opp_or"].cumsum()
    # df["dr_cum"] = df.groupby(["season_code", "team_code"])["dr"].cumsum()
    # df["opp_to_cum"] = df.groupby(["season_code", "team_code"])["opp_to"].cumsum()






    df["team_poss"] = 0.5* ((
                df["fga"] + 0.44 * df["fta"] - 1.07 * (df["or"] / (df["or"] + df["opp_dr"])) * (
                    df["fga"] - df["fgm"]) + df["to"])
        +

    # + (
    #         df["opp_fga"] + 0.44 * df["opp_fta"] - 1.07 * (df["opp_or"] / (df["opp_or"] + df["dr"])) * (
    #         df["opp_fga"] - df["opp_fgm"]) + df["opp_to"]
    #
    # )
   (
                        df["opp_fga"] + 0.44 * df["opp_fta"] - 1.07 * (df["opp_or"] / (df["opp_or"] + df["dr"])) * (
                           df["opp_fga"] - df["opp_fgm"]) + df["opp_to"])
                            )
        #
        #         )

    df["team_min"] = 0.5 * (df["team_minutes"] + df["opp_minutes"])

    cols = [
        "season_code",
        "game_code",
        "game_date",
        "team_code",
        "opp_code",
        "is_home",
        "team_min",
        "team_poss"
    ]

    df_team = df[cols]

    df_team["game_date"] = pd.to_datetime(df_team["game_date"])

    # OBAVEZNO sortiranje
    df_team = df_team.sort_values(["team_code", "game_date"])

    # kumulativi po timu
    df_team["team_poss_until"] = (
        df_team
        .groupby("team_code")["team_poss"]
        .cumsum()
    )

    df_team["team_min_until"] = (
        df_team
        .groupby("team_code")["team_min"]
        .cumsum()
    )
    cols = [
        "season_code",
        "game_code",
        "game_date",
        "team_code",
        "team_min_until",
        "team_poss_until"
    ]
    df_team=df_team[cols]
    # df_team = df_team[df_team["game_code"] ==3]

    df_team["team_pace_until"] =  200*df_team["team_poss_until"]/df_team["team_min_until"]

    df_tmp = (
        df.sort_values(["game_code", "is_home"], ascending=[True, False])
        .copy()
    )

    # 2) numerisanje redova unutar svake utakmice (0 = team, 1 = opp)
    df_tmp["side"] = df_tmp.groupby("game_code").cumcount()

    df_games = (
        df_tmp
        .pivot(
            index=["game_code", "game_date"],
            columns="side",
            values=["team_code", "team_min", "team_poss"]
        )
    )



    df_games.columns = [
        "team_code", "opp_code",
        "team_min", "opp_min",
        "team_poss", "opp_poss"
    ]

    df_games = df_games.reset_index()  # ⬅️ OVO TI JE FALILO

    df_games["team_norm_poss"] = 0.5 * (
            df_games["team_poss"] + df_games["opp_poss"]
    )

    df_games["min_norm"] = 0.5 * (
            df_games["team_min"] + df_games["opp_min"]
    )

    df_games = df_games.sort_values(["game_date"])



    # 1) agregacija po datumu (međukorak, ne finalni df)
    lg = (
        df_games
        .groupby("game_date", as_index=False)
        .agg(
            lg_poss_day=("team_norm_poss", "sum"),
            lg_min_day=("min_norm", "sum")
        )
        .sort_values("game_date")
    )

    # 2) kumulativi (DO DATUMA)
    lg["lg_poss_until"] = lg["lg_poss_day"].cumsum()
    lg["lg_min_until"] = lg["lg_min_day"].cumsum()

    # 3) liga pace-until
    lg["lg_pace_until"] = (
            200*lg["lg_poss_until"] / (lg["lg_min_until"] )

    )

    # 4) zadrži samo ono što ti treba
    df_lg_until = lg[
        ["game_date", "lg_poss_until", "lg_min_until", "lg_pace_until"]
    ]


    df_result = df_team.merge(df_lg_until, on="game_date", how="left")
    cols = [
        "season_code",
        "game_date",
        "team_code",
        "team_poss_until",
        "team_pace_until",
        "team_min_until",
        "lg_poss_until",
        "lg_pace_until",
        "lg_min_until"
    ]

    df_result = df_result[cols]

    df_result = df_result.rename(columns={
        "team_poss_until": "team_poss",
        "team_pace_until": "team_pace",
        "team_min_until" : "team_min",
        "lg_poss_until": "lg_poss",
        "lg_pace_until": "lg_pace",
        "lg_min_until": "lg_min"
    })



    return df_result


if __name__ == "__main__":
    season_code = "E2025"
    df = get_team_lg_poss_pace(season_code)
    col_de=["team_code", "game_date",  "team_poss_cum"]
    # print(df.columns)
    df=df[df["team_code"] == "PAR"]
    df=df[col_de]
    # print(df)




