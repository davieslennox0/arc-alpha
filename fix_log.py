with open("/root/arc/demo_agents.py") as f:
    content = f.read()

old = '''def call_scout(agent: dict) -> dict:
    import logging
    _log = logging.getLogger(agent["name"])'''
new = '''def call_scout(agent: dict) -> dict:'''

content = content.replace(old, new)
with open("/root/arc/demo_agents.py", "w") as f:
    f.write(content)
print("Done")
