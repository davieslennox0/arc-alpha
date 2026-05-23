import json
import os

STRATEGY_FILE = "strategy_history.json"

def load_strategy_history():
    if os.path.exists(STRATEGY_FILE):
        with open(STRATEGY_FILE) as f:
            return json.load(f)
    return {"balanced": {"trades": 0, "wins": 0, "total_pnl": 0},
            "aggressive": {"trades": 0, "wins": 0, "total_pnl": 0},
            "conservative": {"trades": 0, "wins": 0, "total_pnl": 0}}

def save_strategy_history(data):
    with open(STRATEGY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def select_strategy(signal):
    return "balanced", signal, 1.0

def record_strategy_trade(strategy, pnl):
    data = load_strategy_history()
    if strategy in data:
        data[strategy]["trades"] += 1
        data[strategy]["total_pnl"] += pnl
        if pnl > 0:
            data[strategy]["wins"] += 1
    save_strategy_history(data)

def get_leaderboard():
    data = load_strategy_history()
    result = []
    for name, stats in data.items():
        trades = stats.get("trades", 0)
        wins = stats.get("wins", 0)
        pnl = stats.get("total_pnl", 0)
        win_rate = (wins / trades * 100) if trades > 0 else 0
        result.append({
            "strategy": name,
            "trades": trades,
            "win_rate": round(win_rate, 1),
            "total_pnl": round(pnl, 4),
            "sharpe": 0.0,
            "allocation": 99.3 if name == "balanced" else 0.4
        })
    return result
