import sqlite3
import sys

word = " ".join(sys.argv[1:]) or input("Mot-clé : ")

conn = sqlite3.connect("jobs.db")

rows = conn.execute(
    """
    SELECT title, company, location, link,
           CASE WHEN title LIKE ? THEN 'titre' ELSE 'description' END AS found_in
    FROM offers
    WHERE title LIKE ? OR description LIKE ?
    ORDER BY found_in
    """,
    (f"%{word}%", f"%{word}%", f"%{word}%"),
).fetchall()

print(f"{len(rows)} offres trouvées pour « {word} »")
for title, company, location, link, found_in in rows:
    print(f"- [{found_in}] {title} | {company} | {location}")
    print(f"  {link}")

conn.close()