def search_by_title(es_client, query_text, index_name="movies"):
    """3.1 Recherche simple par titre (match query)"""
    print(f"\n--- Recherche simple : '{query_text}' ---")
    
    query = {
        "match": {
            "title": query_text
        }
    }
    
    # On limite à 10 résultats comme souvent demandé
    results = es_client.search(index=index_name, query=query, size=10)
    
    for hit in results["hits"]["hits"]:
        source = hit["_source"]
        score = hit["_score"]
        # Formatage de l'affichage demandé
        print(f"[{score:.2f}] {source.get('title')} ({source.get('year')}) - Note: {source.get('rating')} - Réal: {', '.join(source.get('directors', []))}")
    
    return results


def search_advanced(es_client, title=None, actor=None, director=None, genre=None, min_rating=None, max_rating=None, year_from=None, year_to=None, index_name="movies"):
    """3.2 Recherche multi-critères (bool query)"""
    print("\n--- Recherche Avancée ---")
    
    must_clauses = []
    filter_clauses = []
    
    # Le 'must' influence le score de pertinence (recherche texte)
    if title: must_clauses.append({"match": {"title": title}})
    if actor: must_clauses.append({"match": {"actors": actor}})
    if director: must_clauses.append({"match": {"directors": director}})
    
    # Le 'filter' filtre de façon binaire (oui/non) sans calculer de score (plus rapide)
    if genre: filter_clauses.append({"term": {"genres": genre}})
    
    # Gestion de la fourchette de notes
    if min_rating is not None or max_rating is not None:
        rating_range = {}
        if min_rating is not None: rating_range["gte"] = min_rating
        if max_rating is not None: rating_range["lte"] = max_rating
        filter_clauses.append({"range": {"rating": rating_range}})
        
    # Gestion de la fourchette d'années
    if year_from is not None or year_to is not None:
        year_range = {}
        if year_from is not None: year_range["gte"] = year_from
        if year_to is not None: year_range["lte"] = year_to
        filter_clauses.append({"range": {"year": year_range}})

    # Assemblage de la requête booléenne
    query = {
        "bool": {
            "must": must_clauses,
            "filter": filter_clauses
        }
    }
    
    results = es_client.search(index=index_name, query=query, size=10)
    
    for hit in results["hits"]["hits"]:
        s = hit["_source"]
        print(f"{s.get('title')} ({s.get('year')}) - {s.get('genres')} - Note: {s.get('rating')}")
        
    return results


def search_plot(es_client, keywords, index_name="movies"):
    """3.3 Recherche dans le synopsis avec Highlight"""
    print(f"\n--- Recherche synopsis : '{keywords}' ---")
    
    query = {"match": {"plot": keywords}}
    
    # Configuration de la mise en évidence (highlight)
    highlight = {
        "fields": {
            "plot": {
                "fragment_size": 150, # Longueur de l'extrait
                "number_of_fragments": 1 # Nombre d'extraits à ramener
            }
        }
    }
    
    results = es_client.search(index=index_name, query=query, highlight=highlight, size=5)
    
    for hit in results["hits"]["hits"]:
        title = hit["_source"]["title"]
        # Récupération de l'extrait surligné (Elastic ajoute des balises <em> par défaut)
        plot_highlight = hit["highlight"]["plot"][0] if "highlight" in hit else "Pas d'extrait."
        print(f"🎬 {title}\n   Extrait : {plot_highlight}\n")


def search_fuzzy(es_client, query_text, fuzziness=2, index_name="movies"):
    """3.4 Recherche floue (tolérance aux fautes de frappe)"""
    print(f"\n--- Recherche floue : '{query_text}' ---")
    
    query = {
        "match": {
            "title": {
                "query": query_text,
                "fuzziness": fuzziness # Permet X erreurs (lettre manquante, inversée, etc.)
            }
        }
    }
    
    results = es_client.search(index=index_name, query=query, size=5)
    for hit in results["hits"]["hits"]:
        print(f"Trouvé : {hit['_source']['title']} (Score: {hit['_score']:.2f})")


def suggest_titles(es_client, prefix, index_name="movies"):
    """3.5 Auto-complétion basée sur un préfixe"""
    print(f"\n--- Suggestions pour : '{prefix}...' ---")
    
    query = {
        "prefix": {
            "title": {
                "value": prefix.lower() # Le prefix doit souvent être en minuscules avec l'analyzer standard
            }
        }
    }
    
    results = es_client.search(index=index_name, query=query, size=5)
    for hit in results["hits"]["hits"]:
        print(f"💡 {hit['_source']['title']}")

def recommend_similar_movies(es_client, movie_id, index_name="movies"):
    """Bonus : Recommandation (More Like This) basée sur le synopsis."""
    print(f"\n--- Films recommandés (Basés sur l'ambiance du synopsis) ---")
    
    query = {
        "more_like_this": {
            "fields": ["plot"], # On se concentre uniquement sur le synopsis
            "like": [
                {"_index": index_name, "_id": str(movie_id)} # L'ID du film de référence
            ],
            "min_term_freq": 1,
            "min_doc_freq": 1,
            "max_query_terms": 12 # Optimisation : on prend les 12 mots les plus significatifs du synopsis
        }
    }
    
    results = es_client.search(index=index_name, query=query, size=5)
    
    for hit in results["hits"]["hits"]:
        print(f"👉 {hit['_source']['title']} (Score de similarité : {hit['_score']:.2f})")
        
    return results


def global_search(es_client, query_text, index_name="movies"):
    """Recherche globale multi-champs avec pondération."""
    print(f"\n--- Recherche Globale : '{query_text}' ---")
    
    query = {
        "multi_match": {
            "query": query_text,
            "fields": [
                "title^3",       # Le titre compte triple
                "directors^2",   # Le réalisateur compte double
                "actors",        
                "plot"           # Le synopsis a un poids normal
            ]
        }
    }
    
    results = es_client.search(index=index_name, query=query, size=5)
    for hit in results["hits"]["hits"]:
        s = hit["_source"]
        print(f"[{hit['_score']:.2f}] {s.get('title')} - Réal: {', '.join(s.get('directors', []))}")
        
    return results


def search_best_rated(es_client, query_text, index_name="movies"):
    """Recherche textuelle boostée par la note du film."""
    print(f"\n--- Recherche pondérée par la note : '{query_text}' ---")
    
    query = {
        "function_score": {
            "query": {
                "match": {"title": query_text}
            },
            "field_value_factor": {
                "field": "rating",    
                "factor": 1.2,        
                "modifier": "log1p",
                "missing": 1.0  
            },
            "boost_mode": "multiply" # On multiplie le score texte par la note lissée
        }
    }
    
    results = es_client.search(index=index_name, query=query, size=5)
    for hit in results["hits"]["hits"]:
        print(f"{hit['_source']['title']} (Note: {hit['_source']['rating']} / Score ES: {hit['_score']:.2f})")
        
    return results


def search_exact_quote(es_client, quote, index_name="movies"):
    """Recherche une expression exacte dans le synopsis."""
    print(f"\n--- Recherche de citation exacte : '{quote}' ---")
    
    query = {
        "match_phrase": {
            "plot": quote
        }
    }
    
    results = es_client.search(index=index_name, query=query, size=5)
    for hit in results["hits"]["hits"]:
        print(f"🎬 {hit['_source']['title']}")
        
    return results