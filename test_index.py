from elasticsearch import Elasticsearch
from src.config import create_movies_index 
from src.indexer import index_movies

# 1. Connexion à Elasticsearch
es = Elasticsearch("http://127.0.0.1:9200")

# Remplacer le bloc if es.ping(): ... par ceci :
try:
    info = es.info()
    print(f"✅ Connexion réussie à Elasticsearch v{info['version']['number']}")
except Exception as e:
    print(f"❌ Erreur détaillée de connexion : {e}")
    exit()

# 2. Création de l'index et du mapping
create_movies_index(es, "movies")

# 3. Lancement de l'indexation
# Attention : vérifie que le chemin vers ton fichier JSON est le bon !
chemin_json = "data/movies_cleaned_v2.json" 
index_movies(es, chemin_json, "movies")