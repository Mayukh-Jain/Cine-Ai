import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="hero-section">
      <div className="hero-content">
        <h1>Stop Scrolling.<br />Start <span className="highlight">Watching.</span></h1>
        <p className="hero-sub">
          Powered by <b>Artificial Intelligence</b> and <b>Vector Search</b>. 
          Don't search by genre—describe exactly what you want to feel.
        </p>
        <Link to="/search">
          <button className="cta-button">Find a Movie 🚀</button>
        </Link>
      </div>
    </div>
  );
}

export default Home;