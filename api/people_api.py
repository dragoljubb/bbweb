from api.session import session, sleep_safe
from config.settings import BASE_URL

def fetch_person_bio(person_code):
    url = f"{BASE_URL}/v2/people/{person_code}/bio"
    resp = session.get(url, timeout=(5,15))
    if resp.status_code == 200:
        sleep_safe()
        return resp.json()
    return None

def fetch_person_stats(person_code, club_code, compcode, season):
    season_code =f"{compcode}{season}"
    url = f"{BASE_URL}/v2/competitions/{compcode}/seasons/{season_code}/clubs/{club_code}/people/{person_code}/stats"
    resp = session.get(url, timeout=(5,15))
    if resp.status_code == 200:
        sleep_safe()
        return resp.json()
    return None

def fetch_person_careerhighs(person_code, compcode):
    url = f"{BASE_URL}/v2/competitions/{compcode}/people/{person_code}/careerhighs"
    resp = session.get(url, timeout=(5,15))
    if resp.status_code == 200:
        sleep_safe()
        return resp.json()
    return None

def fetch_team_stats(compcode, season_year, club_code):
    season_code = f"{compcode}{season_year}"
    url = f"{BASE_URL}/v2/competitions/{compcode}/seasons/{season_code}/clubs/{club_code}/stats"
    resp = session.get(url, timeout=(5,15))
    if resp.status_code == 200:
        sleep_safe()
        return resp.json()
    return None

