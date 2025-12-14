import os
import time
import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# --- CONFIGURATION ---
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# CHANGE THESE NUMBERS TO ADD MORE MOVIES
START_PAGE = 101
END_PAGE = 200  # Fetching 50 pages = 1000 movies total

COLLECTION_NAME = "movies"

# --- SETUP ---
print("Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
qdrant = QdrantClient(path="./qdrant_data")

# Only create collection if it doesn't exist
if not qdrant.collection_exists(COLLECTION_NAME):
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

def fetch_and_vectorize():
    total_added = 0
    batch_points = []
    
    print(f"Fetching pages {START_PAGE} to {END_PAGE}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Student Project)",
        "Accept": "application/json"
    }

    for page in range(START_PAGE, END_PAGE + 1):
        url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={TMDB_API_KEY}&language=en-US&page={page}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Skipping page {page}: Status {response.status_code}")
                continue
                
            data = response.json()
            movies = data.get('results', [])

            for movie in movies:
                # 1. Skip movies with no overview (bad data)
                if not movie['overview']:
                    continue

                # 2. Vectorize
                text = f"{movie['title']}: {movie['overview']}"
                vector = model.encode(text).tolist()
                
                # 3. Create Payload
                payload = {
                    "title": movie['title'],
                    "overview": movie['overview'],
                    "poster_path": movie.get('poster_path', ""),
                    "vote_average": movie.get('vote_average', 0),
                    "release_date": movie.get('release_date', "")
                }
                
                # 4. CRITICAL FIX: Use the actual TMDB ID
                # This prevents duplicates. If ID 550 exists, it just updates it.
                batch_points.append(PointStruct(id=movie['id'], vector=vector, payload=payload))
                total_added += 1

            # Upload in batches of ~100 to save memory
            if len(batch_points) >= 100:
                qdrant.upsert(collection_name=COLLECTION_NAME, points=batch_points)
                print(f"--> Saved batch from page {page}")
                batch_points = []

            time.sleep(1) # Be nice to API

        except Exception as e:
            print(f"Error on page {page}: {e}")

    # Upload leftovers
    if batch_points:
        qdrant.upsert(collection_name=COLLECTION_NAME, points=batch_points)
    
    print(f"DONE! Processed {total_added} movies.")

if __name__ == "__main__":
    fetch_and_vectorize()
