from flask import Flask, render_template, Blueprint
from models import get_current_round, get_upcoming_games, get_latest_news, get_teams



app = Flask(__name__)
main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def home():
    current_round = get_current_round("E", 2025)
    games = get_upcoming_games(current_round.round_id) if current_round else []
    news = get_latest_news()
    teams_sidebar = get_teams("E", 2025)
    return render_template('home.html',
                           current_round=current_round,
                           games=games,
                           news=news,
                           teams_sidebar=teams_sidebar)

# Registracija Blueprint-a
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
