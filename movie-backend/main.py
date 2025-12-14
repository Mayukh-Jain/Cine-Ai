import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import google.generativeai as genai

# 1. Load Environment Variables
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# 2. App Setup
app = FastAPI()

# Enable CORS (Crucial for Vercel Frontend to talk to this Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Initialize Clients
print("🧠 Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("🌐 Connecting to Database...")
if QDRANT_URL and QDRANT_API_KEY:
    # Production Mode (Cloud)
    qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
else:
    # Development Mode (Local)
    qdrant = QdrantClient(path="./qdrant_data")

COLLECTION_NAME = "movies"
llm = genai.GenerativeModel('gemini-1.5-flash')

# --- DATA MODELS ---
class SearchQuery(BaseModel):
    query: str
    limit: int = 10

class MovieInput(BaseModel):
    title: str
    limit: int = 10

# --- ENDPOINTS ---

@app.get("/")
def health_check():
    """Simple check to see if the server is running"""
    return {"status": "running", "service": "Movie AI Backend"}

@app.get("/trending")
def get_trending_movies():
    """Fetches global top 10 movies from TMDB"""
    if not TMDB_API_KEY:
        return {"error": "TMDB API Key missing"}

    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        results = []
        for movie in data.get('results', [])[:10]:
            results.append({
                "title": movie.get('title'),
                "overview": movie.get('overview'),
                "score": movie.get('vote_average', 0) / 10, # Normalize to 0-1
                "poster_path": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}",
                "release_date": movie.get('release_date', 'Unknown'),
                "vote_average": movie.get('vote_average', 0)
            })
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

@app.post("/recommend")
def recommend_movies(search: SearchQuery):
    """Vector Search + RAG (AI Explanation)"""
    try:
        # 1. Vectorize Query
        query_vector = model.encode(search.query).tolist()

        # 2. Search Qdrant
        search_result = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=search.limit
        )

        # 3. Format Results & Prepare Context for AI
        results = []
        context_text = ""
        
        for i, hit in enumerate(search_result.points):
            movie_title = hit.payload.get('title')
            overview = hit.payload.get('overview')
            
            results.append({
                "title": movie_title,
                "overview": overview,
                "score": hit.score,
                "poster_path": f"https://image.tmdb.org/t/p/w500{hit.payload.get('poster_path')}",
                "release_date": hit.payload.get('release_date', 'Unknown'),
                "vote_average": hit.payload.get('vote_average', 0)
            })

            # Only send top 3 to Gemini to save time
            if i < 3:
                context_text += f"Movie {i+1}: {movie_title}\nPlot: {overview}\n\n"

        # 4. Generate AI Explanation
        prompt = f"""
        The user asked: "{search.query}"
        Here are the best matches:
        {context_text}
        
        Recommend the #1 best fit and explain why in 2 exciting sentences. 
        Don't mention the other movies.
        """
        try:
            ai_response = llm.generate_content(prompt)
            explanation = ai_response.text
        except:
            explanation = "Here are the best matches I found for you!"

        return {"results": results, "explanation": explanation}

    except Exception as e:
        return {"error": str(e), "results": []}

@app.post("/similar")
def find_similar_movies(input_data: MovieInput):
    """Find movies similar to a specific movie title"""
    if not TMDB_API_KEY:
        return {"error": "TMDB API Key missing"}

    try:
        # 1. Find the source movie on TMDB
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={input_data.title}"
        resp = requests.get(search_url)
        data = resp.json()

        if not data.get('results'):
            return {"error": "Movie not found on TMDB", "results": []}
        
        target_movie = data['results'][0]
        target_plot = target_movie['overview']
        target_title = target_movie['title']
        
        # 2. Vectorize the SOURCE movie's plot
        query_text = f"{target_title}: {target_plot}"
        query_vector = model.encode(query_text).tolist()

        # 3. Search Qdrant
        search_result = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=input_data.limit + 1 # +1 buffer to remove self
        )

        results = []
        for hit in search_result.points:
            # Skip the movie itself if it appears in results
            if hit.payload.get('title') == target_title:
                continue
                
            results.append({
                "title": hit.payload.get('title'),
                "overview": hit.payload.get('overview'),
                "score": hit.score,
                "poster_path": f"https://image.tmdb.org/t/p/w500{hit.payload.get('poster_path')}",
                "release_date": hit.payload.get('release_date', 'Unknown'),
                "vote_average": hit.payload.get('vote_average', 0)
            })

        return {
            "searched_for": target_title,
            "searched_plot": target_plot,
            "results": results[:input_data.limit]
        }
    except Exception as e:
        return {"error": str(e)}