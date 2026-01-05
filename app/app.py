from flask import Flask, render_template, Blueprint, request, redirect, url_for, abort
from models import *
from utils.images import  *
from collections import defaultdict


app = Flask(__name__)
app.jinja_env.globals["team_logo"] = team_logo
app.jinja_env.globals["person_img"] = person_img
app.jinja_env.globals["news_image"] = news_image
main_bp = Blueprint('main_bp', __name__)
COMPETITION_CODE = "E"

@main_bp.route('/')
def home():
    current_round = get_current_round_phase(COMPETITION_CODE)
    def_season_code = 'E2025'
    games = get_upcoming_games(current_round.round, def_season_code) if current_round else []
    main_news, slider_news = get_home_news()

    teams_sidebar = get_clubsbyseasoncode(def_season_code)
    return render_template('pages/home.html',
                           current_round=current_round,
                           games=games,
                           main_news=main_news,
                           slider_news=slider_news,
                           teams_sidebar=teams_sidebar)

# ===========================
# Games page
# ===========================
from flask import request, redirect, url_for



@main_bp.route('/games')
def games():
    season = request.args.get("season")
    phase = request.args.get("phase", "RS")
    team = request.args.get("team")
    selected_round = request.args.get("round", type=int)

    # default season / round
    if not season or not selected_round:
        default_season_raw = get_current_season(COMPETITION_CODE)
    #   default_season = default_season_raw[0]["season_code"]
        default_season = 'E2025'
        default_round = get_current_round_phase(COMPETITION_CODE).round
        return redirect(url_for("main_bp.games",
                                season=default_season,
                                round=default_round,
                                phase=phase))

    # UI podaci
    listseasons = get_seasons(COMPETITION_CODE)
    seasons = [{"code": r.season_code, "label": r.season_info_alias} for r in listseasons]
    phases = [{"phase": p.phase} for p in get_phases(season)]
    teams = [{"crest": t.crest_url, "team_name": t.club_name, "code": t.club_code}
             for t in get_clubsbyseasoncode(season)]
    teams_sidebar = get_clubsbyseasoncode(season)

    if not team:
        # LEAGUE VIEW
        rounds = [{"season_code": r.season_code, "round": r.round, "round_name": r.round_name, "phase": r.phase}
                  for r in get_rounds(season)]
        games_data = get_upcoming_games(selected_round, season)

        return render_template("pages/games.html",
                               mode="LEAGUE",
                               season=season,
                               phase=phase,
                               seasons=seasons,
                               phases=phases,
                               teams=teams,
                               selected_team=None,
                               rounds=rounds,
                               selected_round=selected_round,
                               games=games_data,
                               teams_sidebar=teams_sidebar)
    else:
        # TEAM VIEW
        games = get_team_games(season, team)
        next_game = next((g for g in games if g.game_status == "NEXT"), None)
        results = [g for g in games if g.game_status == "RESULT"]
        upcoming = [g for g in games if g.game_status == "UPCOMING"]
        season_label = next((s["label"] for s in seasons if s["code"] == season), season)
        selected_team_name = next((t["team_name"] for t in teams if t["code"] == team), team)
        return render_template("pages/games.html",
                               mode="TEAM",
                               season=season,
                               phase=phase,
                               seasons=seasons,
                               phases=phases,
                               teams=teams,
                               selected_team=team,
                               selected_round=selected_round,
                               teams_sidebar=teams_sidebar,
                               selected_team_name=selected_team_name,
                               season_label=season_label,
                               games=games,
                               next_game=next_game,
                               results=results,
                               upcoming=upcoming
                               )

@main_bp.route("/standings")
def standings():
    season_code = request.args.get("season", "E2025")

    last_round = get_last_round(season_code).round
    round_ = int(request.args.get("round", last_round))
    season = request.args.get("season")
    rounds = get_available_rounds( season_code)
    standings = get_standings(season_code, round_)
    teams_sidebar = get_clubsbyseasoncode(season_code)
    return render_template(
        "pages/standings.html",
        standings=standings,
        rounds=rounds,
        selected_round=round_,
        teams_sidebar=teams_sidebar,
        selected_season=season_code
    )

@main_bp.route("/teams")
def teams():
    season_code = request.args.get("season", "E2025")
    listseasons = get_seasons(COMPETITION_CODE)
    seasons = [{"code": r.season_code, "label": r.season_info_alias} for r in listseasons]
    teams_sidebar = get_clubsbyseasoncode(season_code)
    teams = [{"crest": t.crest_url, "team_name": t.club_name, "code": t.club_code}
             for t in get_clubsbyseasoncode(season_code)]
    return render_template(
        "pages/teams.html",
        teams_sidebar=teams_sidebar,
        teams = teams,
        selected_season=season_code,
        seasons=seasons
    )


