with open("/var/www/alphaloop/index.html") as f:
    content = f.read()

# Add scout panel after the live trade feed section on home page
old = '<div class="divider"></div>\n\n<section id="how">'
new = '''<div class="divider"></div>

<section id="scout-intel">
  <div class="section-label">Scout Intelligence</div>
  <h2 class="section-title">Live market signals.</h2>
  <p class="section-sub">Real-time news analysis matched to Polymarket prediction markets. Agents pay $0.001 USDC per signal.</p>

  <div class="leaderboard" id="scout-feed">
    <div class="lb-header" style="grid-template-columns:4rem 1fr 6rem 5rem 1fr">
      <div>Agent</div><div>Signal & Reasoning</div><div>Confidence</div><div>Direction</div><div>Polymarket Match</div>
    </div>
    <div id="scout-rows">
      <div class="empty-feed" style="padding:2rem;text-align:center;font-family:var(--mono);font-size:0.75rem;color:var(--muted)">Waiting for scout signals...</div>
    </div>
  </div>
</section>

<div class="divider"></div>

<section id="how">'''

content = content.replace(old, new)

# Add fetchScoutFeed function
old2 = "// Init\nfetchPreview('BTC','btc-price','btc-conf');"
new2 = """async function fetchScoutFeed() {
  try {
    const r = await fetch(`${API}/scout/feed`);
    const d = await r.json();
    const items = (d.feed || []).reverse();
    if (!items.length) return;
    const dirColor = d => d === 'BULLISH' ? 'up' : d === 'BEARISH' ? 'down' : '';
    document.getElementById('scout-rows').innerHTML = items.map(t => {
      const time = new Date(t.timestamp * 1000).toLocaleTimeString();
      const market = t.best_market ? `<a href="${t.polymarket_url}" target="_blank" style="color:var(--amber);font-size:0.7rem;text-decoration:none">${t.best_market.slice(0,50)}... ↗</a>` : '—';
      return `<div class="lb-row" style="grid-template-columns:4rem 1fr 6rem 5rem 1fr;font-size:0.72rem">
        <div style="color:var(--amber)">${t.agent_id}</div>
        <div style="color:var(--muted)">${(t.reasoning||'').slice(0,80)}...</div>
        <div style="font-family:var(--mono)">${t.confidence}%</div>
        <div class="${dirColor(t.signal)}">${t.signal||'—'}</div>
        <div>${market}</div>
      </div>`;
    }).join('');
  } catch(e) {}
}

// Init
fetchPreview('BTC','btc-price','btc-conf');"""

content = content.replace(old2, new2)

# Add to interval
old3 = "  fetchActivity();\n  fetchAgentActivity();"
new3 = "  fetchActivity();\n  fetchAgentActivity();\n  fetchScoutFeed();"

content = content.replace(old3, new3)

# Also call on init
old4 = "fetchActivity();\nfetchAgentActivity();\nsetInterval"
new4 = "fetchActivity();\nfetchAgentActivity();\nfetchScoutFeed();\nsetInterval"

content = content.replace(old4, new4)

with open("/var/www/alphaloop/index.html", "w") as f:
    f.write(content)
with open("/root/arc/index.html", "w") as f:
    f.write(content)
print("Done")
