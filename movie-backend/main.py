import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import google.generativeai as genai
# import requests # <--- 1. NEW IMPORT

# 1. Load Keys
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- SETUP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Models
model = SentenceTransformer('all-MiniLM-L6-v2')
qdrant = QdrantClient(path="./qdrant_data") 
COLLECTION_NAME = "movies"
llm = genai.GenerativeModel('gemini-2.5-flash-lite') # Fast & Free

class SearchQuery(BaseModel):
    query: str
    limit: int = 10

@app.post("/recommend")
def recommend_movies(search: SearchQuery):
    # 1. Vector Search (Retrieval)
    query_vector = model.encode(search.query).tolist()
    
    search_result = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=search.limit
    )

    # 2. Prepare Context for LLM (The "R" in RAG)
    results = []
    context_text = ""
    
    for i, hit in enumerate(search_result.points):
        movie_title = hit.payload['title']
        overview = hit.payload['overview']
        
        # Add to results list for frontend
        results.append({
            "title": hit.payload['title'],
            "overview": hit.payload['overview'],
            "score": hit.score,
            "poster_path": f"https://image.tmdb.org/t/p/w500{hit.payload['poster_path']}",
            # --- NEW FIELDS ---
            "release_date": hit.payload.get('release_date', 'Unknown'),
            "vote_average": hit.payload.get('vote_average', 0)
        })

        # Add to Context String (only top 3 to save tokens)
        if i < 3:
            context_text += f"Movie {i+1}: {movie_title}\nPlot: {overview}\n\n"

    # 3. Generate Explanation (The "G" in RAG)
    # We ask the LLM to act as a movie critic using ONLY the data we found.
    prompt = f"""
    You are an enthusiastic movie expert. The user asked for: "{search.query}".
    
    Here are the best matches from our database:
    {context_text}
    
    Based ONLY on these movies, recommend the best one and explain why it fits their request. 
    Keep it short (2-3 sentences) and exciting.
    """
    
    try:
        response = llm.generate_content(prompt)
        ai_explanation = response.text
    except Exception as e:
        ai_explanation = "I found these movies, but my brain is a bit tired to explain them right now!"

    # Return both the raw data AND the AI explanation
    return {
        "results": results,
        "explanation": ai_explanation
    }


import requests # <--- 1. NEW IMPORT
# ... keep your existing imports ...

# ... keep your existing setup ...
TMDB_API_KEY = os.getenv("TMDB_API_KEY") # Ensure this is loaded

class MovieInput(BaseModel):
    title: str
    limit: int = 10

@app.post("/similar")
def find_similar_movies(input_data: MovieInput):
    # 1. Search TMDB to find the movie the user is talking about
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={input_data.title}"
    resp = requests.get(search_url)
    data = resp.json()

    if not data['results']:
        return {"error": "Movie not found on TMDB", "results": []}
    
    # Get the best match (first result)
    target_movie = data['results'][0]
    target_plot = target_movie['overview']
    target_title = target_movie['title']
    
    # 2. Vectorize THIS plot (The "Anchor" Movie)
    # We combine title + plot to make the search accurate
    query_text = f"{target_title}: {target_plot}"
    query_vector = model.encode(query_text).tolist()

    # 3. Search Qdrant for similar movies
    search_result = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=input_data.limit + 1 # Fetch 1 extra in case we find the same movie
    )

    results = []
    for hit in search_result.points:
        # Filter out the movie itself if it's in our DB
        if hit.payload['title'] == target_title:
            continue
            
        results.append({
            "title": hit.payload['title'],
            "overview": hit.payload['overview'],
            "score": hit.score,
            "poster_path": f"https://image.tmdb.org/t/p/w500{hit.payload['poster_path']}",
            "release_date": hit.payload.get('release_date', 'Unknown'),
            "vote_average": hit.payload.get('vote_average', 0)
        })

    return {
        "searched_for": target_title,
        "searched_plot": target_plot,
        "results": results[:input_data.limit] # Return strictly the limit
    }


# ... inside main.py ...

@app.get("/trending")
def get_trending_movies():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    results = []
    for movie in data['results'][:10]: # Top 10 only
        results.append({
            "title": movie['title'],
            "overview": movie['overview'],
            # We map TMDB rating (0-10) to our "score" format (0-1) for consistency
            "score": movie['vote_average'] / 10, 
            "poster_path": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
            "release_date": movie.get('release_date', 'Unknown'),
            "vote_average": movie.get('vote_average', 0)
        })
        
    return {"results": results}