import json
import time
from elasticsearch.helpers import bulk

def index_movies(es_client, filepath, index_name="movies"):
    print(f"Début de la lecture du fichier {filepath}...")
    start_time = time.time()
    actions = []
    
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
        
    for i in range(1, len(lines), 2):
        try:
            data_line = json.loads(lines[i].strip())
            movie_data = data_line["fields"]
            
            # Optionnel : récupérer l'ID
            meta_line = json.loads(lines[i-1].strip())
            doc_id = meta_line["index"]["_id"]
            
            action = {
                "_index": index_name,
                "_id": doc_id,
                "_source": movie_data
            }
            actions.append(action)
        except Exception as e:
            continue

    print(f"{len(actions)} films préparés. Envoi en cours...")

    try:
        success, errors = bulk(es_client, actions, raise_on_error=False)
        print(f"{success} films indexés avec succès")
        if errors:
            print(f"{len(errors)} erreurs")
    except Exception as e:
        print(f"Erreur d'indexation : {e}")
        
    print(f"Temps total d'exécution : {time.time() - start_time:.2f} s")

def verify_indexation(es_client, index_name="movies"):
    print("\n--- Vérification de l'indexation ---")
    
    # 1. Forcer le rafraîchissement de l'index
    es_client.indices.refresh(index=index_name)
    
    # 2. Vérifier le nombre de documents
    count = es_client.count(index=index_name)["count"]
    print(f"✅ Nombre de documents indexés : {count}")
    
    # 3. Afficher un échantillon de 3 documents
    print("\nÉchantillon de 3 documents :")
    result = es_client.search(index=index_name, size=3)
    for hit in result["hits"]["hits"]:
        source = hit["_source"]
        print(f" - {source.get('title')} ({source.get('year')}) - Note: {source.get('rating')}")
        
    # 4. Vérifier que le mapping appliqué est correct
    print("\nAperçu du mapping (champs 'title' et 'genres') :")
    mapping = es_client.indices.get_mapping(index=index_name)
    properties = mapping[index_name]["mappings"]["properties"]
    print(f" - Type du champ 'title' : {properties.get('title', {}).get('type')}")
    print(f" - Type du champ 'genres' : {properties.get('genres', {}).get('type')}")