@app.route("/teams/<team_code>")
def team_details(team_code):
    season = request.args.get("season", "E2025")  # default sezona
    team = get_clubbyseason_team_details(season, team_code)
    games = get_team_games(season, team_code)
    next_game = next((g for g in games if g.game_status == "NEXT"), None)
    results = [g for g in games if g.game_status == "RESULT"]
    upcoming = [g for g in games if g.game_status == "UPCOMING"]
    teams_sidebar = get_clubsbyseasoncode(season)
    roster = get_roster(season, team_code)
    coaches = get_coaches(season, team_code)
    team_stats = get_team_stats(season, team_code)
    players_stats = get_players_stats(season, team_code)

    grouped_roster = defaultdict(list)

    for player in roster:
        grouped_roster[player.position_name].append(player)

    # SORT po broju dresa
    for pos in grouped_roster:
        grouped_roster[pos].sort(
            key=lambda p: (p.dorsal is None, p.dorsal)
        )

    position_order = ["Guard", "Forward", "Center"]

    team_stats_list = [
        {"label": "Points", "avg": team_stats.avg_points, "tot": team_stats.acc_points, "highlight": False},

        {"label": "Rebounds", "avg": team_stats.avg_total_rebounds, "tot": team_stats.acc_total_rebounds,
         "highlight": False},
        {"label": "Assists", "avg": team_stats.avg_assistances, "tot": team_stats.acc_assistances, "highlight": False},
        {"label": "Steals", "avg": team_stats.avg_steals, "tot": team_stats.acc_steals, "highlight": False},
        {"label": "Blocks", "avg": team_stats.avg_blocks_favour, "tot": team_stats.acc_blocks_favour,
         "highlight": False},
        {"label": "PIR", "avg": team_stats.avg_valuation, "tot": team_stats.acc_valuation, "highlight": True},
    ]

    if not team:
        abort(404)

        # # Roster - igrači i treneri iz view-a
        # roster = session.execute(
        #     text("""
        #          SELECT *
        #          FROM vw_team_roster
        #          WHERE team_code = :team_code
        #            AND season_code = :season_code
        #          ORDER BY position
        #          """),
        #     {"team_code": team_code, "season_code": season_code}
        # ).fetchall()
        #
        # # Games - utakmice tima iz view-a
        # games = session.execute(
        #     text("""
        #          SELECT *
        #          FROM vw_team_games
        #          WHERE team_code = :team_code
        #            AND season_code = :season_code
        #          ORDER BY game_date
        #          """),
        #     {"team_code": team_code, "season_code": season_code}
        # ).fetchall()

    return render_template(
        "pages/team_details.html",
        team=team,
        teams_sidebar=teams_sidebar,
        # season={"code": season_code},
        roster=roster,
        coaches = coaches,
        grouped_roster=grouped_roster,
        position_order=position_order,
        # coaches=[p for p in roster if p.role and 'Coach' in p.role],
        next_game = next_game,
        results=results,
        upcoming=upcoming,
        games=games,
        team_stats = team_stats,
        players_stats = players_stats,
        team_stats_list=team_stats_list
        )

@app.route("/player/<person_code>")
def player_profile(person_code):

    season = request.args.get("season", "E2025")  # default sezona
    player_stats = get_player_stats(season, person_code)
    player_stats_list = [
        {"label": "Points", "avg": player_stats.avg_points, "tot": player_stats.acc_points, "highlight": False},
        {"label": "Rebounds", "avg": player_stats.avg_total_rebounds, "tot": player_stats.acc_total_rebounds,
         "highlight": False},
        {"label": "Assists", "avg": player_stats.avg_assistances, "tot": player_stats.acc_assistances,
         "highlight": False},
        {"label": "Steals", "avg": player_stats.avg_steals, "tot": player_stats.acc_steals, "highlight": False},
        {"label": "Blocks", "avg": player_stats.avg_blocks_favour, "tot": player_stats.acc_blocks_favour,
         "highlight": False},
        {"label": "PIR", "avg": player_stats.avg_valuation, "tot": player_stats.acc_valuation, "highlight": True},
    ]
    return render_template("pages/player.html",
                           player = player_stats,
                           player_stats_list = player_stats_list,
                           season=season)


@main_bp.route("/players")
def players():
    # default sezona ili iz query parametra
    season_code = request.args.get("season", "E2025")

    # sve dostupne sezone za dropdown
    listseasons = get_seasons(COMPETITION_CODE)
    seasons = [{"code": r.season_code, "label": r.season_info_alias} for r in listseasons]

    # igrači za sezonu
    players_list = get_players_by_season(season_code)  # vraca listu objekata
    # sortiramo po prezimenu (azbučno)
    teams_sidebar = get_clubsbyseasoncode(season_code)
    return render_template(
        "pages/players.html",
        teams_sidebar=teams_sidebar,
        players=players_list,
        selected_season=season_code,
        seasons=seasons
    )
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
