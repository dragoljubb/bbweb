from flask import Flask, render_template, Blueprint, request
from models import (get_current_round, get_upcoming_games,
                    get_home_news, get_teams, get_seasons,
                    get_phases, get_rounds, get_clubsbycompcodeseason)#, get_all_games

app = Flask(__name__)
main_bp = Blueprint('main_bp', __name__)
def_compcode = "E"
def_season_year = 2025
@main_bp.route('/')
def home():
    current_round = get_current_round("E", 2025)
    games = get_upcoming_games(current_round.round, def_season_year,def_compcode) if current_round else []
    main_news, slider_news = get_home_news()
    teams_sidebar = get_teams("E", 2025)
    return render_template('home.html',
                           current_round=current_round,
                           games=games,
                           main_news=main_news,
                           slider_news=slider_news,
                           teams_sidebar=teams_sidebar)

# ===========================
# Games page
# ===========================
@main_bp.route('/games')
def games():
    # -------------------------
    # PARAMETRI (query string)
    # -------------------------
    season = request.args.get("season", default=2025, type=int)
    season = request.args.get("season")
    if season is None:
        season = "2025-26"
    phase = request.args.get("phase", default="RS")
    team = request.args.get("team")  # None ili ""

    selected_round = request.args.get("round", type=int)

    # -------------------------
    # Sidebar (grbovi timova)
    # -------------------------
    teams_sidebar = get_teams("E", season)

    # -------------------------
    # Zajednički podaci za filter bar
    # -------------------------
    listseasons = get_seasons(def_compcode)           # lista sezona za combo
    seasons = [row.season_info_alias for row in listseasons]
    phases = get_phases(def_compcode)   # RS / PO / FF
    teams = get_clubsbycompcodeseason(def_compcode, season)  # lista timova za filter

    # -------------------------
    # Određivanje režima
    # -------------------------
    if not team:
        # -------- LEAGUE VIEW --------
        rounds = get_rounds(def_compcode, phase, season)
        current_round = get_current_round("E", season)
        if not selected_round:
            selected_round = current_round

        games = get_upcoming_games(selected_round.round, season, def_compcode)

        return render_template(
            "games.html",
            mode="LEAGUE",
            season=season,
            phase=phase,
            seasons=seasons,
            phases=phases,
            teams=teams,
            selected_team=None,
            rounds=rounds,
            current_round=current_round,
            selected_round=selected_round,
            games=games,
            teams_sidebar=teams_sidebar
        )

    else:
        return render_template(
            "games.html",
            mode="LEAGUE",
            season=season,
            phase=phase,
            seasons=seasons,
            phases=phases,
            teams=teams,
            selected_team=None,
            #rounds=rounds,
         #   current_round=current_round,
            selected_round=selected_round,
          #  games=games,
            teams_sidebar=teams_sidebar
        )

        # -------- TEAM VIEW --------
        # next_game = get_next_game(season, round_type, team)
        # results = get_results(season, round_type, team)
        # upcoming = get_upcoming_games(season, round_type, team)
        #
        # return render_template(
        #     "games.html",
        #     mode="TEAM",
        #     season=season,
        #     round_type=round_type,
        #     seasons=seasons,
        #     round_types=round_types,
        #     teams=teams,
        #     selected_team=team,
        #     next_game=next_game,
        #     results=results,
        #     upcoming=upcoming,
        #     teams_sidebar=teams_sidebar
        # )


# Registracija Blueprint-a
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
