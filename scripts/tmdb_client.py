import requests
from scripts.config import API_KEY, BASE_URL, DEFAULT_LANGUAGE

def fetch_popular_movies(page=1):
    """Fetches a list of popular movies from TMDB."""
    url = f"{BASE_URL}/movie/popular"
    params = {"api_key": API_KEY, "language": DEFAULT_LANGUAGE, "page": page}
    return requests.get(url, params=params).json()

def search_movie(title):
    """Searches for a movie by title."""
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "language": DEFAULT_LANGUAGE, "query": title}
    return requests.get(url, params=params).json()

def get_movie_details(movie_id):
    """Fetches detailed information about a specific movie by its ID."""
    url = f"{BASE_URL}/movie/{movie_id}?append_to_response=credits"
    params = {"api_key": API_KEY, "language": DEFAULT_LANGUAGE}
    return requests.get(url, params=params).json()

def get_all_movies_by_ids(movie_ids):
    """Fetches detailed information for multiple movies
       by their IDs."""
    movies = []
    for movie_id in movie_ids:
        details = get_movie_details(movie_id)
        movies.append(details)

    return movies
