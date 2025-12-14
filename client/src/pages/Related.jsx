import { useState } from 'react';
import '../index.css'; 

function Related() {
  const [input, setInput] = useState('');
  const [sourceMovie, setSourceMovie] = useState(null); 
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // 1. NEW: State for the popup
  const [selectedMovie, setSelectedMovie] = useState(null);

  const findRelated = async () => {
    if (!input) return;
    setLoading(true);
    setSourceMovie(null);
    setMovies([]);

    try {
      const response = await fetch('https://jain-mayukh-movieback.hf.space/similar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: input })
      });
      
      const data = await response.json();
      
      if (data.error) {
        alert("Movie not found!");
      } else {
        setSourceMovie({ title: data.searched_for, overview: data.searched_plot });
        setMovies(data.results);
      }
    } catch (error) {
      console.error("Error:", error);
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <div style={{textAlign: 'center', marginBottom: '3rem'}}>
        <h1>🔗 Movie Chain</h1>
        <p className="subtitle">Type a movie you love. We'll find its "Soulmates."</p>
      </div>

      <div className="search-container">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. The Dark Knight..."
          onKeyDown={(e) => e.key === 'Enter' && findRelated()}
        />
        <button onClick={findRelated} disabled={loading}>
          {loading ? 'Analyzing...' : 'Find Matches'}
        </button>
      </div>

      {sourceMovie && (
        <div className="ai-box" style={{borderLeft: '4px solid #ab47bc'}}>
          <div className="ai-header">
            <span>🎬</span> 
            <span>Based on: {sourceMovie.title}</span>
          </div>
          <p style={{fontSize: '0.9rem', opacity: 0.8}}>{sourceMovie.overview}</p>
        </div>
      )}

      <div className="movie-grid">
        {movies.map((movie, index) => (
          <div 
            key={index} 
            className="card" 
            style={{animationDelay: `${index * 100}ms`}}
            // 2. NEW: Add Click Handler
            onClick={() => setSelectedMovie(movie)}
          >
            <div className="poster-wrapper">
              <img src={movie.poster_path} alt={movie.title} />
              <div className="score-badge">{(movie.score * 100).toFixed(0)}% Match</div>
            </div>
            <div className="card-content">
              <h3>{movie.title}</h3>
              <p>{movie.overview}</p>
            </div>
          </div>
        ))}
      </div>

      {/* 3. NEW: Paste the Modal JSX here */}
      {selectedMovie && (
        <div className="modal-overlay" onClick={() => setSelectedMovie(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedMovie(null)}>×</button>
            
            <img className="modal-poster" src={selectedMovie.poster_path} alt={selectedMovie.title} />
            
            <div className="modal-info">
              <h2 style={{marginTop: 0, fontSize: '2rem'}}>{selectedMovie.title}</h2>
              
              <div className="meta-tags">
                <span className="tag">📅 {selectedMovie.release_date || 'N/A'}</span>
                <span className="tag">⭐ {selectedMovie.vote_average}/10</span>
                <span className="tag" style={{background: '#4ade8020', color: '#4ade80'}}>
                  Match: {(selectedMovie.score * 100).toFixed(0)}%
                </span>
              </div>

              <p style={{lineHeight: 1.8, color: '#ddd', fontSize: '1.1rem'}}>
                {selectedMovie.overview}
              </p>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default Related;