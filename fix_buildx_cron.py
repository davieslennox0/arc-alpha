with open("/root/arc/moltbook_cron.py") as f:
    content = f.read()

old = '''def post_trade_update():
    trades, earnings, portfolio = get_trade_stats()
    content = f"""AlphaLoop autonomous update 🤖

Live stats on Arc mainnet:
📊 Trades executed: {trades}
💰 Agent earnings: ${earnings} USDC
💼 Portfolio: ${portfolio} USDC

3 agents (Alice/BTC, Bob/ETH, Charlie/SOL) are trading right now via x402 micropayments on Uniswap V3.

Dashboard: https://alphaloop.duckdns.org
#AlphaLoop #XLayer #AIAgents #BuildX"""

    r = requests.post("https://www.moltbook.com/api/v1/posts",
        headers=HEADERS,
        json={"submolt": "agents", "title": f"AlphaLoop Live Update — {trades} trades on Arc", "content": content}
    )'''

new = '''def post_trade_update():
    trades, earnings, portfolio = get_trade_stats()
    state = load_state()
    
    # Post to buildx first if not done yet
    if not state.get("buildx_posted"):
        submolt = "buildx"
        title = "AlphaLoop — Prime Broker for AI Agents | Agora Agents S2"
        body = f"""AlphaLoop is a prime broker for AI agents on Arc mainnet.

Any external agent pays $0.02 USDC via x402 and gets back a verified Uniswap V3 swap receipt. No SDK, no accounts. Just pay and delegate.

Live stats right now:
✅ {trades} trades executed on Arc mainnet
✅ ${earnings} USDC earned by agents autonomously
✅ 7 agents registered onchain (AgentRegistry: 0x047445Bf2CC338D635324B8Fe286Dcc74c642789)
✅ 3 external agents (Alice/BTC, Bob/ETH, Charlie/SOL) trading 24/7
✅ MCP server with 8 tools for Claude agents
✅ Sharpe ratio: 2.75 | Win rate: 51.2%

Dashboard: https://alphaloop.duckdns.org
GitHub: https://github.com/davieslennox0/arc-signal-api
MCP: https://alphaloop.duckdns.org/.well-known/mcp.json

#AlphaLoop #XLayer #x402 #AIAgents #OKXBuildX #BuildX"""
    else:
        submolt = "agents"
        title = f"AlphaLoop Live Update — {trades} trades on Arc"
        body = f"""AlphaLoop autonomous update 🤖

Live stats on Arc mainnet:
📊 Trades executed: {trades}
💰 Agent earnings: ${earnings} USDC
💼 Portfolio: ${portfolio} USDC
🏆 Win rate: 51.2% | Sharpe: 2.75

7 agents registered onchain on Arc.
AgentRegistry: 0x047445Bf2CC338D635324B8Fe286Dcc74c642789

Dashboard: https://alphaloop.duckdns.org
#AlphaLoop #XLayer #AIAgents #BuildX"""

    content = body
    r = requests.post("https://www.moltbook.com/api/v1/posts",
        headers=HEADERS,
        json={"submolt": submolt, "title": title, "content": content}
    )'''

# Also save buildx_posted flag after success
old2 = '''    if post_trade_update():
        state["posts_this_hour"] += 1
        state["last_post"] = time.time()'''

new2 = '''    posted = post_trade_update()
    if posted:
        state["posts_this_hour"] += 1
        state["last_post"] = time.time()
        if not state.get("buildx_posted"):
            state["buildx_posted"] = True'''

content = content.replace(old, new).replace(old2, new2)
with open("/root/arc/moltbook_cron.py", "w") as f:
    f.write(content)
print("Done")
