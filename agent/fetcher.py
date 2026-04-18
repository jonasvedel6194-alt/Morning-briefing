import feedparser
import requests
from datetime import datetime, timezone, timedelta
from config.settings import SOURCES, LOOKBACK_HOURS


def _parse_date(entry):
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def fetch_all_articles():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    seen_urls = set()
    articles = []

    for category, feeds in SOURCES.items():
        for feed in feeds:
            print(f"  Fetching: {feed['name']}")
            try:
                headers = {"User-Agent": "Mozilla/5.0 (compatible; NewsAgent/1.0)"}
                response = requests.get(feed["url"], headers=headers, timeout=15)
                parsed = feedparser.parse(response.content)
            except Exception as e:
                print(f"    Warning: could not fetch {feed['name']}: {e}")
                continue

            for entry in parsed.entries:
                url = entry.get("link", "")
                if not url or url in seen_urls:
                    continue
                published = _parse_date(entry)
                if published < cutoff:
                    continue
                seen_urls.add(url)
                articles.append({
                    "title": entry.get("title", "Untitled").strip(),
                    "url": url,
                    "source": feed["name"],
                    "category": category,
                    "published": published.isoformat(),
                    "summary": entry.get("summary", "")[:500],
                })

    print(f"  Total fresh articles found: {len(articles)}")
    return articles
