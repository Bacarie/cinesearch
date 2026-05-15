def global_stats(es_client, index_name="movies"):
    """Retourne les statistiques globales du dataset."""
    
    aggs = {
        "avg_rating": {"avg": {"field": "rating"}},
        "min_rating": {"min": {"field": "rating"}},
        "max_rating": {"max": {"field": "rating"}},
        "extended_stats_rating": {"extended_stats": {"field": "rating"}},
        "avg_duration": {"avg": {"field": "running_time_secs"}},
        "count_by_decade": {"terms": {"field": "year", "size": 100}}
    }
    
    result = es_client.search(index=index_name, size=0, aggs=aggs)
    
    total_films = result["hits"]["total"]["value"]
    aggs_result = result["aggregations"]
    
    extended_stats = aggs_result["extended_stats_rating"]
    
    stats = {
        "total_films": total_films,
        "avg_rating": round(aggs_result["avg_rating"]["value"], 2),
        "min_rating": aggs_result["min_rating"]["value"],
        "max_rating": aggs_result["max_rating"]["value"],
        "std_rating": round(extended_stats.get("std_deviation", 0), 2),
        "avg_duration_secs": int(aggs_result["avg_duration"]["value"]),
        "avg_duration_min": int(aggs_result["avg_duration"]["value"]) // 60
    }
    
    best = es_client.search(index=index_name, size=1, sort=[{"rating": "desc"}])
    worst = es_client.search(index=index_name, size=1, sort=[{"rating": "asc"}])
    
    if best["hits"]["hits"]:
        best_doc = best["hits"]["hits"][0]["_source"]
        stats["best_movie"] = f"{best_doc['title']} ({best_doc.get('year')}) - {best_doc.get('rating')}/10"
    
    if worst["hits"]["hits"]:
        worst_doc = worst["hits"]["hits"][0]["_source"]
        stats["worst_movie"] = f"{worst_doc['title']} ({worst_doc.get('year')}) - {worst_doc.get('rating')}/10"
    
    # Print pour compatibilité
    print(f"\n📊 Statistiques globales")
    print(f"Total de films indexés : {stats['total_films']}")
    print(f"Note moyenne : {stats['avg_rating']}/10 (±{stats['std_rating']})")
    print(f"Note min/max : {stats['min_rating']:.1f} / {stats['max_rating']:.1f}")
    print(f"Durée moyenne : {stats['avg_duration_min']}min")
    print(f"Meilleur film : {stats.get('best_movie', 'N/A')}")
    print(f"Moins bon : {stats.get('worst_movie', 'N/A')}")
    
    return stats


def analyze_categories(es_client, index_name="movies"):
    """Retourne les analyses par catégorie."""
    
    aggs = {
        "top_genres": {
            "terms": {"field": "genres", "size": 10}
        },
        "top_directors": {
            "terms": {"field": "directors.keyword", "size": 10}
        },
        "top_actors": {
            "terms": {"field": "actors.keyword", "size": 10}
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
    
    categories = {
        "top_genres": [{"name": b["key"], "count": b["doc_count"]} for b in aggs_result["top_genres"]["buckets"]],
        "top_directors": [{"name": b["key"], "count": b["doc_count"]} for b in aggs_result["top_directors"]["buckets"]],
        "top_actors": [{"name": b["key"], "count": b["doc_count"]} for b in aggs_result["top_actors"]["buckets"]],
        "by_decade": [{"decade": int(b["key"]), "count": b["doc_count"]} for b in aggs_result["movies_per_decade"]["buckets"]]
    }
    
    print("\n📊 Analyses par catégorie ===")
    print("\nTop 10 des genres :")
    for item in categories["top_genres"]:
        print(f"  - {item['name']} : {item['count']} films")
    
    print("\nTop 10 des réalisateurs :")
    for item in categories["top_directors"][:5]:
        print(f"  - {item['name']} : {item['count']} films")
        
    print("\nTop 10 des acteurs :")
    for item in categories["top_actors"][:5]:
        print(f"  - {item['name']} : {item['count']} films")
    
    print("\nSorties par décennie :")
    for item in sorted(categories["by_decade"], key=lambda x: x["decade"]):
        print(f"  - Années {item['decade']}s : {item['count']} films")
    
    return categories


def advanced_analytics(es_client, min_films=3, index_name="movies"):
    """Retourne les analyses avancées (réalisateurs avec meilleures moyennes)."""
    
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
                "sort_by_rating": {
                    "bucket_sort": {
                        "sort": [{"avg_rating": "desc"}],
                        "size": 10
                    }
                }
            }
        }
    }
    
    result = es_client.search(index=index_name, size=0, aggs=aggs)
    buckets = result["aggregations"]["directors_avg_rating"]["buckets"]
    
    directors = [
        {
            "rank": i,
            "name": bucket["key"],
            "avg_rating": round(bucket["avg_rating"]["value"], 2),
            "film_count": bucket["doc_count"]
        }
        for i, bucket in enumerate(buckets, 1)
    ]
    
    print(f"\n🎬 Top Réalisateurs (min {min_films} films) :")
    for d in directors[:10]:
        print(f"  {d['rank']}. {d['name']} → Moyenne: {d['avg_rating']}/10 ({d['film_count']} films)")
    
    return directors


