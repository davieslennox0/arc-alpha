with open("/root/arc/moltbook_cron.py") as f:
    content = f.read()

old = "import requests\nimport time\nimport sys\nimport json\nfrom pathlib import Path"
new = """import requests
import time
import sys
import json
import os
from pathlib import Path
from groq import Groq"""

old2 = "def get_trade_stats():"
new2 = """def generate_post_content(trades, earnings, portfolio, is_buildx=False):
    try:
        env = {}
        with open('/root/arc/.env') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()

        client = Groq(api_key=env.get('GORQ_API_KEY'))
        
        context = f\"\"\"You are AlphaLoop, an autonomous AI prime broker running on Arc blockchain mainnet.
Current live stats:
- Trades executed: {trades}
- Agent earnings: ${earnings} USDC
- Portfolio value: ${portfolio} USDC
- Win rate: 51.2%
- Sharpe ratio: 2.75
- 3 external agents (Alice/BTC, Bob/ETH, Charlie/SOL) trading autonomously
- AgentRegistry deployed at 0x047445Bf2CC338D635324B8Fe286Dcc74c642789 on Arc

Write a short Moltbook post (max 200 words) as AlphaLoop agent sharing a unique insight about:
- Your trading activity and what signals you're seeing
- The agent economy and how agents are earning
- Something interesting about the market or Arc
- Your ML model learning from trades

Be specific, technical, and autonomous-sounding. Vary the tone and topic each time.
{'Focus on the Agora Agents hackathon submission and what makes AlphaLoop unique as infrastructure for the agent economy.' if is_buildx else ''}
Include the dashboard link: https://alphaloop.duckdns.org
End with 2-3 relevant hashtags including #XLayer\"\"\"

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": context}],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log(f"Groq error: {e}")
        return None

def get_trade_stats():"""

old3 = '''    content = body
    r = requests.post("https://www.moltbook.com/api/v1/posts",
        headers=HEADERS,
        json={"submolt": submolt, "title": title, "content": content}
    )'''

new3 = '''    # Generate unique content via Groq
    groq_content = generate_post_content(trades, earnings, portfolio, is_buildx=not state.get("buildx_posted"))
    if groq_content:
        content = groq_content
        log(f"Groq generated post ({len(content)} chars)")
    else:
        content = body

    r = requests.post("https://www.moltbook.com/api/v1/posts",
        headers=HEADERS,
        json={"submolt": submolt, "title": title, "content": content}
    )'''

content = content.replace(old, new).replace(old2, new2).replace(old3, new3)
with open("/root/arc/moltbook_cron.py", "w") as f:
    f.write(content)
print("Done")
