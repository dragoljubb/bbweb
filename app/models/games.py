from app import db


class Game(db.Model):
    __tablename__ = 'games'
    __table_args__ = {'schema': 'dwh'}


id = db.Column(db.Integer, primary_key=True)
season = db.Column(db.String(32), nullable=True)
round = db.Column(db.Integer, nullable=True)
home_team = db.Column(db.String(128), nullable=False)
away_team = db.Column(db.String(128), nullable=False)
date_utc = db.Column(db.DateTime, nullable=False)
arena = db.Column(db.String(128), nullable=True)
created_at = db.Column(db.DateTime, server_default=db.func.now())


def to_dict(self):
    return {
    "game_id": self.id,
    "season": self.season,
    "round": self.round,
    "home": self.home_team,
    "away": self.away_team,
    "date": self.date_utc.isoformat() if self.date_utc else None,
    "arena": self.arena
    }