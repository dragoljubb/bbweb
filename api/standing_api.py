from api.session import session, sleep_safe
from config.settings import BASE_URL

def fetch_standing(round, compcode, season_year):
    season_code = f"{compcode}{season_year}"
    url = f"{BASE_URL}/v3/competitions/{compcode}/seasons/{season_code}/rounds/{round}/basicstandings"
    resp = session.get(url, timeout=(5,15))
    if resp.status_code == 200:
        sleep_safe()
        return resp.json()
    return None