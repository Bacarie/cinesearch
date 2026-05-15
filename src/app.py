import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from elasticsearch import Elasticsearch
from search import (
    search_by_title, search_advanced, search_plot, search_fuzzy, 
    recommend_similar_movies, global_search, search_exact_quote,
    search_by_duration, search_by_year_range, search_best_movies_by_criteria,
    search_by_actors_and_directors
)
from analytics import (
    global_stats, analyze_categories, advanced_analytics,
    top_actors, best_rated_genres, rating_distribution, years_with_most_releases
)

# Configuration Streamlit
st.set_page_config(page_title="🎬 CinéSearch", layout="wide", initial_sidebar_state="expanded")

# Connexion Elasticsearch
@st.cache_resource
def get_es_client():
    return Elasticsearch("http://127.0.0.1:9200")

es = get_es_client()

# CSS personnalisé
st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# En-tête principal
st.title("🎬 CinéSearch — Moteur de Recherche de Films")
st.markdown("*Explorez une base de données de 5000+ films avec Elasticsearch*")

# Vérification de la connexion
try:
    es.info()
    # On a retiré le st.success pour plus de discrétion
except:
    st.error("❌ Erreur de connexion à Elasticsearch. Vérifiez que le service est démarré.")
    st.stop()

def clear_search():
    st.session_state.last_results = None

if "last_results" not in st.session_state:
    st.session_state.last_results = None
if "last_source_name" not in st.session_state:
    st.session_state.last_source_name = "résultats"

# Menu principal
menu = st.sidebar.radio("📌 Navigation", [
    "🔍 Recherche Globale",
    "📋 Recherche Avancée",
    "🎯 Recherche Spécialisée",
    "⭐ Statistiques Globales",
    "🏆 Classements & Top 10"
], on_change=clear_search)

def format_french_date(date_str):
    if not date_str or date_str == 'N/A': return 'N/A'
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        mois = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        return f"{dt.day} {mois[dt.month]} {dt.year}"
    except:
        return date_str

def display_movie_card(movie, hit_id, idx=0, prefix=""):
    """Affiche une fiche film avec détails."""
    col1, col2 = st.columns([1, 2])
    
    placeholder = "https://placehold.co/400x600/1a1a2e/ffffff?text=Image+Indisponible"
    img_url = movie.get("image_url", "")
    if img_url and "ia.media-imdb.com" in img_url:
        img_url = img_url.replace("http://ia.media-imdb.com", "https://m.media-amazon.com")
        img_url = img_url.replace("ia.media-imdb.com", "m.media-amazon.com")
    if not img_url:
        img_url = placeholder
        
    with col1:
        try:
            st.image(img_url, use_container_width=True)
        except:
            st.image(placeholder, use_container_width=True)
    
    with col2:
        st.subheader(f"{movie.get('title')} ({movie.get('year')})")
        
        # Métriques du film
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("⭐ Note", f"{movie.get('rating', 'N/A')}/10")
        with col_b:
            duration = movie.get("running_time_secs", 0) // 60
            st.metric("⏱️ Durée", f"{duration}min")
        with col_c:
            st.metric("🎬 Rang", movie.get('rank', 'N/A'))
        
        # Genres
        st.write(f"🎭 **Genres:** {', '.join(movie.get('genres', []))}")
        
        # Réalisateurs et acteurs
        st.write(f"🎥 **Réalisateurs:** {', '.join(movie.get('directors', []))}")
        st.write(f"👥 **Acteurs:** {', '.join(movie.get('actors', []))}")
        
        # Expander pour plus de détails
        with st.expander("📖 Voir plus"):
            st.write(f"**Synopsis:** {movie.get('plot')}")
            st.write(f"**Date de sortie:** {format_french_date(movie.get('release_date'))}")
            
            # Bouton recommandations
            if st.toggle(f"💡 Afficher les films similaires", key=f"reco_{prefix}_{hit_id}_{idx}"):
                try:
                    recos = recommend_similar_movies(es, hit_id)
                    if recos["hits"]["hits"]:
                        st.info("🎬 Films similaires trouvés:")
                        for r in recos["hits"]["hits"]:
                            r_movie = r["_source"]
                            st.write(f"• **{r_movie['title']}** ({r_movie['year']}) - ⭐ {r_movie['rating']}/10")
                    else:
                        st.warning("Aucune recommandation trouvée.")
                except Exception as e:
                    st.error(f"Erreur: {e}")

