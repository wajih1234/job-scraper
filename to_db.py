import json
import sqlite3

conn = sqlite3.connect("jobs.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS offers (
    link TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    contract TEXT,
    experience TEXT,
    education TEXT,
    salary TEXT,
    description TEXT
)
""")

with open("offers.json", encoding="utf-8") as f:
    offers = json.load(f)

for o in offers:
    conn.execute(
        "INSERT OR REPLACE INTO offers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (o["link"], o["title"], o["company"], o["location"], o["contract"],
         o["experience"], o["education"], o["salary"], o["description"]),
    )

conn.commit()

count = conn.execute("SELECT COUNT(*) FROM offers").fetchone()[0]
print(count, "offres dans la base")
conn.close()