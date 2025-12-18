from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
from sqlalchemy import text

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
    newstitle = Column(String)
    newslead = Column(String)
    image_url = Column(String)
    created = Column(DateTime)

class HomeNews(Base):
    __tablename__ = "vw_news_home"
    __table_args__ = {"schema": "dwh"}

    id = Column(Integer, primary_key=True)
    newstitle = Column(String)
    newslead = Column(String)
    newscontent = Column(String)
    image_url = Column(String)
    created = Column(DateTime)

# =================== Data fetching functions ===================
def get_current_round(compcode: str, season_year: int):
    with SessionLocal() as session:
        result = session.execute(
            text("""
                SELECT *
                FROM dwh.vw_current_round
                WHERE compcode = :pcompcode
                  AND season_year = :pseason_year
                    
            """),
            {"pcompcode": compcode, "pseason_year": season_year}
        ).first()
        return result  # ovo je SQLAlchemy Row object

def get_upcoming_games(round: int, season_year: int, compcode : str ):
    with SessionLocal() as session:
        result = session.execute(
            text("""
                SELECT *
                FROM dwh.vw_gamesinfo
                WHERE round = :pround AND season_year = :pseason_year 
                    AND compcode = :pcompcode
                    ORDER BY game_date
            """),
            {"pround": round, "pseason_year":season_year,  "pcompcode": compcode }
        ).fetchall()  # fetchall vraća listu Row objekata
        return result

def get_latest_news(limit=6):
    session = SessionLocal()
    try:
        news = session.query(News).order_by(News.created.desc()).limit(limit).all()
        return news
    finally:
        session.close()

def get_home_news():
    session = SessionLocal()
    try:
        news = session.query(HomeNews).all()

        main_news = news[0] if news else None
        slider_news = news[1:]  # max 5

        return main_news, slider_news
    finally:
        session.close()

def get_teams(compcode: str, season_year: int):
    with SessionLocal() as session:
        result = session.execute(
            text("""
                SELECT *
                FROM dwh.vw_teams_sidebar
                WHERE compcode = :pcompcode
                  AND season_year = :pseason_year
            """),
            {"pcompcode": compcode, "pseason_year": season_year}
        ).fetchall()
        return result
def get_seasons(compcode: str):
    with SessionLocal() as session:
        result = session.execute(
            text("""SELECT * FROM dwh.vw_seasons WHERE compcode = :pcompcode ORDER BY season_year DESC
            """), {"pcompcode": compcode}
        ).fetchall()
        return result
def get_phases(compcode: str):
    with SessionLocal() as session:
        result = session.execute(
            text("""SELECT * FROM dwh.vw_comp_phases 
                    WHERE compcode = :pcompcode 
                    ORDER BY default_order DESC
            """), {"pcompcode": compcode}
        ).fetchall()
        return result


def get_rounds(compcode: str, phase:str, season_year: int):
    with SessionLocal() as session:
        result = session.execute(
            text("""SELECT * FROM dwh.vw_rounds 
                    WHERE compcode = :pcompcode 
                          AND phase = :pphase
                          AND season_year = :pseason_year
                    ORDER BY round 
            """), {"pcompcode": compcode, "pphase": phase, "pseason_year": season_year }
        ).fetchall()
        return result

def get_clubsbycompcodeseason(compcode :str, season_year: int):
    with SessionLocal() as session:
        result = session.execute(
            text("""SELECT * FROM dwh.vw_clubsbyseason 
                    WHERE compcode = :pcompcode 
                          AND season_year = :pseason_year
                    ORDER BY club_name
            """), {"pcompcode": compcode,  "pseason_year": season_year }
        ).fetchall()
        return result



