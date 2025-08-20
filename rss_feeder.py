import feedparser
import requests
from datetime import date

# ==== CONFIG ====
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

RSS_FEEDS = {
    "TechCrunch AI": "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "MIT Technology Review": "https://www.technologyreview.com/feed/"
}
NUM_ARTICLES_PER_FEED = 3
TOTAL_NUM_ARTICLES = 15
# ===============

def fetch_rss_articles():
    articles_by_feed = {}
    headers = {'User-Agent': 'Mozilla/5.0'}
    for feed_name, feed_url in RSS_FEEDS.items():
        response = requests.get(feed_url, headers=headers)
        feed = feedparser.parse(response.content)
        articles = []
        for entry in feed.entries[:NUM_ARTICLES_PER_FEED]:
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": summary[:250]  # truncate
            })
        articles_by_feed[feed_name] = articles
    return articles_by_feed

def post_to_slack(articles_by_feed):
    message_lines = [f"🤖 *Daily AI & Tech Brief – {date.today().strftime('%b %d, %Y')}*\n"]
    for feed_name, articles in articles_by_feed.items():
        message_lines.append(f"📌 *{feed_name}*")
        for a in articles:
            message_lines.append(f"• <{a['link']}|{a['title']}>")
            if a['summary']:
                message_lines.append(f"   _{a['summary']}_")
        message_lines.append("")  # extra line between feeds
    payload = {"text": "\n".join(message_lines)}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    articles_by_feed = fetch_rss_articles()
    post_to_slack(articles_by_feed)
