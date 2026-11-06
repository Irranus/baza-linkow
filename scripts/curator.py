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
    model = genai.GenerativeModel("gemini-2.5-flash")

    json_path = "data/links.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            existing_links = json.load(f)
    else:
        existing_links = []

    existing_urls = {link["url"] for link in existing_links}
    candidates = fetch_rss_candidates()
    fresh_candidates = [c for c in candidates if c["link"] not in existing_urls]

    if not fresh_candidates:
        print("Brak nowych unikalnych artykułów.")
        return

    prompt = f"""
    Jesteś kuratorem treści. Z listy kandydatów wybierz po 2 najciekawsze artykuły dla każdej z kategorii: {json.dumps(CATEGORIES, ensure_ascii=False)}.
    
    Kandydaci:
    {json.dumps(fresh_candidates, ensure_ascii=False)}

    Format odpowiedzi (wyłącznie czysty JSON bez markdown):
    [
      {{
        "title": "Tytuł po polsku",
        "url": "Link",
        "category": "Kategoria z listy",
        "summary": "2-3 zdaniowy opis własnymi słowami"
      }}
    ]
    """

    response = model.generate_content(prompt)
    clean_json_str = response.text.strip().replace("```json", "").replace("```", "")
    new_articles = json.loads(clean_json_str)

    today_str = datetime.date.today().isoformat()

    for i, item in enumerate(new_articles):
        new_entry = {
            "id": f"{today_str}-{i+1}",
            "title": item["title"],
            "url": item["url"],
            "category": item["category"],
            "summary": item["summary"],
            "date": today_str
        }
        existing_links.insert(0, new_entry)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(existing_links, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_agent()
