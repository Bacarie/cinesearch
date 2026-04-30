from elasticsearch import Elasticsearch
from src.analytics import global_stats, analyze_categories, advanced_analytics

es = Elasticsearch("http://127.0.0.1:9200")

global_stats(es)
analyze_categories(es)
advanced_analytics(es, min_films=5) # Cherchons les réals qui ont au moins fait 5 films