// URL de l'API FastAPI
const API_BASE = 'http://127.0.0.1:8001/api';

// DOM Elements
const navLinks = document.querySelectorAll('.nav-links a');
const views = document.querySelectorAll('.view');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsHeader = document.getElementById('resultsHeader');
const resultsGrid = document.getElementById('resultsGrid');
const statsGrid = document.getElementById('statsGrid');
const similarModal = document.getElementById('similarModal');
const closeModalBtn = document.getElementById('closeModal');
const similarGrid = document.getElementById('similarGrid');

// Historique de navigation
let viewHistory = [];

function switchView(viewId) {
    views.forEach(v => v.classList.remove('active'));
    document.getElementById(`view-${viewId}`).classList.add('active');
    window.scrollTo(0, 0);
}

function goBack() {
    if (viewHistory.length > 0) {
        const prevView = viewHistory.pop();
        switchView(prevView);
    } else {
        switchView('search');
    }
}

// Navigation
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Update active link
        navLinks.forEach(l => l.classList.remove('active'));
        e.target.classList.add('active');
        
        // Show view
        const viewId = e.target.getAttribute('data-view');
        viewHistory = []; // Reset history
        switchView(viewId);

        // Load stats if stats view
        if (viewId === 'stats') {
            loadStats();
        }
    });
});

// Create Movie Card HTML
function createMovieCard(movie) {
    const ratingClass = movie.rating >= 7.5 ? 'high' : (movie.rating >= 6 ? 'medium' : 'low');
    const genres = movie.genres ? movie.genres.map(g => `<span class="card-genre">${g}</span>`).join('') : '';
    
    // Placeholder si pas d'image
    const imgUrl = movie.image_url || 'https://placehold.co/400x600/1a1a2e/ffffff?text=Pas+d\'affiche';

    return `
        <div class="card">
            <div class="card-img-wrapper" style="cursor:pointer;" onclick="loadMovie('${movie.id}')">
                <img src="${imgUrl}" alt="${movie.title}" loading="lazy" onerror="this.src='https://placehold.co/400x600/1a1a2e/ffffff?text=Erreur+Image'">
                <div class="card-rating ${ratingClass}">⭐ ${movie.rating || 'N/A'}</div>
            </div>
            <div class="card-content">
                <div class="card-title" style="cursor:pointer;" onclick="loadMovie('${movie.id}')">${movie.title}</div>
                <div class="card-year">${movie.year || 'N/A'} • ${Math.floor((movie.running_time_secs||0) / 60)} min</div>
                <div class="card-genres">${genres}</div>
            </div>
        </div>
    `;
}

// Search
async function performSearch() {
    const query = searchInput.value.trim();
    if (!query) return;

    // UI State
    resultsGrid.innerHTML = '';
    resultsHeader.innerHTML = '';
    loadingIndicator.classList.add('active');

    try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        loadingIndicator.classList.remove('active');
        
        resultsHeader.innerHTML = `Résultats pour "${query}" <span style="margin-left:10px; padding:2px 8px; background:rgba(255,255,255,0.1); border-radius:10px; font-size:0.8rem;">${data.total} trouvés</span>`;
        
        if (data.movies.length === 0) {
            resultsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align:center; color: var(--text-secondary);">Aucun film trouvé.</p>';
        } else {
            resultsGrid.innerHTML = data.movies.map(m => createMovieCard(m)).join('');
        }
    } catch (error) {
        console.error(error);
        loadingIndicator.classList.remove('active');
        resultsHeader.innerHTML = '<span style="color: #f87171;">Erreur lors de la communication avec l\'API. L\'API est-elle lancée ?</span>';
    }
}

searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});

// Load Similar Movies
async function loadSimilar(movieId) {
    similarModal.classList.add('active');
    similarGrid.innerHTML = '<div class="loading active"><div class="spinner"></div><p>Recherche des recommandations...</p></div>';

    try {
        const response = await fetch(`${API_BASE}/recommend/${movieId}`);
        const data = await response.json();

        if (data.movies.length === 0) {
            similarGrid.innerHTML = '<p style="grid-column: 1/-1; text-align:center;">Aucune recommandation trouvée pour ce film.</p>';
        } else {
            similarGrid.innerHTML = data.movies.map(m => createMovieCard(m)).join('');
        }
    } catch (error) {
        console.error(error);
        similarGrid.innerHTML = '<p style="color:#f87171;">Erreur lors du chargement des films similaires.</p>';
    }
}

