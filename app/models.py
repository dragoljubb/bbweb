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
def get_current_round_phase(compcode: str):
    with SessionLocal() as session:
        result = session.execute(
            text("""
                SELECT *
                FROM dwh.vw_current_round
                WHERE compcode = :pcompcode;
                    
            """),
            {"pcompcode": compcode}
        ).first()
        return result  # ovo je SQLAlchemy Row object

def get_upcoming_games(round: int, season_code ):
    with SessionLocal() as session:
        result = session.execute(
            text("""
                SELECT *
                FROM dwh.vw_gamesinfo
                WHERE round = :pround AND season_code = :pseason_code 
                    ORDER BY game_date
            """),
            {"pround": round, "pseason_code":season_code }
        ).all()  #
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
            text("""SELECT  season_info_alias, season_code, season_year FROM dwh.vw_seasons 
                    WHERE compcode = :pcompcode 
                    ORDER BY season_info_alias DESC
            """), {"pcompcode": compcode}
        ).fetchall()
        return result
def get_phases(seasoncode: str):
    with SessionLocal() as session:
        result = session.execute(
            text("""SELECT * FROM dwh.vw_comp_phases 
                    WHERE season_code = :pseasoncode
                    ORDER BY default_order DESC
            """), {"pseasoncode": seasoncode}
        ).fetchall()
        return result


def get_rounds(seasoncode:str):
    with SessionLocal() as session:
        result = session.execute(
            text("""SELECT season_code, round, phase, round_name  FROM dwh.vw_rounds 
                    WHERE season_code = :pseason_code 
                    ORDER BY round 
            """), {"pseason_code":seasoncode}
        ).fetchall()
        return result

def get_clubsbyseasoncode(seasoncode :str):
    with SessionLocal() as session:
        result = session.execute(
            text("""SELECT * FROM dwh.vw_clubsbyseason 
                    WHERE season_code = :pseasoncode 
                    ORDER BY club_name
            """), {"pseasoncode": seasoncode}
        ).fetchall()
        return result

def get_current_season(compcode :str):
    with (SessionLocal() as session):
        result = session.execute(
            text("""SELECT * FROM dwh.vw_current_season
                    WHERE compcode = :pcompcode 
                    ORDER BY season_year DESC
            """), {"pcompcode": compcode }
        ).mappings(
        ).first()
        return result

def get_next_team_game(team_code :str, season_code:str) :
    with SessionLocal() as session:
        result = session.execute(
            text("""SELECT * FROM dwh.vw_gamesinfo 
                    WHERE season_code = :pseason_code 
                          AND played 
                          AND (home_code = :pteam_code 
                            OR away_code = :pteam_code)
                     ORDER BY game_date
                    LIMIT 1
                
            """), {"pteam_code": team_code, "pseason_code": season_code}
        ).fetchall()
        return result


def get_team_games(season_code, team_code):
    with SessionLocal() as session:
        result = session.execute(
            text("SELECT * FROM dwh.get_team_games(:team, :season)"),
            {"team": team_code, "season": season_code}
        ).mappings().all()
    return result

# standings

def get_available_rounds(season_code: str):
    with SessionLocal() as session:
        return session.execute(
            text("""
                SELECT DISTINCT round
                FROM dwh.vw_standings
                WHERE season_code = :pseason_code
                ORDER BY round
            """),
            {
                "pseason_code": season_code
            }
        ).fetchall()

def get_last_round(season_code: str):
    with SessionLocal() as session:
        return session.execute(
            text("""
                SELECT MAX(round) AS round
                FROM dwh.vw_standings
                WHERE season_code = :pseason_code
            """),
            {
                "pseason_code": season_code
            }
        ).fetchone()

def get_standings( season_code: str, round_: int):
    with SessionLocal() as session:
        return session.execute(
            text("""
                SELECT *
                FROM dwh.vw_standings
                WHERE season_code = :pseason_code
                  AND round = :pround
                ORDER BY team_position
            """),
            {
                "pseason_code": season_code,
                "pround": round_
            }
        ).fetchall()

