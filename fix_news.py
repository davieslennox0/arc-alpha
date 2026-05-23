with open("scout_skill.py") as f:
    content = f.read()

old = '''def fetch_news(topic: str) -> list:
    """Fetch recent news headlines for a topic."""
    try:
        r = requests.get(
            "https://newsdata.io/api/1/news",
            params={
                "apikey": os.getenv("NEWSDATA_API_KEY", ""),
                "q": topic,
                "language": "en",
                "size": 5
            },
            timeout=8
        )
        articles = r.json().get("results", [])
        return [a.get("title", "") for a in articles[:5]]
    except:
        # Fallback to free RSS
        try:
            r = requests.get(
                f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={topic}&region=US&lang=en-US",
                timeout=8
            )
            import re
            titles = re.findall(r'<title>(.*?)</title>', r.text)[2:7]
            return titles
        except:
            return []'''

new = '''def fetch_news(topic: str) -> list:
    """Fetch recent news headlines using free RSS feeds."""
    import re
    headlines = []
    
    feeds = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={topic.replace(' ','+')}&region=US&lang=en-US",
        f"https://news.google.com/rss/search?q={topic.replace(' ','+')}&hl=en-US&gl=US&ceid=US:en",
        "https://feeds.feedburner.com/CoinDesk",
    ]
    
    for feed_url in feeds:
        try:
            r = requests.get(feed_url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', r.text)
            if not titles:
                titles = re.findall(r'<title>(.*?)</title>', r.text)
            clean = [t for t in titles if len(t) > 10 and "RSS" not in t and "Google" not in t]
            headlines.extend(clean[:3])
            if len(headlines) >= 5:
                break
        except:
            continue
    
    return headlines[:5]'''

content = content.replace(old, new)
with open("scout_skill.py", "w") as f:
    f.write(content)
print("Done")