closeModalBtn.addEventListener('click', () => {
    similarModal.classList.remove('active');
});
similarModal.addEventListener('click', (e) => {
    if (e.target === similarModal) similarModal.classList.remove('active');
});

// Load Stats
async function loadStats() {
    statsGrid.innerHTML = '<div class="loading active" style="grid-column:1/-1;"><div class="spinner"></div><p>Calcul des statistiques...</p></div>';
    
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();

        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${data.total_films.toLocaleString()}</div>
                <div class="stat-label">Films Indexés</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">⭐ ${data.avg_rating}</div>
                <div class="stat-label">Note Moyenne</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">⏱️ ${data.avg_duration_min}</div>
                <div class="stat-label">Durée Moyenne (min)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="font-size:1.5rem; margin-top:10px;">${data.best_movie}</div>
                <div class="stat-label">Meilleur Film</div>
            </div>
        `;
    } catch (error) {
        console.error(error);
        statsGrid.innerHTML = '<p style="color:#f87171;">Impossible de charger les statistiques.</p>';
    }
}

// Load Movie Details
async function loadMovie(movieId) {
    viewHistory.push(document.querySelector('.view.active').id.replace('view-', ''));
    switchView('movie');
    
    const container = document.getElementById('movieDetailContainer');
    const similarGrid = document.getElementById('movieSimilarGrid');
    
    container.innerHTML = '<div class="loading active"><div class="spinner"></div><p>Chargement du film...</p></div>';
    similarGrid.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/movies/${movieId}`);
        const movie = await response.json();
        
        const imgUrl = movie.image_url || 'https://placehold.co/400x600/1a1a2e/ffffff?text=Pas+d\'affiche';
        
        // Generate clickable tags
        const actorsHtml = (movie.actors || []).map(a => `<span class="clickable-tag" onclick="loadPerson('actor', '${a}')">${a}</span>`).join('');
        const directorsHtml = (movie.directors || []).map(d => `<span class="clickable-tag" onclick="loadPerson('director', '${d}')">${d}</span>`).join('');
        
        container.innerHTML = `
            <div class="movie-detail-content">
                <img src="${imgUrl}" class="movie-poster" alt="${movie.title}">
                <div class="movie-info">
                    <h1>${movie.title}</h1>
                    <div class="movie-meta">
                        <span>⭐ ${movie.rating || 'N/A'}/10</span>
                        <span>📅 ${movie.year || 'N/A'}</span>
                        <span>⏱️ ${Math.floor((movie.running_time_secs||0)/60)} min</span>
                    </div>
                    <p class="movie-plot">${movie.plot || 'Aucun synopsis disponible.'}</p>
                    
                    <div class="tags-section">
                        <h3>Réalisateur(s)</h3>
                        <div>${directorsHtml || '-'}</div>
                    </div>
                    <div class="tags-section">
                        <h3>Casting</h3>
                        <div>${actorsHtml || '-'}</div>
                    </div>
                </div>
            </div>
        `;
        
        // Load similar movies automatically
        const simRes = await fetch(`${API_BASE}/recommend/${movieId}`);
        const simData = await simRes.json();
        similarGrid.innerHTML = simData.movies.length > 0 
            ? simData.movies.map(m => createMovieCard(m)).join('') 
            : '<p>Aucun film similaire trouvé.</p>';
            
    } catch (e) {
        container.innerHTML = '<p style="color:red;">Erreur de chargement du film.</p>';
    }
}

// Load Person (Actor or Director)
async function loadPerson(type, name) {
    viewHistory.push(document.querySelector('.view.active').id.replace('view-', ''));
    switchView('person');
    
    document.getElementById('personTitle').textContent = name;
    document.getElementById('personSubtitle').textContent = `Meilleurs films (${type === 'actor' ? 'Acteur' : 'Réalisateur'})`;
    
    const grid = document.getElementById('personMoviesGrid');
    grid.innerHTML = '<div class="loading active" style="grid-column:1/-1;"><div class="spinner"></div><p>Recherche des films...</p></div>';
    
    try {
        const response = await fetch(`${API_BASE}/${type}s/${encodeURIComponent(name)}/movies`);
        const data = await response.json();
        
        if (data.movies.length === 0) {
            grid.innerHTML = '<p style="grid-column: 1/-1;">Aucun film trouvé.</p>';
        } else {
            grid.innerHTML = data.movies.map(m => createMovieCard(m)).join('');
        }
    } catch (e) {
        grid.innerHTML = '<p style="color:red; grid-column:1/-1;">Erreur de chargement.</p>';
    }
}
