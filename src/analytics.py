def global_stats(es_client, index_name="movies"):
    print("\n Statistiques globales")
    
    aggs = {
        "avg_rating": {"avg": {"field": "rating"}},
        "min_rating": {"min": {"field": "rating"}},
        "max_rating": {"max": {"field": "rating"}}
    }
    
    result = es_client.search(index=index_name, size=0, aggs=aggs)
    
    #total de films
    total_films = result["hits"]["total"]["value"]
    
    #agrégations
    aggs_result = result["aggregations"]
    avg = aggs_result["avg_rating"]["value"]
    mini = aggs_result["min_rating"]["value"]
    maxi = aggs_result["max_rating"]["value"]
    
    print(f"Total de films indexés : {total_films}")
    if avg:
        print(f"Note moyenne globale   : {avg:.2f}/10")
        print(f"Note minimale trouvée  : {mini}/10")
        print(f"Note maximale trouvée  : {maxi}/10")
    
    best = es_client.search(index=index_name, size=1, sort=[{"rating": "desc"}])
    worst = es_client.search(index=index_name, size=1, sort=[{"rating": "asc"}])
    
    if best["hits"]["hits"]:
        best_doc = best["hits"]["hits"][0]["_source"]
        print(f"Film le mieux noté  : {best_doc['title']} ({best_doc.get('rating')})")
    
    if worst["hits"]["hits"]:
        worst_doc = worst["hits"]["hits"][0]["_source"]
        print(f"Film le moins bien noté : {worst_doc['title']} ({worst_doc.get('rating')})")


def analyze_categories(es_client, index_name="movies"):
    print("\n Analyses par catégorie ===")
    
    aggs = {
        "top_genres": {
            "terms": {"field": "genres", "size": 5}
        },
        "top_directors": {
            "terms": {"field": "directors.keyword", "size": 5}
        },
        "movies_per_decade": {
            "histogram": {
                "field": "year",
                "interval": 10,
                "min_doc_count": 1 
            }
        }
    }
    
    result = es_client.search(index=index_name, size=0, aggs=aggs)
    aggs_result = result["aggregations"]
    
    print("\n Top 5 des genres :")
    for bucket in aggs_result["top_genres"]["buckets"]:
        print(f"  - {bucket['key']} : {bucket['doc_count']} films")
        
    print("\n Top 5 des réalisateurs les plus prolifiques :")
    for bucket in aggs_result["top_directors"]["buckets"]:
        print(f"  - {bucket['key']} : {bucket['doc_count']} films")
        
    print("\n Sorties par décennie :")
    for bucket in aggs_result["movies_per_decade"]["buckets"]:
        print(f"  - Années {int(bucket['key'])}s : {bucket['doc_count']} films")


def advanced_analytics(es_client, min_films=3, index_name="movies"):
    print("\n Analyses Avancées ")
    
    aggs = {
        "directors_avg_rating": {
            "terms": {"field": "directors.keyword", "size": 100},
            "aggs": {
                "avg_rating": {"avg": {"field": "rating"}},
                "filter_min_films": {
                    "bucket_selector": {
                        "buckets_path": {
                            "count": "_count"
                        },
                        "script": f"params.count >= {min_films}"
                    }
                },
                # 4. On trie les buckets restants par la meilleure moyenne
                "sort_by_rating": {
                    "bucket_sort": {
                        "sort": [{"avg_rating": "desc"}],
                        "size": 5 # On ne garde que le Top 5 final
                    }
                }
            }
        }
    }
    
    result = es_client.search(index=index_name, size=0, aggs=aggs)
    buckets = result["aggregations"]["directors_avg_rating"]["buckets"]
    
    print(f" Top 5 Réalisateurs les mieux notés en moyenne (min {min_films} films) :")
    for i, bucket in enumerate(buckets, 1):
        nom = bucket['key']
        nb_films = bucket['doc_count']
        moyenne = bucket['avg_rating']['value']
        print(f"  {i}. {nom} -> Moyenne: {moyenne:.2f}/10 ({nb_films} films)")