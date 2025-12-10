from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

# =================== Database setup ===================
DATABASE_URL = "postgresql+psycopg2://user_view:2222@localhost:5432/bb_test"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =================== Models ===================
class Round(Base):
    __tablename__ = "rounds"
    __table_args__ = {"schema": "dwh"}

    id = Column(Integer, primary_key=True)
    round_name = Column(String)
    round_index = Column(Integer)
    id_seasons = Column(Integer)
    phase= Column(String)
    min_game_start = Column(DateTime)
    max_game_start = Column(DateTime)

class Team(Base):
    __tablename__ = "teams"
    __table_args__ = {"schema": "dwh"}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    logo_url = Column(String)

class Game(Base):
    __tablename__ = "games"
    __table_args__ = {"schema": "dwh"}

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey("dwh.rounds.id"))
    teamA_id = Column(Integer, ForeignKey("dwh.teams.id"))
    teamB_id = Column(Integer, ForeignKey("dwh.teams.id"))
    game_date = Column(DateTime)

    teamA = relationship("Team", foreign_keys=[teamA_id])
    teamB = relationship("Team", foreign_keys=[teamB_id])
    round = relationship("Round")

class News(Base):
    __tablename__ = "news"
    __table_args__ = {"schema": "dwh"}

    id = Column(Integer, primary_key=True)
    title = Column(String)
    lead = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime)

# =================== Data fetching functions ===================
def get_current_round():
    session = SessionLocal()
    try:
        today = datetime.today()
        round_ = session.query(Round).filter(
            Round.min_game_start <= today,
            Round.max_game_start >= today
        ).first()
        return round_
    finally:
        session.close()

def get_upcoming_games(round_id):
    session = SessionLocal()
    try:
        today = datetime.today()
        games = session.query(Game).filter(
            Game.round_id == round_id,
            Game.game_date >= today
        ).order_by(Game.game_date).all()
        return games
    finally:
        session.close()

def get_latest_news(limit=6):
    session = SessionLocal()
    try:
        news = session.query(News).order_by(News.created_at.desc()).limit(limit).all()
        return news
    finally:
        session.close()

def get_teams():
    session = SessionLocal()
    try:
        teams = session.query(Team).order_by(Team.name).all()
        return teams
    finally:
        session.close()