def get_clubbyseason_team_details(season_code: str, club_code: str):
    with SessionLocal() as session:
        result = session.execute(
            text(""" SELECT season_code, club_code, club_name, city, address, country_name, website, president, phone, crest_url, club_tv_code, arena_code, arena_name, tickets_url, twitter_account, club_info 
                    FROM   dwh.vw_clubsbyseason_team_details
                 WHERE club_code = :pclub_code
                   AND season_code = :pseason_code
            """), {"pclub_code": club_code, "pseason_code": season_code}
        ).mappings().fetchone()
        return result

def get_roster(season_code: str, club_code: str):
    with SessionLocal() as session:
        result = session.execute(
            text(""" SELECT person_code,  club_code, season_code, person_type, active, position_name, dorsal,  first_name, last_name,  height, 
                        weight, birth_date, formatted_date,  country_code, country_name, twitter_account, facebook_account, 
                        instagram_account,  last_team
                    FROM dwh.vw_person
                    WHERE club_code = :pclub_code
                   AND season_code = :pseason_code
                    AND active = true AND person_type = 'J';
            """), {"pclub_code": club_code, "pseason_code": season_code}
        ).fetchall()
        return result

def get_coaches(season_code: str, club_code: str):
    with SessionLocal() as session:
        result = session.execute(
            text(""" SELECT person_code,  person_type_name, club_code, season_code, person_type, active, position_name, dorsal,  first_name, last_name,  height, 
                        weight, birth_date, formatted_date,  country_code, country_name, twitter_account, facebook_account, 
                        instagram_account,  last_team
                    FROM dwh.vw_person
                    WHERE club_code = :pclub_code
                   AND season_code = :pseason_code
                    AND active = true AND person_type IN ('A','E' )
                ORDER BY person_type DESC, last_name
            """), {"pclub_code": club_code, "pseason_code": season_code}
        ).fetchall()
        return result

def get_team_stats(season_code: str, club_code: str):
    with SessionLocal() as session:
        result = session.execute(
            text(""" SELECT person_code, club_code, season_code,
                            acc_games_played,
	                        avg_games_played,
	                        acc_time_played,
 	                        avg_time_played,
                            avg_points, acc_points,
                            acc_fg2_num, acc_fg2_txt, acc_fg3_num, acc_fg3_txt, acc_ft_num, acc_ft_txt, 
                            avg_fg2_num, avg_fg2_txt, avg_fg3_num, avg_fg3_txt, avg_ft_num, avg_ft_txt,
                            avg_offensive_rebounds, acc_offensive_rebounds, avg_defensive_rebounds, acc_defensive_rebounds, 
                            avg_total_rebounds, acc_total_rebounds, avg_assistances, acc_assistances, avg_steals, 
                            acc_steals, avg_blocks_favour, acc_blocks_favour, avg_blocks_against, 
                            acc_blocks_against, avg_fouls_commited, acc_fouls_commited, avg_fouls_received, 
                            acc_fouls_received, avg_valuation, acc_valuation
                     FROM dwh.vw_team_stats
                     WHERE club_code = :pclub_code
                       AND season_code = :pseason_code
                 """), {"pclub_code": club_code, "pseason_code": season_code}
        ).mappings().first()
        return result

def get_player_acc_stats(season_code: str, club_code: str):
    with SessionLocal() as session:
        result = session.execute(
            text(""" SELECT person_code, dorsal, season_code, club_code, acc_points, acc_assists, acc_rebounds_total, acc_rebounds_defensive, acc_rebounds_offensive, acc_steals, acc_blocks_favour, acc_blocks_against, acc_turnovers, acc_fouls_commited, acc_fouls_received, acc_plus_minus, acc_valuation, acc_time_played_sec, acc_games_played, acc_games_started, acc_total_games_started, acc_fg2_made, acc_fg3_made, acc_fg2_attempted, acc_fg3_attempted, acc_fg_made_total, acc_fg_attempted_total, acc_ft_made, acc_ft_attempted, acc_accuracy_made, acc_accuracy_attempted, acc_pct_2p, acc_pct_3p, acc_pct_ft, acc_fg2_num, acc_fg2_txt, acc_fg3_num, acc_fg3_txt, acc_ft_num, acc_ft_txt, person_name
	                FROM dwh.vw_person_acc_stats
                    WHERE club_code = :pclub_code
                    AND season_code = :pseason_code
                    ORDER BY CAST (dorsal as int)
            """), {"pclub_code": club_code, "pseason_code": season_code}
        ).fetchall()
        return result
