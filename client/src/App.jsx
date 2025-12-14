import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Search from './pages/Search';
import Related from './pages/Related'; 
import Trending from './pages/Trending'; 
import './index.css';

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Navbar />
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/trending" element={<Trending />} />
            <Route path="/search" element={<Search />} />
            <Route path="/related" element={<Related />} /> {/* <--- Add Route */}
          </Routes>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;