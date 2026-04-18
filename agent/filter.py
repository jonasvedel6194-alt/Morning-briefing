import json
import anthropic
from config.settings import ANTHROPIC_API_KEY, TOPICS, CLAUDE_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _score_articles_for_topic(articles, topic):
    if not articles:
        return []

    article_list = "\n".join(
        f"[{i}] {a['title']} — {a['source']}\n    {a['summary'][:200]}"
        for i, a in enumerate(articles)
    )

    prompt = f"""You are a news curator. Score each article for relevance to the topic:

TOPIC: {topic['name']}
DESCRIPTION: {topic['description']}

ARTICLES:
{article_list}

Return ONLY a JSON array with one object per article, in order:
[{{"index": 0, "score": 8, "reason": "directly about renewable energy policy"}}]

Score 0-10. Score 0 if not about this topic at all. Be strict."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        scores = json.loads(raw.strip())
        return [(articles[s["index"]], s["score"]) for s in scores if s["score"] >= 6]
    except Exception as e:
        print(f"    Warning: scoring failed for topic '{topic['name']}': {e}")
        return [(a, 5) for a in articles[:topic["max_articles"]]]


def filter_and_rank(articles):
    results = {}
    used_urls = set()

    for topic in TOPICS:
        print(f"  Scoring articles for topic: {topic['name']}")

        # Only consider articles not already assigned to a previous topic
        available = [a for a in articles if a["url"] not in used_urls]
        scored = _score_articles_for_topic(available, topic)
        scored.sort(key=lambda x: x[1], reverse=True)
        top = [article for article, score in scored[:topic["max_articles"]]]

        # Lock these URLs so they can't appear in later topics
        for article in top:
            used_urls.add(article["url"])

        results[topic["name"]] = top
        print(f"    Selected {len(top)} articles")

    return results
