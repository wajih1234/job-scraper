import sqlite3
import pandas as pd
import streamlit as st
from tanit import get_links_for_keyword, save_offers
st.title("Offres d'emploi en Tunisie")

word = st.text_input("Quel poste cherchez-vous ?", "python")
pages = st.slider("Nombre de pages à chercher", 1, 5, 1)
if st.button("Chercher en ligne sur Tanitjobs"):
    if word.strip():
        with st.spinner("Recherche en cours..."):
            links = get_links_for_keyword(word, max_pages=pages)
            added = save_offers(links)
        st.success(f"{added} nouvelles offres ajoutées")
    else:
        st.warning("Écris d'abord un poste.")
conn = sqlite3.connect("jobs.db")
df = pd.read_sql_query(
    "SELECT title, company, location, contract, experience, salary, link "
    "FROM offers WHERE title LIKE ?",
    conn,
    params=("%" + word + "%",),
)
conn.close()


cities = ["Toutes"] + sorted(df["location"].dropna().unique())
city = st.selectbox("Ville", cities)
if city != "Toutes":
    df = df[df["location"] == city]
st.write(len(df), "offres trouvées")
df = df.fillna("Non précisé")

st.dataframe(
    df,
    use_container_width=True,
    column_config={
        "title": st.column_config.TextColumn("Titre", width="medium"),
        "link": st.column_config.LinkColumn("Lien", display_text="Ouvrir")
        },
)