"""
page_builder.py — renders the morning briefing as a standalone HTML page.
Saved to docs/index.html which GitHub Pages serves as a website.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from config.settings import OUTPUT_FILE, TOPICS


TOPIC_COLORS = {
    "green":  {"tag": "#1a2e1a", "text": "#4caf7d", "bar": "#2d5a2d"},
    "blue":   {"tag": "#1a1f2e", "text": "#5b8adb", "bar": "#1f2d4a"},
    "amber":  {"tag": "#2e2210", "text": "#d4933a", "bar": "#4a3010"},
    "purple": {"tag": "#1e1a2e", "text": "#9b7fd4", "bar": "#2d1f4a"},
}


def _topic_color(topic):
    color = topic.get("tag_color", "blue")
    return TOPIC_COLORS.get(color, TOPIC_COLORS["blue"])


def _get_topic_meta(topic_name):
    for t in TOPICS:
        if t["name"] == topic_name:
            return t
    return {"tag_color": "blue"}


def build_page(summarised_articles):
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%A, %-d %B %Y")
    time_str = now.strftime("%H:%M UTC")
    total = sum(len(v) for v in summarised_articles.values())

    topic_names = list(summarised_articles.keys())

    sections_html = ""
    for topic_name, articles in summarised_articles.items():
        if not articles:
            continue
        meta = _get_topic_meta(topic_name)
        colors = _topic_color(meta)
        slug = topic_name.lower().replace(" ", "-").replace("&", "and")

        cards_html = ""
        for i, article in enumerate(articles):
            featured = "card--featured" if i == 0 else ""
            digest = article.get("digest", article.get("summary", ""))
            cards_html += f"""
            <a class="card {featured}" href="{article['url']}" target="_blank" rel="noopener" data-topic="{slug}">
              <div class="card__source">{article['source']}</div>
              <div class="card__title">{article['title']}</div>
              <div class="card__body">{digest}</div>
              <div class="card__tag" style="background:{colors['tag']};color:{colors['text']};">{topic_name}</div>
            </a>"""

        sections_html += f"""
        <section class="section" id="{slug}">
          <div class="section__header" style="border-left:3px solid {colors['text']};">
            <span class="section__title">{topic_name}</span>
            <span class="section__count">{len(articles)} stories</span>
          </div>
          <div class="grid">{cards_html}</div>
        </section>"""

    nav_items = '<button class="nav__pill nav__pill--active" onclick="filterTopic(\'all\', this)">All</button>'
    for name in topic_names:
        slug = name.lower().replace(" ", "-").replace("&", "and")
        nav_items += f'<button class="nav__pill" onclick="filterTopic(\'{slug}\', this)">{name}</button>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Morning Briefing — {date_str}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg: #0a0a0a;
      --bg2: #111;
      --bg3: #161616;
      --border: #1e1e1e;
      --border2: #282828;
      --text: #e0e0e0;
      --text2: #888;
      --text3: #555;
      --accent: #fff;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 14px; line-height: 1.6; min-height: 100vh; }}

    /* Masthead */
    .masthead {{ position: sticky; top: 0; z-index: 100; background: var(--bg); border-bottom: 1px solid var(--border); padding: 14px 32px; display: flex; align-items: center; justify-content: space-between; backdrop-filter: blur(8px); }}
    .masthead__title {{ font-size: 12px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--accent); }}
    .masthead__right {{ display: flex; align-items: center; gap: 20px; }}
    .masthead__date {{ font-size: 12px; color: var(--text2); }}
    .masthead__count {{ font-size: 11px; color: var(--text3); background: var(--bg3); border: 1px solid var(--border); padding: 3px 10px; border-radius: 20px; }}

    /* Nav */
    .nav {{ padding: 0 32px; border-bottom: 1px solid var(--border); display: flex; gap: 0; overflow-x: auto; scrollbar-width: none; }}
    .nav::-webkit-scrollbar {{ display: none; }}
    .nav__pill {{ background: none; border: none; border-bottom: 2px solid transparent; color: var(--text3); font-size: 11px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; padding: 12px 16px; cursor: pointer; white-space: nowrap; transition: color 0.15s, border-color 0.15s; }}
    .nav__pill:hover {{ color: var(--text); }}
    .nav__pill--active {{ color: var(--accent); border-bottom-color: var(--accent); }}

    /* Content */
    .content {{ max-width: 1100px; margin: 0 auto; padding: 32px; }}

    /* Section */
    .section {{ margin-bottom: 48px; }}
    .section__header {{ display: flex; align-items: baseline; justify-content: space-between; padding-left: 12px; margin-bottom: 16px; }}
    .section__title {{ font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--text); }}
    .section__count {{ font-size: 11px; color: var(--text3); }}

    /* Grid */
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}

    /* Cards */
    .card {{ display: block; background: var(--bg2); border: 1px solid var(--border); border-radius: 6px; padding: 14px 16px; text-decoration: none; color: inherit; transition: border-color 0.15s, background 0.15s; cursor: pointer; }}
    .card:hover {{ border-color: var(--border2); background: var(--bg3); }}
    .card--featured {{ grid-column: 1 / -1; background: var(--bg3); border-color: var(--border2); }}
    .card--featured .card__title {{ font-size: 16px; }}
    .card--featured .card__body {{ font-size: 13px; color: var(--text2); -webkit-line-clamp: 6; }}
    .card__source {{ font-size: 10px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
    .card__title {{ font-size: 13px; font-weight: 600; color: var(--text); line-height: 1.4; margin-bottom: 8px; }}
    .card__body {{ font-size: 12px; color: var(--text3); line-height: 1.65; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden; }}
    .card__tag {{ display: inline-block; font-size: 10px; font-weight: 500; padding: 2px 8px; border-radius: 3px; letter-spacing: 0.3px; }}

    /* Footer */
    .footer {{ border-top: 1px solid var(--border); padding: 20px 32px; display: flex; justify-content: space-between; align-items: center; margin-top: 32px; }}
    .footer span {{ font-size: 11px; color: var(--text3); }}

    /* Hidden */
    .section--hidden {{ display: none; }}

    @media (max-width: 768px) {{
      .masthead, .nav, .content, .footer {{ padding-left: 16px; padding-right: 16px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .card--featured {{ grid-column: 1; }}
    }}
  </style>
</head>
<body>
  <header class="masthead">
    <span class="masthead__title">Morning Briefing</span>
    <div class="masthead__right">
      <span class="masthead__date">{date_str} &nbsp;·&nbsp; {time_str}</span>
      <span class="masthead__count">{total} stories</span>
    </div>
  </header>

  <nav class="nav">{nav_items}</nav>

  <main class="content">{sections_html}</main>

  <footer class="footer">
    <span>Curated by Claude · Powered by Anthropic</span>
    <span>Updated {time_str}</span>
  </footer>

  <script>
    function filterTopic(slug, btn) {{
      document.querySelectorAll('.nav__pill').forEach(p => p.classList.remove('nav__pill--active'));
      btn.classList.add('nav__pill--active');
      document.querySelectorAll('.section').forEach(s => {{
        if (slug === 'all' || s.id === slug) {{
          s.classList.remove('section--hidden');
        }} else {{
          s.classList.add('section--hidden');
        }}
      }});
    }}
  </script>
</body>
</html>"""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"  Page written to {OUTPUT_FILE}")
    return str(OUTPUT_FILE)
