with open("/root/arc/demo_agents.py") as f:
    content = f.read()

old = '''def agent_cycle(agent: dict):
    AGENT_CYCLES[agent["name"]] += 1

    # Scout signal first
    scout = call_scout(agent)
    if scout.get("signal"):
        log.info(f"Scout: {scout['signal']} ({scout.get('confidence', 0)}%) — {scout.get('best_market', '')[:50]}")
    log = logging.getLogger(agent["name"])'''

new = '''def agent_cycle(agent: dict):
    AGENT_CYCLES[agent["name"]] += 1
    log = logging.getLogger(agent["name"])

    # Scout signal first
    scout = call_scout(agent)
    if scout.get("signal"):
        log.info(f"Scout: {scout['signal']} ({scout.get('confidence', 0)}%) — {scout.get('best_market', '')[:50]}")'''

content = content.replace(old, new)
with open("/root/arc/demo_agents.py", "w") as f:
    f.write(content)
print("Done")
