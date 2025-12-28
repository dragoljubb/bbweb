import requests, time, random

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.euroleaguebasketball.net/"
})

def sleep_safe():
    """Ban-safe sleep između poziva"""
    time.sleep(random.uniform(1.5, 3.0))
