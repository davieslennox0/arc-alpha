with open("prime_broker.py") as f:
    content = f.read()

old = "app = FastAPI("
new = """from scout_skill import router as scout_router

app = FastAPI("""

old2 = 'app.add_middleware('
new2 = '''app.include_router(scout_router)

app.add_middleware('''

content = content.replace(old, new, 1).replace(old2, new2, 1)
with open("prime_broker.py", "w") as f:
    f.write(content)
print("Done")
