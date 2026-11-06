import os
import json
import datetime
import feedparser
import google.generativeai as genai

RSS_FEEDS = [
    "https://niebezpiecznik.pl/feed/",
    "https://zaufanatrzeciastrona.pl/feed/",
    "https://justgeek.it/feed/",
    "https://www.crazynauka.pl/feed/",
    "https://naukatolubie.pl/feed/",
    "https://forbot.pl/blog/feed",
    "https://majsterkowo.pl/feed/",
    "https://subiektywnieofinansach.pl/feed/",
    "https://jakoszczedzacpieniadze.pl/feed"
]

CATEGORIES = ["Technologia", "Nauka", "Majsterkowanie", "Finanse"]

def fetch_rss_candidates():
    candidates = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:4]:
                candidates.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": getattr(entry, 'summary', '')
                })
        except Exception as e:
            print(f"Błąd przy pobieraniu {feed_url}: {e}")
    return candidates

def run_agent():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Brak GEMINI_API_KEY w secretach!")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    json_path = "data/links.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            existing_links = json.load(f)
    else:
        existing_links = []

    existing_urls = {link["url"] for link in existing_links}
    candidates = fetch_rss_candidates()
