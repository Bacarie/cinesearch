import streamlit as st
from elasticsearch import Elasticsearch
from search import (search_by_title, search_advanced, search_plot, 
                    search_fuzzy, recommend_similar_movies, global_search)
from analytics import global_stats, analyze_categories, advanced_analytics

st.set_page_config(page_title="CinéSearch", layout="wide")

es = Elasticsearch("http://127.0.0.1:9200")

st.title(" CinéSearch — Moteur de Recherche de Films")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Recherche Simple", "Recherche Avancée", "Statistiques & Tops"]
)

def display_movies(results):
    if not results or not results["hits"]["hits"]:
        st.warning("Aucun film trouvé.")
        return

    hits = results["hits"]["hits"]
    cols = st.columns(3)
    
    placeholder = "https://placehold.co/400x600/1a1a2e/ffffff?text=Image+Indisponible"

    for i, hit in enumerate(hits):
        movie = hit["_source"]
        with cols[i % 3]:
            img_url = movie.get("image_url", "")
            
            if not img_url or img_url == "N/A" or "imdb" in img_url.lower():
                img_url = placeholder
                
            try:
                st.image(img_url, caption=f"{movie.get('title')} ({movie.get('year')})", use_container_width=True)
            except Exception:
                st.image(placeholder, caption=f"{movie.get('title')} ({movie.get('year')})", use_container_width=True)
            
            st.write(f"⭐ **Note : {movie.get('rating', 'N/A')}**")
            st.write(f"🎭 {', '.join(movie.get('genres', []))}")
            
            with st.expander("Détails & Recommandations"):
                st.write(f"**Synopsis :** {movie.get('plot')}")
                
                if st.button(f"Recommander pour {movie.get('title')}", key=f"reco_{hit['_id']}"):
                    recos = recommend_similar_movies(es, hit["_id"])
                    if recos and recos["hits"]["hits"]:
                        st.info("Films similaires :")
                        for r in recos["hits"]["hits"]:
                            st.write(f"- {r['_source']['title']} ({r['_source']['year']})")
                    else:
                        st.warning("Aucune recommandation trouvée.")

if menu == "Recherche Simple":
    query = st.text_input("Entrez un titre, un acteur ou un réalisateur...")
    if query:
        res = global_search(es, query) 
        display_movies(res)

elif menu == "Recherche Avancée":
    st.subheader("Filtres précis")
    col1, col2 = st.columns(2)
    with col1:
        genre = st.selectbox("Genre", ["Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Thriller"])
        year_from = st.number_input("Année min", value=1920)
    with col2:
        min_rating = st.slider("Note minimale", 0.0, 10.0, 5.0)
        year_to = st.number_input("Année max", value=2026)
    
    if st.button("Filtrer"):
        res = search_advanced(es, genre=genre, min_rating=min_rating, 
                               year_from=year_from, year_to=year_to)
        display_movies(res)

elif menu == "Statistiques & Tops":
    st.subheader("Analyses du Dataset")
    tab1, tab2 = st.tabs(["Global", "Classements"])
    
    with tab1:
        # On peut appeler tes fonctions d'analytics ici
        # Astuce : Pour Streamlit, il vaudrait mieux que analytics.py retourne des données
        # Mais pour l'instant, on peut ré-afficher les résultats clés
        st.write("Consultez la console pour les stats détaillées ou créez des graphiques ici.")
        # Exemple d'intégration rapide :
        if st.button("Calculer les Stats"):
            global_stats(es) # Cela s'affichera dans ton terminal Linux
            st.success("Statistiques calculées (voir terminal).")