with open("prime_broker.py") as f:
    content = f.read()

# Remove the auto-post on every trade
old = '''            try:
                post_trade(asset, req.direction, size, result["tx_hash"], result["status"])
            except Exception as e:
                log.error(f"Moltbook post error: {e}")'''
new = ''

# Remove the heartbeat thread
old2 = '''    t2 = threading.Thread(target=run_moltbook_heartbeat, daemon=True)
    t2.start()
    log.info("Moltbook heartbeat started")'''
new2 = ''

# Remove imports
old3 = '''from moltbook_agent import post_trade'''
new3 = ''

content = content.replace(old, new).replace(old2, new2).replace(old3, new3)
with open("prime_broker.py", "w") as f:
    f.write(content)
print("Done")
