# src/api.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from typing import Optional

# Import de tes fonctions existantes
from .search import search_by_title, global_search, search_advanced, recommend_similar_movies, get_movie_by_id, search_by_actors_and_directors
from .analytics import global_stats, analyze_categories

def fix_image_url(movie):
    """Remplace l'URL obsolète d'IMDb par le CDN d'Amazon"""
    img_url = movie.get("image_url", "")
    if img_url and "ia.media-imdb.com" in img_url:
        img_url = img_url.replace("http://ia.media-imdb.com", "https://m.media-amazon.com")
        img_url = img_url.replace("ia.media-imdb.com", "m.media-amazon.com")
    movie["image_url"] = img_url
    return movie

app = FastAPI(title="CinéSearch API")

#config CORS pour autoriser l'interface à communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #URL du front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

es = Elasticsearch("http://127.0.0.1:9200")

# --- ROUTES DE RECHECHE ---

@app.get("/api/search")
def api_global_search(q: str = Query(..., description="texte à chercher")):
    results = global_search(es, q)
    hits = results["hits"]["hits"]
    return {
        "total": results["hits"]["total"]["value"],
        "movies": [fix_image_url(hit["_source"]) | {"id": hit["_id"], "score": hit["_score"]} for hit in hits]
    }

@app.get("/api/search/advanced")
def api_advanced_search(
    genre: Optional[str] = None,
    min_rating: Optional[float] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
):
    results = search_advanced(es, genre=genre, min_rating=min_rating, year_from=year_from, year_to=year_to)
    hits = results["hits"]["hits"]
    return {"movies": [fix_image_url(hit["_source"]) | {"id": hit["_id"]} for hit in hits]}

@app.get("/api/movies/{movie_id}")
def api_get_movie(movie_id: str):
    result = get_movie_by_id(es, movie_id)
    if not result:
        return {"error": "Movie not found"}
    movie = result["_source"]
    return fix_image_url(movie) | {"id": result["_id"]}

@app.get("/api/directors/{name}/movies")
def api_director_movies(name: str):
    results = search_by_actors_and_directors(es, directors=name)
    hits = results["hits"]["hits"]
    return {"movies": [fix_image_url(hit["_source"]) | {"id": hit["_id"]} for hit in hits]}

@app.get("/api/actors/{name}/movies")
def api_actor_movies(name: str):
    results = search_by_actors_and_directors(es, actors=name)
    hits = results["hits"]["hits"]
    return {"movies": [fix_image_url(hit["_source"]) | {"id": hit["_id"]} for hit in hits]}

@app.get("/api/recommend/{movie_id}")
def api_recommend(movie_id: str):
    results = recommend_similar_movies(es, movie_id)
    hits = results["hits"]["hits"]
    return {"movies": [fix_image_url(hit["_source"]) | {"id": hit["_id"]} for hit in hits]}


 # Stats globales
@app.get("/api/stats")
def api_stats():
    stats = global_stats(es)
    return stats