from flask import Flask, render_template, Blueprint, request
from models import (get_current_round_phase, get_upcoming_games,
                    get_home_news, get_teams, get_seasons,get_current_season,
                    get_phases, get_rounds, get_clubsbyseasoncode)#, get_all_games

app = Flask(__name__)
main_bp = Blueprint('main_bp', __name__)
COMPETITION_CODE = "E"
def_season_year = 2025
def_season_code = 'E2025'
@main_bp.route('/')
def home():
    current_round = get_current_round_phase(COMPETITION_CODE)
    games = get_upcoming_games(current_round.round, def_season_code) if current_round else []
    main_news, slider_news = get_home_news()

    teams_sidebar = get_clubsbyseasoncode(def_season_code)
    return render_template('home.html',
                           current_round=current_round,
                           games=games,
                           main_news=main_news,
                           slider_news=slider_news,
                           teams_sidebar=teams_sidebar)

# ===========================
# Games page
# ===========================
from flask import request, redirect, url_for

@app.route("/games")
def games():

    # -------------------------
    # 1. URL parametri (KANON)
    # -------------------------
    season = request.args.get("season")        # npr. "E2025"
    phase = request.args.get("phase", "RS")
    team = request.args.get("team")
    selected_round = request.args.get("round", type=int)

    # -------------------------
    # 2. Ako URL nije kompletan → redirect
    # -------------------------
    if not season or not selected_round:
        default_season_raw = get_current_season(COMPETITION_CODE) # "E2025"
        default_season = default_season_raw ["season_code"]
        default_round = get_current_round_phase(COMPETITION_CODE).round

        return redirect(
            url_for(
                "games",
                season=default_season,
                round=default_round,
                phase=phase
            )
        )
    # -------------------------
    # 3. UI podaci (label-e)
    # -------------------------
    listseasons = get_seasons(COMPETITION_CODE)
    seasons = [
        {
            "code": row.season_code,              # E2025
            "label": row.season_info_alias        # 2025-26
        }
        for row in listseasons
    ]


    listphases = get_phases(season)
    phases = [
        {
            "phase": row.phase
        }
        for row in listphases
    ]


    listteams = get_clubsbyseasoncode(season)
    teams = [
        {
            "crest": row.crest_url,
            "team_name": row.club_name,
            "code": row.club_code
        }
        for row in listteams
    ]

    teams_sidebar = get_clubsbyseasoncode(season)
    # -------------------------
    # 4. LEAGUE VIEW
    # -------------------------
    if not team:
        listrounds = get_rounds(season)
        rounds= [
            {
                "season_code": row.season_code,
                "round": row.round,
                "round_name": row.round_name,
                "phase": row.phase
            }
            for row in listrounds
        ]
        games = get_upcoming_games(selected_round, season)

        return render_template(
            "games.html",
            mode="LEAGUE",
            season=season,                 # E2025
            phase=phase,
            seasons=seasons,
            phases=phases,
            teams=teams,
            selected_team=None,
            rounds=rounds,
            selected_round=selected_round,
            games=games,
            teams_sidebar=teams_sidebar
        )

    # -------------------------
    # 5. TEAM VIEW (kasnije)
    # -------------------------
    return render_template(
        "games.html",
        mode="TEAM",
        season=season,
        phase=phase,
        seasons=seasons,
        phases=phases,
        teams=teams,

        selected_team=team,
        selected_round=selected_round,
        teams_sidebar=teams_sidebar
    )

app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
