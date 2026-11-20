# Job Scraper — offres d'emploi en Tunisie

Petit projet personnel : un scraper Python qui récupère des offres d'emploi
et un tableau de bord Streamlit pour les chercher par poste et par ville.

## Fonctionnement
- `tanit.py` : récupère et lit les pages d'offres (requests + BeautifulSoup).
- `app.py` : tableau de bord Streamlit avec recherche par poste et filtre par ville.
- Les offres sont stockées dans une base SQLite locale (`jobs.db`).

## Lancer le projet
    pip install requests beautifulsoup4 streamlit
    streamlit run app.py

