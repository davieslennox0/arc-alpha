with open("demo_agents.py") as f:
    content = f.read()

old = '''def agent_cycle(agent: dict):
    AGENT_CYCLES[agent["name"]] += 1'''

new = '''def call_scout(agent: dict) -> dict:
    """Agent pays $0.001 and requests a scout signal."""
    try:
        asset = agent["asset"]
        r = requests.post(
            "http://localhost:8000/scout/signal",
            json={"market": f"{asset}-5m", "query": f"{asset} price"},
            timeout=15
        )
        result = r.json()
        # Record to scout feed
        requests.post("http://localhost:8000/scout/record", json={
            "agent_id": agent["name"].lower(),
            "asset": asset,
            "signal": result.get("signal"),
            "confidence": result.get("confidence"),
            "reasoning": result.get("reasoning", ""),
            "news": result.get("news_sources", []),
            "polymarket_url": result.get("polymarket_url", ""),
            "best_market": result.get("best_market", ""),
            "action": result.get("action", "")
        }, timeout=5)
        return result
    except Exception as e:
        return {}

def agent_cycle(agent: dict):
    AGENT_CYCLES[agent["name"]] += 1
    
    # Scout signal first
    scout = call_scout(agent)
    if scout.get("signal"):
        log.info(f"[{agent['name']}] Scout: {scout['signal']} ({scout.get('confidence', 0)}%) — {scout.get('best_market', '')[:50]}")'''

content = content.replace(old, new)
with open("demo_agents.py", "w") as f:
    f.write(content)
print("Done")
