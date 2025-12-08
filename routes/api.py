from flask import Blueprint, jsonify, request
from app import db
from app.models.games import Game
from app.models.news import News
from app.models.teams import Team


api_bp = Blueprint("api", __name__)


@api_bp.get('/health')
def health():
    return jsonify({"status": "ok"})

@api_bp.get('/games')
def get_games():
    # query params: upcoming=true
    upcoming = request.args.get('upcoming', 'false').lower() in ('1', 'true', 'yes')
    q = Game.query
    if upcoming:
        q = q.filter(Game.date_utc >= db.func.now())
        games = q.order_by(Game.date_utc).limit(200).all()
        return jsonify([g.to_dict() for g in games])

@api_bp.get('/games/<int:game_id>')
def get_game(game_id):
    g = Game.query.get_or_404(game_id)
    return jsonify(g.to_dict())

@api_bp.get('/news')
def get_news():
    q = News.query.order_by(News.published_at.desc())
    limit = min(int(request.args.get('limit', 20)), 200)
    items = q.limit(limit).all()
    return jsonify([n.to_dict() for n in items])

@api_bp.get('/teams')
def get_teams():
    teams = Team.query.order_by(Team.name).all()
    return jsonify([t.to_dict() for t in teams])