import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import google.generativeai as genai

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
            "title": movie_title,
            "overview": overview,
            "score": hit.score,
            "poster_path": f"https://image.tmdb.org/t/p/w500{hit.payload['poster_path']}"
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