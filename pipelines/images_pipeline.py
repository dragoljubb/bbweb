import os
from api.session import session, sleep_safe
from pipelines.helpers import get_people_by_club

def save_person_image(person_code, club_code, image_url):
    """
    Čuva sliku igrača u app/static/people/{club_code}/{person_code}.jpg
    """
    import os

    # ide do project_root, jer run_images.py je u load/
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "app", "static", "people", club_code)
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f"{person_code}.jpg")

    if image_url and not os.path.exists(file_path):
        r = session.get(image_url, timeout=(5,15))
        r.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(r.content)
        sleep_safe()  # ban-safe delay

def run_images_pipeline(conn, club_code, season_year):
    """
    Pokreće preuzimanje slika za sve ljude iz datog kluba i sezone.
    """
    people = get_people_by_club(conn, club_code, season_year)
    for person_code, club_code, season_year, image_url in people:
        save_person_image(person_code, club_code, image_url)
