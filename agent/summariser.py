import anthropic
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def summarise_article(article):
    prompt = f"""Write a detailed 4-5 sentence news digest summary of this article.
Cover: what happened, who is involved, why it matters, and any key numbers or implications.
Be factual and direct. No fluff, no "In this article...". Write in plain prose, past tense.

Title: {article['title']}
Source: {article['source']}
Excerpt: {article['summary']}

Summary:"""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=350,
            messages=[{"role": "user", "content": prompt}]
        )
        article["digest"] = response.content[0].text.strip()
    except Exception as e:
        print(f"    Warning: summarisation failed for '{article['title']}': {e}")
        article["digest"] = article["summary"][:400]

    return article


def summarise_all(filtered_articles):
    for topic_name, articles in filtered_articles.items():
        print(f"  Summarising {len(articles)} articles for: {topic_name}")
        for article in articles:
            summarise_article(article)
    return filtered_articles
