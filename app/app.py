from flask import Flask, render_template, Blueprint, request
from models import get_current_round, get_upcoming_games, get_home_news, get_teams#, get_all_games

app = Flask(__name__)
main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def home():
    current_round = get_current_round("E", 2025)
    games = get_upcoming_games(current_round.round_id) if current_round else []
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
    round_type = request.args.get("round_type", default="RS")
    team = request.args.get("team")  # None ili ""

    selected_round = request.args.get("round", type=int)

    # -------------------------
    # Sidebar (grbovi timova)
    # -------------------------
    teams_sidebar = get_teams("E", season)

    # -------------------------
    # Zajednički podaci za filter bar
    # -------------------------
    seasons = get_seasons()           # lista sezona za combo
    round_types = get_round_types()   # RS / PO / FF
    teams = get_teams_by_season(season)  # lista timova za filter

    # -------------------------
    # Određivanje režima
    # -------------------------
    if not team:
        # -------- LEAGUE VIEW --------
        rounds = get_rounds(season, round_type)
        current_round = get_current_round("E", season, round_type)
        if not selected_round:
            selected_round = current_round

        games = get_games_by_round(season, round_type, selected_round)

        return render_template(
            "games.html",
            mode="LEAGUE",
            season=season,
            round_type=round_type,
            seasons=seasons,
            round_types=round_types,
            teams=teams,
            selected_team=None,
            rounds=rounds,
            current_round=current_round,
            selected_round=selected_round,
            games=games,
            teams_sidebar=teams_sidebar
        )

    else:
        # -------- TEAM VIEW --------
        next_game = get_next_game(season, round_type, team)
        results = get_results(season, round_type, team)
        upcoming = get_upcoming_games(season, round_type, team)

        return render_template(
            "games.html",
            mode="TEAM",
            season=season,
            round_type=round_type,
            seasons=seasons,
            round_types=round_types,
            teams=teams,
            selected_team=team,
            next_game=next_game,
            results=results,
            upcoming=upcoming,
            teams_sidebar=teams_sidebar
        )


# Registracija Blueprint-a
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
