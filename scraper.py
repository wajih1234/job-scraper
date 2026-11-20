import requests
import time
import json
from bs4 import BeautifulSoup


def scrape_offer(link):
    soup = BeautifulSoup(requests.get(link).text, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    lines = text.split("\n")

    def get_field(label):
        for i, line in enumerate(lines):
            if line == label:
                return " ".join(lines[i + 1].split())
        return None

    start = lines.index("« Retour")
    d_start = text.find("Description de l'emploi")
    d_end = text.find("Date d'expiration")
    header = lines[start + 1 : start + 6]
    location = next((l for l in header if l.endswith("Tunisie")), None)

    return {
        "link": link,
        "title": lines[start + 1],
        "company": lines[start + 2].rstrip(" -"),
        "location": location,
        "contract": get_field("Type d'emploi désiré :"),
        "experience": get_field("Experience :"),
        "education": get_field("Niveau d'étude :"),
        "salary": get_field("Rémunération proposée :"),
        "description": text[d_start:d_end],
    }


with open("links.json", encoding="utf-8") as f:
    links = json.load(f)

print(len(links), "liens chargés")

offers = []

for link in links:
    try:
        offers.append(scrape_offer(link))
    except Exception as e:
        print("Erreur :", link, e)
    time.sleep(1)

    if offers and len(offers) % 50 == 0:
        with open("offers.json", "w", encoding="utf-8") as f:
            json.dump(offers, f, ensure_ascii=False, indent=2)
        print(len(offers), "offres sauvegardées")

print("Total :", len(offers), "offres")

with open("offers.json", "w", encoding="utf-8") as f:
    json.dump(offers, f, ensure_ascii=False, indent=2)

print("Fichier offers.json créé")