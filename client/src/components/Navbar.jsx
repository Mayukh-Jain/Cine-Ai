import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/">✨ Cine-AI</Link>
      </div>
      <div className="nav-links">
        
        <Link to="/">Home</Link>
        <Link to="/trending">🔥 Trending</Link> {/* NEW LINK */}
        <Link to="/search" className="nav-btn">AI Search</Link>
        <Link to="/related" className="nav-btn" style={{background: '#ab47bc'}}>Similar Movies</Link>
      </div>
    </nav>
  );
}

export default Navbar;