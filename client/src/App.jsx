import { useState } from 'react'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [movies, setMovies] = useState([])
  const [explanation, setExplanation] = useState('') // <--- New State
  const [loading, setLoading] = useState(false)

  const searchMovies = async () => {
    if (!query) return
    setLoading(true)
    setExplanation('') // Clear old explanation
    setMovies([])

    try {
      const response = await fetch('http://127.0.0.1:8000/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, limit: 10})
      })
      const data = await response.json()
      setMovies(data.results)
      setExplanation(data.explanation) // <--- Set the AI text
    } catch (error) {
      console.error("Error:", error)
      alert("Backend not running?")
    }
    setLoading(false)
  }

  return (
    <div className="container">
      <h1>🎬 AI Movie Recommender</h1>
      <p style={{marginBottom: '20px', color: '#888'}}>
        Powered by RAG & Gemini
      </p>
      
      <div className="search-box">
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., A psychological thriller with a twist..."
          onKeyDown={(e) => e.key === 'Enter' && searchMovies()}
        />
        <button onClick={searchMovies} disabled={loading}>
          {loading ? 'Thinking...' : 'Ask AI'}
        </button>
      </div>

      {/* NEW: AI Explanation Box */}
      {explanation && (
        <div style={{
          background: '#2a2a40', 
          padding: '20px', 
          borderRadius: '12px', 
          marginBottom: '30px',
          borderLeft: '4px solid #646cff',
          textAlign: 'left'
        }}>
          <h3 style={{marginTop: 0, color: '#a5a6f6'}}>🤖 AI's Pick:</h3>
          <p style={{margin: 0, fontSize: '1.1rem', lineHeight: '1.6'}}>{explanation}</p>
        </div>
      )}

      <div className="movie-grid">
        {movies.map((movie, index) => (
          <div key={index} className="card">
            <img src={movie.poster_path} alt={movie.title} />
            <div className="card-content">
              <div className="match-score">
                Match: {(movie.score * 100).toFixed(0)}%
              </div>
              <h3>{movie.title}</h3>
              <p>{movie.overview}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App