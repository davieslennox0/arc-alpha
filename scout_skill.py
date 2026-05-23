import os
import json
import requests
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/scout", tags=["Scout Skill"])
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

POLYMARKET_API = "https://gamma-api.polymarket.com"

class ScoutRequest(BaseModel):
    market: str = "BTC-5m"
    query: str = ""

def fetch_news(topic: str) -> list:
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
    
    return headlines[:5]

def fetch_polymarket_markets(keyword: str) -> list:
    """Fetch relevant Polymarket markets."""
    try:
        r = requests.get(
            f"{POLYMARKET_API}/markets",
            params={"search": keyword, "limit": 5, "active": True},
            timeout=8
        )
        markets = r.json() if isinstance(r.json(), list) else []
        result = []
        for m in markets[:3]:
            prices = m.get("outcomePrices", "[]")
            if isinstance(prices, str):
                import json as _j
                try:
                    prices = _j.loads(prices)
                except:
                    prices = ["0", "0"]
            result.append({
                "id": m.get("id"),
                "question": m.get("question"),
                "yes_price": prices[0] if len(prices) > 0 else "0",
                "no_price": prices[1] if len(prices) > 1 else "0",
                "volume": m.get("volume", 0),
                "url": f"https://polymarket.com/event/{m.get('slug', '')}"
            })
        return result
    except:
        return []

def analyze_with_groq(news: list, markets: list, market_type: str) -> dict:
    """Use Groq to match news sentiment to market outcomes."""
    if not news:
        return {"confidence": 0, "signal": "NEUTRAL", "reasoning": "No news available"}

    news_text = "\n".join([f"- {n}" for n in news])
    markets_text = "\n".join([f"- {m['question']} (YES: {m['yes_price']})" for m in markets]) if markets else "No markets found"

    prompt = f"""You are AlphaLoop Scout, an AI signal agent analyzing news for prediction market opportunities.

Market type requested: {market_type}

Recent news headlines:
{news_text}

Related Polymarket markets:
{markets_text}

Analyze the news and determine:
1. Overall sentiment: BULLISH, BEARISH, or NEUTRAL
2. Confidence score: 0-100
3. Which Polymarket market best matches this signal
4. Brief reasoning (1-2 sentences)

Respond in JSON only:
{{"signal": "BULLISH|BEARISH|NEUTRAL", "confidence": 0-100, "best_market": "market question or null", "reasoning": "brief explanation"}}"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        text = response.choices[0].message.content.strip()
        # Extract JSON
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"signal": "NEUTRAL", "confidence": 0, "reasoning": text}
    except Exception as e:
        return {"signal": "NEUTRAL", "confidence": 0, "reasoning": str(e)}

@router.post("/signal")
def get_scout_signal(req: ScoutRequest):
    """
    AlphaLoop Scout — news-matched Polymarket signal.
    Costs $0.001 USDC per request via Transfer Skill.
    """
    topic = req.query or req.market.replace("-", " ")
    
    # Fetch news and markets in parallel
    news = fetch_news(topic)
    markets = fetch_polymarket_markets(topic)
    
    # Analyze with Groq
    analysis = analyze_with_groq(news, markets, req.market)
    
    return {
        "market": req.market,
        "signal": analysis.get("signal", "NEUTRAL"),
        "confidence": analysis.get("confidence", 0),
        "reasoning": analysis.get("reasoning", ""),
        "best_market": analysis.get("best_market"),
        "polymarket_markets": markets,
        "news_sources": news[:3],
        "action": "HIGH_CONFIDENCE — Consider placing bet on Polymarket" if analysis.get("confidence", 0) >= 70 else "LOW_CONFIDENCE — Monitor market",
        "polymarket_url": markets[0]["url"] if markets else "https://polymarket.com",
        "powered_by": "AlphaLoop Scout + Groq llama-3.1-8b-instant"
    }

@router.get("/markets")
def list_markets(keyword: str = "crypto"):
    """List active Polymarket markets for a keyword."""
    return {"markets": fetch_polymarket_markets(keyword)}
