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