# 🎬 CinéSearch

CinéSearch est un moteur de recherche et d'analyse de films propulsé par **Elasticsearch** et **Python**. Il permet de rechercher, filtrer et analyser un dataset de plus de 5000 films avec des fonctionnalités avancées (recherche full-text, floue, suggestions, système de recommandation par similarité).

Ce projet contient plusieurs interfaces utilisateurs, notamment un tableau de bord analytique sous **Streamlit** et une véritable application Web SPA (Single Page Application) avec un backend **FastAPI**.

---

## 🛠️ Prérequis

- **Docker** et **Docker Compose** (pour Elasticsearch et Kibana)
- **Python 3.9+**

---

## 🚀 Installation & Démarrage

### 1. Lancer l'infrastructure (Elasticsearch)

Démarrez les conteneurs Elasticsearch et Kibana en arrière-plan à l'aide de Docker Compose :

```bash
docker compose up -d
```
*Patientez quelques secondes que le serveur Elasticsearch soit prêt.*

### 2. Configurer l'environnement Python

Créez un environnement virtuel et installez les dépendances :

```bash
# 1. Créer l'environnement virtuel
python -m venv .venv

# 2. Activer l'environnement
# Sur Linux / macOS :
source .venv/bin/activate
# Sur Windows :
# .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

### 3. Indexer les données

Avant de pouvoir rechercher, il faut créer l'index Elasticsearch et y insérer les films depuis le fichier JSON :

```bash
python -m src.indexer
```
*Cette commande va créer l'index, configurer les mappings (analyzers, ngrams pour les suggestions) et injecter les documents via l'API Bulk.*

---

## 🖥️ Utilisation

Le projet propose **trois** façons d'interagir avec les données :

### Option A : Interface Analytique (Streamlit) - 🌟 *Bonus*
Une interface complète pour la recherche et l'exploration visuelle des données (graphiques interactifs Plotly).
```bash
streamlit run src/app.py
```
*L'application s'ouvrira automatiquement dans votre navigateur.*

### Option B : Application Web Moderne (SPA + FastAPI) - 🌟 *Bonus*
Une véritable architecture web séparant le Backend de l'interface Frontend.

**Étape 1 : Lancer l'API Backend**
```bash
uvicorn src.api:app --reload --port 8001
```

**Étape 2 : Lancer le Frontend** (dans un nouveau terminal)
```bash
cd frontend
python -m http.server 3000
```
*Accédez ensuite à http://localhost:3000 dans votre navigateur pour une expérience dynamique sans rechargement de page.*

### Option C : Ligne de commande (CLI)
Pour une recherche rapide directement dans le terminal :
```bash
python main.py
```

---

## 📊 Kibana

Si vous souhaitez explorer les données manuellement ou créer des tableaux de bord, Kibana est disponible à l'adresse suivante :
👉 **http://localhost:5601**

---

## 🏗️ Structure du Projet

```text
cinesearch/
├── data/
│   └── movies.json         # Dataset source
├── src/
│   ├── indexer.py          # Logique d'indexation (mapping, analyzers)
│   ├── search.py           # Requêtes de recherche Elasticsearch
│   ├── analytics.py        # Agrégations et statistiques
│   ├── app.py              # Interface Streamlit
│   └── api.py              # Backend FastAPI
├── frontend/
│   ├── index.html          # Vue principale de la SPA
│   ├── style.css           # Design System (Vanilla CSS)
│   └── app.js              # Logique asynchrone (Appels API)
├── docker-compose.yml      # Infrastructure ES + Kibana
├── requirements.txt        # Dépendances Python
└── README.md               # Ce fichier
```