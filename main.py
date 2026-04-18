"""
main.py — entry point. Fetches, filters, summarises, and builds the page.
"""

import sys
from agent.fetcher import fetch_all_articles
from agent.filter import filter_and_rank
from agent.summariser import summarise_all
from agent.page_builder import build_page


def run():
    print("=== Morning Briefing Agent starting ===\n")

    print("[1/4] Fetching articles from RSS feeds...")
    articles = fetch_all_articles()
    if not articles:
        print("No fresh articles found. Exiting.")
        sys.exit(0)

    print(f"\n[2/4] Filtering {len(articles)} articles by topic...")
    filtered = filter_and_rank(articles)
    total = sum(len(v) for v in filtered.values())
    if total == 0:
        print("No relevant articles after filtering. Exiting.")
        sys.exit(0)

    print(f"\n[3/4] Summarising {total} articles...")
    summarised = summarise_all(filtered)

    print("\n[4/4] Building briefing page...")
    path = build_page(summarised)

    print(f"\n=== Done. Page built: {path} ===")


if __name__ == "__main__":
    run()
