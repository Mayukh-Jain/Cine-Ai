import { useState } from 'react'
// import './index.css'

function Search() {
  const [query, setQuery] = useState('')
  const [movies, setMovies] = useState([])
  const [explanation, setExplanation] = useState('')
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  
  // NEW: State for the popup
  const [selectedMovie, setSelectedMovie] = useState(null)

  const searchMovies = async () => {
    if (!query) return
    setLoading(true)
    setSearched(true)
    setExplanation('') 
    setMovies([])

    try {
      const response = await fetch('http://127.0.0.1:8000/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, limit: 10 }) 
      })
      const data = await response.json()
      setMovies(data.results)
      setExplanation(data.explanation)
    } catch (error) {
      console.error("Error:", error)
      alert("Backend is offline!")
    }
    setLoading(false)
  }

  return (
    <div className="app-container">
      
        <h1>✨ Cine-AI</h1>
        <p className="subtitle">Describe a vibe, a plot, or a feeling.</p>
      
      
      <div className="search-container">
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., A cyberpunk detective story..."
          onKeyDown={(e) => e.key === 'Enter' && searchMovies()}
        />
        <button onClick={searchMovies} disabled={loading}>
          {loading ? '🔮...' : '🚀 Explore'}
        </button>
      </div>

      {explanation && (
        <div className="ai-box">
          <div className="ai-header"><span>🤖</span> <span>AI Insight</span></div>
          <p>{explanation}</p>
        </div>
      )}

      <div className="movie-grid">
        {movies.map((movie, index) => (
          <div 
            key={index} 
            className="card" 
            style={{animationDelay: `${index * 100}ms`}}
            // NEW: Open popup on click
            onClick={() => setSelectedMovie(movie)}
          >
            <div className="poster-wrapper">
              <img src={movie.poster_path} alt={movie.title} />
              <div className="score-badge">{(movie.score * 100).toFixed(0)}%</div>
            </div>
            <div className="card-content">
              <h3>{movie.title}</h3>
              <p>{movie.overview}</p>
            </div>
          </div>
        ))}
      </div>

      {/* --- NEW: POPUP MODAL --- */}
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
  )
}

export default Search