import os
import requests
from sqlalchemy import create_engine, text

# ---- Config ----
DB_URL = "postgresql+psycopg2://user:password@localhost/dbname"
STATIC_LOGO_PATH = "static/logos"  # folder gde ce se cuvati grbovi
os.makedirs(STATIC_LOGO_PATH, exist_ok=True)

# ---- DB session ----
engine = create_engine(DB_URL)

with engine.connect() as conn:
    # Dohvati sve timove i njihove grbove
    teams = conn.execute(text("SELECT code, crest FROM vw_team_info")).fetchall()

    for team in teams:
        code = team.code
        url = team.crest
        if not url:
            continue  # preskoci ako nema URL

        # lokalni fajl
        ext = os.path.splitext(url)[-1].split("?")[0]  # čisti query parametre
        filename = f"{code}{ext}"
        filepath = os.path.join(STATIC_LOGO_PATH, filename)

        # preuzimanje slike
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                print(f"Grb sačuvan: {filename}")
            else:
                print(f"Greška: {url} status {resp.status_code}")
        except Exception as e:
            print(f"Ne mogu da skinem {url}: {e}")