def top_actors(es_client, n=10, index_name="movies"):
    """Retourne les top N acteurs par nombre de films."""
    
    aggs = {
        "top_actors_agg": {
            "terms": {"field": "actors.keyword", "size": n},
            "aggs": {
                "avg_rating": {"avg": {"field": "rating"}}
            }
        }
    }
    
    result = es_client.search(index=index_name, size=0, aggs=aggs)
    buckets = result["aggregations"]["top_actors_agg"]["buckets"]
    
    actors = [
        {
            "rank": i,
            "name": bucket["key"],
            "film_count": bucket["doc_count"],
            "avg_rating": round(bucket["avg_rating"]["value"], 2)
        }
        for i, bucket in enumerate(buckets, 1)
    ]
    
    return actors


def best_rated_genres(es_client, n=10, index_name="movies"):
    """Retourne les genres les mieux notés en moyenne."""
    
    aggs = {
        "genres_agg": {
            "terms": {"field": "genres", "size": 100},
            "aggs": {
                "avg_rating": {"avg": {"field": "rating"}},
                "min_rating": {"min": {"field": "rating"}},
                "max_rating": {"max": {"field": "rating"}}
            }
        }
    }
    
    result = es_client.search(index=index_name, size=0, aggs=aggs)
    buckets = result["aggregations"]["genres_agg"]["buckets"]
    
    # Trier par note moyenne décroissante
    sorted_buckets = sorted(buckets, key=lambda x: x["avg_rating"]["value"], reverse=True)[:n]
    
    genres = [
        {
            "rank": i,
            "name": bucket["key"],
            "avg_rating": round(bucket["avg_rating"]["value"], 2),
            "min_rating": round(bucket["min_rating"]["value"], 2),
            "max_rating": round(bucket["max_rating"]["value"], 2),
            "film_count": bucket["doc_count"]
        }
        for i, bucket in enumerate(sorted_buckets, 1)
    ]
    
    return genres


def rating_distribution(es_client, index_name="movies"):
    """Retourne la distribution des notes."""
    
    aggs = {
        "rating_dist": {
            "histogram": {"field": "rating", "interval": 0.5, "min_doc_count": 1}
        }
    }
    
    result = es_client.search(index=index_name, size=0, aggs=aggs)
    buckets = result["aggregations"]["rating_dist"]["buckets"]
    
    distribution = [
        {
            "rating_range": f"{bucket['key']:.1f}-{bucket['key']+0.5:.1f}",
            "count": bucket["doc_count"]
        }
        for bucket in buckets
    ]
    
    return distribution


def years_with_most_releases(es_client, n=10, index_name="movies"):
    """Retourne les années avec le plus de sorties de films."""
    
    aggs = {
        "releases_by_year": {
            "terms": {"field": "year", "size": n, "order": {"_count": "desc"}}
        }
    }
    
    result = es_client.search(index=index_name, size=0, aggs=aggs)
    buckets = result["aggregations"]["releases_by_year"]["buckets"]
    
    years = [
        {
            "year": int(bucket["key"]),
            "count": bucket["doc_count"]
        }
        for bucket in buckets
    ]
    
    return sorted(years, key=lambda x: x["year"])
