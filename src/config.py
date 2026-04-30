from elasticsearch import Elasticsearch

def create_movies_index(es_client, index_name="movies"):
    # On supprime l'index s'il existe déjà 
    if es_client.indices.exists(index=index_name):
        print(f"L'index '{index_name}' existe déjà. Suppression")
        es_client.indices.delete(index=index_name)

    # Définition du mapping 
    mapping = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "directors": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "actors": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "genres": {
                    "type": "keyword"
                },
                "year": {
                    "type": "integer"
                },
                "rating": {
                    "type": "float"
                },
                "rank": {
                    "type": "integer"
                },
                "release_date": {
                    "type": "date"
                },
                "plot": {
                    "type": "text",
                    "analyzer": "english"
                },
                "running_time_secs": {
                    "type": "integer"
                },
                "image_url": {
                    "type": "keyword"
                }
            }
        }
    }

    print(f"Création de l'index '{index_name}' avec le mapping")
    es_client.indices.create(index=index_name, body=mapping)
    print("Index créé")

if __name__ == "__main__":
    es = Elasticsearch("http://127.0.0.1:9200")
    create_movies_index(es)