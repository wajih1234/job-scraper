import requests
import time
import json
from urllib.parse import quote
from urllib.parse import urljoin
from bs4 import BeautifulSoup

KEYWORD = "développeur"

LIST_URL = (
    "https://www.tanitjobs.com/jobs/?listing_type%5Bequal%5D=Job&action=search"
    "&keywords%5Ball_words%5D=" + quote(KEYWORD)
    + "&GooglePlace%5Blocation%5D%5Bvalue%5D=&GooglePlace%5Blocation%5D%5Bradius%5D=50"
)

def get_offer_links(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        if "/job/" in a["href"]:
            links.add(a["href"])
    return list(links)

def get_page_urls(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    pages = {url}
    for a in soup.find_all("a", href=True):
        if "page=" in a["href"]:
            pages.add(urljoin(url, a["href"]))
    return sorted(pages)
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

all_links = set()
visited = set()
to_visit = [LIST_URL]

while to_visit:
    page_url = to_visit.pop(0)
    if page_url in visited:
        continue
    visited.add(page_url)

    page_links = get_offer_links(page_url)
    all_links.update(page_links)
    print("Page", len(visited), ":", len(page_links), "offres")

    for p in get_page_urls(page_url):
        if p not in visited:
            to_visit.append(p)
    time.sleep(1)

print("Total sans doublons :", len(all_links))

with open("links.json", "w", encoding="utf-8") as f:
    json.dump(sorted(all_links), f, ensure_ascii=False, indent=2)

print("Fichier links.json créé")
exit()
links = get_offer_links(LIST_URL)
offers = []

for link in links:
    try:
        offer = scrape_offer(link)
        offers.append(offer)
        print(len(offers), "-", offer["title"])
    except Exception as e:
        print("Erreur :", link, e)
    time.sleep(1)

print("Total :", len(offers), "offres")

with open("offers.json", "w", encoding="utf-8") as f:
    json.dump(offers, f, ensure_ascii=False, indent=2)

print("Fichier offers.json créé")