def display_results(results, source_name="Résultats", show_count=True, prefix=""):
    """Affiche les résultats de recherche de manière formatée."""
    if not results or not results["hits"]["hits"]:
        st.warning(f"❌ Aucun film trouvé pour {source_name}.")
        return
    
    hits = results["hits"]["hits"]
    total = results["hits"]["total"]["value"]
    
    if show_count:
        st.info(f"✅ {len(hits)} résultats trouvés (total: {total})")
    
    # Afficher les films un par un
    for idx, hit in enumerate(hits):
        with st.container():
            st.divider()
            display_movie_card(hit["_source"], hit["_id"], idx, prefix=prefix)

# PAGE 1: Recherche Globale
if menu == "🔍 Recherche Globale":
    st.header("🔍 Recherche Globale Multi-Champs")
    st.markdown("Recherchez dans le titre, réalisateurs, acteurs et synopsis.")
    
    search_query = st.text_input(
        "Entrez votre recherche",
        placeholder="Ex: Inception, Christopher Nolan, Brad Pitt..."
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        pass
    with col2:
        search_button = st.button("🔍 Rechercher", width='stretch')
    
    if search_button and search_query:
        with st.spinner("⏳ Recherche en cours..."):
            st.session_state.last_results = global_search(es, search_query)
            st.session_state.last_source_name = "votre recherche"
            
    if st.session_state.last_results is not None:
        display_results(st.session_state.last_results, st.session_state.last_source_name, prefix="global")

# PAGE 2: Recherche Avancée
elif menu == "📋 Recherche Avancée":
    st.header("📋 Recherche Avancée Multi-Critères")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Critères Texte")
        title = st.text_input("Titre", placeholder="Ex: Batman")
        actor = st.text_input("Acteur", placeholder="Ex: Tom Cruise")
        director = st.text_input("Réalisateur", placeholder="Ex: Spielberg")
    
    with col2:
        st.subheader("Critères Numériques")
        
        col_a, col_b = st.columns(2)
        with col_a:
            min_rating = st.slider("Note minimale", 0.0, 10.0, 5.0)
            year_from = st.number_input("Année min", value=1900, min_value=1900, max_value=2030)
        with col_b:
            max_rating = st.slider("Note maximale", 0.0, 10.0, 10.0)
            year_to = st.number_input("Année max", value=2030, min_value=1900, max_value=2030)
        
        genre = st.selectbox("Genre", [
            "Tous",
            "Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Thriller",
            "Adventure", "Animation", "Biography", "Crime", "Documentary",
            "Family", "Fantasy", "History", "Mystery", "Romance", "Sport",
            "Western"
        ])
    
    search_button = st.button("🔍 Rechercher avec filtres", width='stretch')
    
    if search_button:
        with st.spinner("⏳ Application des filtres..."):
            genre_filter = None if genre == "Tous" else genre
            st.session_state.last_results = search_advanced(
                es,
                title=title or None,
                actor=actor or None,
                director=director or None,
                genre=genre_filter,
                min_rating=min_rating,
                max_rating=max_rating,
                year_from=year_from,
                year_to=year_to
            )
            st.session_state.last_source_name = "vos critères"
            
    if st.session_state.last_results is not None:
        display_results(st.session_state.last_results, st.session_state.last_source_name, prefix="adv")

# PAGE 3: Recherche Spécialisée
elif menu == "🎯 Recherche Spécialisée":
    st.header("🎯 Recherches Spécialisées")
    
    search_type = st.tabs([
        "📖 Phrase exacte",
        "⏱️ Par durée",
        "📅 Par période",
        "🎬 Meilleurs films",
        "👥 Acteurs & Réalisateurs"
    ])
    
    with search_type[0]:  # Phrase exacte
        st.subheader("📖 Recherche de Phrase Exacte")
        quote = st.text_area(
            "Recherchez une phrase exacte dans les synopsis",
            placeholder="Ex: hero, love, time travel, artificial intelligence..."
        )
        if st.button("🔍 Chercher cette phrase"):
            if quote:
                with st.spinner("⏳ Recherche en cours..."):
                    st.session_state.last_results = search_exact_quote(es, quote)
                    st.session_state.last_source_name = "cette phrase"
        
        if st.session_state.last_results is not None:
            display_results(st.session_state.last_results, st.session_state.last_source_name, prefix="intrigue")
    
    with search_type[1]:  # Durée
        st.subheader("⏱️ Recherche par Durée")
        col1, col2 = st.columns(2)
        with col1:
            min_duration = st.slider("Durée min (minutes)", 0, 300, 60)
        with col2:
            max_duration = st.slider("Durée max (minutes)", 0, 300, 180)
        
        if st.button("🔍 Chercher par durée"):
            with st.spinner("⏳ Recherche en cours..."):
                st.session_state.last_results = search_by_duration(
                    es,
                    min_duration_secs=min_duration * 60,
                    max_duration_secs=max_duration * 60
                )
                st.session_state.last_source_name = "cette plage horaire"
                
        if st.session_state.last_results is not None:
            display_results(st.session_state.last_results, st.session_state.last_source_name, prefix="floue")
    
    with search_type[2]:  # Période
        st.subheader("📅 Recherche par Période")
        col1, col2 = st.columns(2)
        with col1:
            year_from = st.number_input("De l'année", value=2000, min_value=1920, max_value=2030)
        with col2:
            year_to = st.number_input("À l'année", value=2030, min_value=1920, max_value=2030)
        
        if st.button("🔍 Chercher par période"):
            if year_from <= year_to:
                with st.spinner("⏳ Recherche en cours..."):
                    st.session_state.last_results = search_by_year_range(es, year_from, year_to)
                    st.session_state.last_source_name = f"la période {year_from}-{year_to}"
            else:
                st.error("L'année de fin doit être après l'année de début.")
                
        if st.session_state.last_results is not None:
            display_results(st.session_state.last_results, st.session_state.last_source_name, prefix="crit")
    
    with search_type[3]:  # Meilleurs films
        st.subheader("🎬 Top Films par Critères")
        col1, col2 = st.columns(2)
        with col1:
            genre = st.selectbox("Genre (ou Tous)", [
                "Tous", "Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Thriller",
                "Adventure", "Animation", "Biography", "Crime", "Documentary",
                "Family", "Fantasy", "History", "Mystery", "Romance", "Sport"
            ])
        with col2:
            min_rating = st.slider("Note minimale", 0.0, 10.0, 7.0)
        
        if st.button("🔍 Voir top films"):
            with st.spinner("⏳ Recherche en cours..."):
                genre_filter = None if genre == "Tous" else genre
                st.session_state.last_results = search_best_movies_by_criteria(
                    es, genre=genre_filter, min_rating=min_rating, limit=20
                )
                st.session_state.last_source_name = f"{genre} avec note ≥ {min_rating}"
                
        if st.session_state.last_results is not None:
            display_results(st.session_state.last_results, st.session_state.last_source_name, prefix="top")
    
    with search_type[4]:  # Acteurs & Réalisateurs
        st.subheader("👥 Recherche par Acteurs & Réalisateurs")
        col1, col2 = st.columns(2)
        with col1:
            actors = st.text_input("Acteur", placeholder="Ex: Tom Cruise")
        with col2:
            directors = st.text_input("Réalisateur", placeholder="Ex: Spielberg")
        
        if st.button("🔍 Chercher films"):
            if actors or directors:
                with st.spinner("⏳ Recherche en cours..."):
                    st.session_state.last_results = search_by_actors_and_directors(
                        es, actors=actors or None, directors=directors or None
                    )
                    st.session_state.last_source_name = "vos critères"
                    
        if st.session_state.last_results is not None:
            display_results(st.session_state.last_results, st.session_state.last_source_name, prefix="act")

# PAGE 4: Statistiques Globales
elif menu == "⭐ Statistiques Globales":
    st.header("⭐ Statistiques Globales du Dataset")
    
    if st.button("📊 Charger les statistiques"):
        with st.spinner("⏳ Calcul des statistiques..."):
            stats = global_stats(es)
            
            # Affichage des metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎬 Total films", stats["total_films"])
            with col2:
                st.metric("⭐ Note moyenne", f"{stats['avg_rating']}/10")
            with col3:
                st.metric("📊 Écart-type", f"±{stats['std_rating']}")
            with col4:
                st.metric("⏱️ Durée moyenne", f"{stats['avg_duration_min']}min")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                max_min = stats["max_rating"] - stats["min_rating"]
                st.metric("📈 Écart (max-min)", f"{max_min:.1f}", delta="Variabilité")
            with col2:
                st.metric("⭐ Meilleur film", stats.get("best_movie", "N/A")[:50])
            
            st.info(f"🎭 Moins bon: {stats.get('worst_movie', 'N/A')[:60]}")
            
            # Distribution des notes
            st.subheader("📊 Distribution des Notes")
            dist = rating_distribution(es)
            dist_df = pd.DataFrame(dist)
            st.bar_chart(dist_df.set_index("rating_range")["count"], width='stretch')
            
            # Années avec plus de sorties
            st.subheader("📅 Années avec Plus de Sorties")
            years_data = years_with_most_releases(es, n=20)
            years_df = pd.DataFrame(years_data)
            st.line_chart(years_df.set_index("year")["count"], width='stretch')

# PAGE 5: Classements & Tops
elif menu == "🏆 Classements & Top 10":
    st.header("🏆 Classements & Top 10")
    
    tabs = st.tabs(["🎬 Catégories", "👥 Acteurs", "🎭 Genres", "🎥 Réalisateurs"])
    
    with tabs[0]:  # Catégories
        st.subheader("📊 Analyses par Catégories")
        if st.button("Charger les analyses"):
            with st.spinner("⏳ Calcul en cours..."):
                categories = analyze_categories(es)
                
                # Top genres
                st.subheader("🎭 Top 10 Genres")
                genres_df = pd.DataFrame(categories["top_genres"]).sort_values("count", ascending=True)
                st.dataframe(genres_df.sort_values("count", ascending=False), width='stretch')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.bar_chart(genres_df.set_index("name")["count"], horizontal=True)
                with col2:
                    fig = px.pie(genres_df, values='count', names='name', title='Distribution des Genres')
                    st.plotly_chart(fig, width='stretch')
                
                # Top réalisateurs
                st.subheader("🎥 Top 10 Réalisateurs")
                directors_df = pd.DataFrame(categories["top_directors"][:10]).sort_values("count", ascending=True)
                st.dataframe(directors_df.sort_values("count", ascending=False), width='stretch')
                st.bar_chart(directors_df.set_index("name")["count"], horizontal=True)
                
                # Films par décennie
                st.subheader("📅 Films par Décennie")
                decades_df = pd.DataFrame(categories["by_decade"])
                st.line_chart(decades_df.set_index("decade")["count"])
    
    with tabs[1]:  # Acteurs
        st.subheader("👥 Top 10 Acteurs (par nombre de films)")
        if st.button("Charger les top acteurs"):
            with st.spinner("⏳ Calcul en cours..."):
                actors_data = top_actors(es, n=10)
                actors_df = pd.DataFrame(actors_data).sort_values("film_count", ascending=True)
                
                st.dataframe(actors_df.sort_values("film_count", ascending=False), width='stretch')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.bar_chart(actors_df.set_index("name")["film_count"], horizontal=True)
                with col2:
                    st.scatter_chart(actors_df, x="avg_rating", y="name", color="avg_rating", size="film_count")
    
    with tabs[2]:  # Genres
        st.subheader("🎭 Genres Mieux Notés")
        if st.button("Charger les meilleurs genres"):
            with st.spinner("⏳ Calcul en cours..."):
                genres_data = best_rated_genres(es, n=10)
                genres_df = pd.DataFrame(genres_data).sort_values("avg_rating", ascending=True)
                
                st.dataframe(genres_df.sort_values("avg_rating", ascending=False), width='stretch')
                
                st.bar_chart(genres_df.set_index("name")["avg_rating"], horizontal=True)
    
    with tabs[3]:  # Réalisateurs
        st.subheader("🎥 Top Réalisateurs (Note Moyenne)")
        if st.button("Charger les top réalisateurs"):
            with st.spinner("⏳ Calcul en cours..."):
                directors_data = advanced_analytics(es, min_films=3)
                directors_df = pd.DataFrame(directors_data).sort_values("avg_rating", ascending=True)
                
                st.dataframe(directors_df.sort_values("avg_rating", ascending=False), width='stretch')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.bar_chart(directors_df.set_index("name")["avg_rating"], horizontal=True)
                with col2:
                    st.scatter_chart(directors_df, x="film_count", y="name", color="avg_rating", size="film_count")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; padding: 1rem; color: #666;'>
        <small>🎬 CinéSearch - Moteur de Recherche de Films avec Elasticsearch | Dataset: ~5000 films</small>
    </div>
""", unsafe_allow_html=True)