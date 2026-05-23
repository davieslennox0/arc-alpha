with open("scout_skill.py") as f:
    content = f.read()

old = '''        return [{
            "id": m.get("id"),
            "question": m.get("question"),
            "yes_price": m.get("outcomePrices", ["0"])[0] if m.get("outcomePrices") else "0",
            "no_price": m.get("outcomePrices", ["0", "0"])[1] if m.get("outcomePrices") else "0",
            "volume": m.get("volume", 0),
            "url": f"https://polymarket.com/event/{m.get('slug', '')}"
        } for m in markets[:3]]'''

new = '''        result = []
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
        return result'''

content = content.replace(old, new)
with open("scout_skill.py", "w") as f:
    f.write(content)
print("Done")
