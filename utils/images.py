import os
from flask import current_app, url_for

def team_logo(team_code: str):
    """
    Vraća lokalni logo ako postoji,
    u suprotnom placeholder.
    """
    logos_dir = os.path.join(
        current_app.root_path, "static", "logos"
    )

    filename = f"{team_code}.png"
    filepath = os.path.join(logos_dir, filename)

    if os.path.exists(filepath):
        return url_for("static", filename=f"logos/{filename}")

    return url_for("static", filename="logos/placeholder.png")

def news_image(news_id: int):
    """
    Vrati lokalni path do slike vesti.
    Ako ne postoji, vrati placeholder.
    """
    filename = f"{news_id}.png"
    path = f"static/news/{filename}"

    if os.path.exists(path):
        return url_for("static", filename=f"news/{filename}")
    else:
        return url_for("static", filename="news/news_placeholder.png")
