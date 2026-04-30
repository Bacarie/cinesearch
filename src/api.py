# src/api.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from typing import Optional

# Import de tes fonctions existantes
from .search import search_by_title, global_search, search_advanced, recommend_similar_movies
from .analytics import global_stats, analyze_categories

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
        "movies": [hit["_source"] | {"id": hit["_id"], "score": hit["_score"]} for hit in hits]
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
    return {"movies": [hit["_source"] | {"id": hit["_id"]} for hit in hits]}

@app.get("/api/recommend/{movie_id}")
def api_recommend(movie_id: str):
    results = recommend_similar_movies(es, movie_id)
    hits = results["hits"]["hits"]
    return {"movies": [hit["_source"] | {"id": hit["_id"]} for hit in hits]}


 #WIP stats sur le site
@app.get("/api/stats")
def api_stats():
    return {"message": "Endpoint pour les stats"}