import requests
import time
import sqlite3
import re
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup

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
def build_url(keyword):
    return (
        "https://www.tanitjobs.com/jobs/?listing_type%5Bequal%5D=Job&action=search"
        "&keywords%5Ball_words%5D=" + quote(keyword)
        + "&GooglePlace%5Blocation%5D%5Bvalue%5D=&GooglePlace%5Blocation%5D%5Bradius%5D=50"
    )

def get_links_for_keyword(keyword, max_pages=3):
    to_visit = [build_url(keyword)]
    visited = set()
    all_links = []

    while to_visit and len(visited) < max_pages:
        page_url = to_visit.pop(0)
        if page_url in visited:
            continue
        visited.add(page_url)

        soup = BeautifulSoup(requests.get(page_url).text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/job/" in href:
                if href not in all_links:
                    all_links.append(href)
            elif "page=" in href:
                full = urljoin(page_url, href)
                if full not in visited and full not in to_visit:
                    to_visit.append(full)
        time.sleep(1)

    return all_links

def save_offers(links):
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

    existing = {row[0] for row in conn.execute("SELECT link FROM offers")}
    new_links = [l for l in links if l not in existing]

    saved = 0
    for link in new_links:
        try:
            o = scrape_offer(link)
        except Exception as e:
            print("Erreur :", link, e)
            continue
        conn.execute(
            "INSERT OR REPLACE INTO offers "
            "(link, title, company, location, contract, experience, education, salary, description) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (o["link"], o["title"], o["company"], o["location"], o["contract"],
             o["experience"], o["education"], o["salary"], o["description"]),
        )
        conn.commit()
        saved += 1
        time.sleep(1)

    conn.close()
    return saved

def get_links_from_sitemap():
    text = requests.get("https://www.tanitjobs.com/sitemap.xml").text
    return re.findall(r"<loc>(https://www\.tanitjobs\.com/job/[^<]+)</loc>", text)