def get_people_by_club(conn, club_code, season_year):
    """
    Vraća listu ljudi za dati klub i sezonu, uključujući image_url.
    Output: list of tuples -> (person_code, club_code, season_year, image_url)
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT person_code, club_code, season_year, images_action AS image_url
            FROM dwh.peoplebyseason
            WHERE club_code = %s
              AND season_year = %s
        """, (club_code, season_year))
        return cur.fetchall()

def get_players_by_club(conn, club_code, compcode,  season_year):
    """
    Vraća samo igrače (person_type = 'J')
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT person_code
            FROM dwh.peoplebyseason
            WHERE club_code = %s
              AND season_year = %s
                AND compcode = %s
              AND person_type = 'J'
                
        """, (club_code, season_year, compcode))
        return cur.fetchall()
