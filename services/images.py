import os
from api.session import session, sleep_safe

def save_person_image(person_code, club_code, image_url):
    path = f"STATIC/people/{club_code}"
    os.makedirs(path, exist_ok=True)
    file_path = f"{path}/{person_code}.jpg"
    if image_url and not os.path.exists(file_path):
        r = session.get(image_url, timeout=(5,15))
        r.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(r.content)
        sleep_safe()
