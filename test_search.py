from elasticsearch import Elasticsearch

# Importation de toutes nos fonctions depuis src/search.py
from src.search import (
    search_by_title, 
    search_advanced, 
    search_plot, 
    search_fuzzy, 
    suggest_titles,
    recommend_similar_movies,
    global_search,
    search_best_rated,
    search_exact_quote
)

# 1. Connexion à Elasticsearch
es = Elasticsearch("http://127.0.0.1:9200")

# Vérification rapide de la connexion
if not es.ping():
    print("Impossible de se connecter à ES")
    exit()

print("Connexion OK. \n")


search_by_title(es, "Star Wars")

search_advanced(es, genre="Sci-Fi", min_rating=8.0, year_from=2010, year_to=2019)

search_plot(es, "time travel past mutant")

search_fuzzy(es, "Incepion") 

suggest_titles(es, "Batma")


recommend_similar_movies(es, "12")

global_search(es, "Christopher Nolan")

search_best_rated(es, "Batman")

search_exact_quote(es, "A medical engineer and an astronaut work together")