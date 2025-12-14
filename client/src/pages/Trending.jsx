import { useState, useEffect } from 'react';
import '../index.css'; 

function Trending() {
  const [movies, setMovies] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);

  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const response = await fetch('https://jain-mayukh-movieback.hf.space/trending', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        setMovies(data.results);
      } catch (error) {
        console.error("Error fetching trending:", error);
      }
    };
    fetchTrending();
  }, []);

  return (
    <div className="app-container">
      <div style={{textAlign: 'center', marginBottom: '3rem'}}>
        <h1>🔥 Trending Now</h1>
        <p className="subtitle">The top 10 movies the world is watching this week.</p>
      </div>

      <div className="movie-grid">
        {movies.map((movie, index) => (
          <div 
            key={index} 
            className="card" 
            style={{animationDelay: `${index * 100}ms`}}
            onClick={() => setSelectedMovie(movie)}
          >
            <div className="poster-wrapper">
              <img src={movie.poster_path} alt={movie.title} />
              {/* Show Rating instead of "Match" for trending */}
              <div className="score-badge" style={{background: '#ff9f43', color: 'black'}}>
                ★ {movie.vote_average.toFixed(1)}
              </div>
            </div>
            <div className="card-content">
              <h3>{movie.title}</h3>
              <p>{movie.overview}</p>
            </div>
          </div>
        ))}
      </div>

      {/* MODAL POPUP (Reused) */}
      {selectedMovie && (
        <div className="modal-overlay" onClick={() => setSelectedMovie(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedMovie(null)}>×</button>
            <img className="modal-poster" src={selectedMovie.poster_path} alt={selectedMovie.title} />
            <div className="modal-info">
              <h2 style={{marginTop: 0, fontSize: '2rem'}}>{selectedMovie.title}</h2>
              <div className="meta-tags">
                <span className="tag">📅 {selectedMovie.release_date}</span>
                <span className="tag">⭐ {selectedMovie.vote_average}/10</span>
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

export default Trending;