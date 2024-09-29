from flask import Flask, request, jsonify
import requests, re, json, os
from bs4 import BeautifulSoup
from string import punctuation
from dotenv import load_dotenv

load_dotenv()

class MovieAPI:
    def __init__(self):
        self.expected_api_key = os.getenv('expected_key')
        self.apikey = os.getenv('api_key')
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule('/', 'index', self.index, methods=['GET'])
        self.app.add_url_rule('/trending', 'get_popular', self.get_popular, methods=['GET'])
        self.app.add_url_rule('/movie', 'search_for_movie', self.search_for_movie, methods=['GET'])
        self.app.add_url_rule('/score', 'score', self.score, methods=['GET']) #ToDo - secure behind internal-call header!!

    def index(self):
        return jsonify(status=200, message='Welcome to CineRedux')

    def get_rotten_tomatoes_rating(self, query):
        formatted_query = re.sub(f"[{re.escape(punctuation)}]", '', query)
        formatted_query = re.sub(' ', '_', formatted_query)
        search_url = f"https://www.rottentomatoes.com/m/{formatted_query.lower()}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        search_response = requests.get(search_url, headers=headers)
        search_soup = BeautifulSoup(search_response.content, "html.parser")
        script_tag = search_soup.find("script", {"id": "media-scorecard-json"})
        if script_tag:
            script_data = json.loads(script_tag.string)
            if 'criticsScore' in script_data:
                rating_info = script_data['criticsScore']
                if rating_info['title'] == 'Tomatometer':
                    return {
                        rating_info.get('title'): {
                        "movie": query,
                        "ratingCount": rating_info.get('ratingCount'),
                        "ratingValue": rating_info.get('scorePercent'),
                        "reviewCount": rating_info.get('reviewCount')
                        }
                    }
        return None

    def get_trailer(self, id):
        url = f"https://api.themoviedb.org/3/movie/{id}/videos"
        params = {'api_key': self.apikey}
        response = requests.get(url, params)
        movies = response.json()
        for movie in movies['results']:
            if movie['type'] == "Trailer" and "Official Trailer" in movie['name']:
                yt_url = f"https://www.youtube.com/watch?v={movie['key']}"
                return yt_url

    def get_popular(self):
        provided_api_key = request.args.get('api_key')
        if provided_api_key != self.expected_api_key:
            return jsonify({"error": "Unauthorized access: Invalid API key"}), 401

        rating_url = f"http://127.0.0.1:8080/score?"
        url = "https://api.themoviedb.org/3/trending/movie/week"
        params = {'api_key': self.apikey}
        response = requests.get(url, params=params)
        movies = response.json()
        top_movies = []

        custom_header = {"X-Internal-Call": "true"}

        for index, movie in enumerate(movies['results'][:10]):
            title = re.sub('&', 'and', movie.get('title'))
            ratings_response = requests.get(rating_url, f"query={title}", headers=custom_header)
            if not ratings_response.status_code == 404:
                ratingType = "tomatometer"
                ratings = ratings_response.json()
                rating = ratings.get('Tomatometer').get('ratingValue')
            else:
                ratingType = "tmdbScore"
                rating = f"{round(movie.get('vote_average'), 2)}/10"
            
            movie_info = {
                'movie': index + 1,
                'title': movie.get('title'),
                'overview': movie.get('overview'),
                'year' : movie.get('release_date').split('-')[0],
                'id': movie['id'],
                ratingType: rating,
                'poster': f"{self.image_base_url}{movie.get('poster_path')}",
                'backdrop': f"{self.image_base_url}{movie.get('backdrop_path')}",
                'trailer': self.get_trailer(movie['id'])
            }
            top_movies.append(movie_info)
        
        return {'TopMovies': top_movies}

    def search_for_movie(self):
        query = request.args.get('query')
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        provided_api_key = request.args.get('api_key')
        if provided_api_key != self.expected_api_key:
            return jsonify({"error": "Unauthorized access: Invalid API key"}), 401
        
        url = "https://api.themoviedb.org/3/search/movie"
        params = {'api_key': self.apikey, 'query': query}
        movie_results = []
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json()
            movies = results.get('results')
            for index, movie in enumerate(movies[:10]):
                movie_info = {
                    'movie': index + 1,
                    'title': movie.get('title'),
                    'overview': movie.get('overview'),
                    'id': movie['id'],
                    'tmdbScore': f"{round(movie.get('vote_average'), 2)}/10",
                    'poster': f"{self.image_base_url}{movie.get('poster_path')}",
                    'trailer': self.get_trailer(movie['id'])
                }
                movie_results.append(movie_info)
            return {'SimilarMovies': movie_results}
        except requests.exceptions.RequestException as e:
            return jsonify({"error": "Movie not found"}), e

    def score(self):

        if request.headers.get("X-Internal-Call") != "true":
            return jsonify({"error": "Unauthorized access"}), 403

        query = request.args.get('query')
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        result = self.get_rotten_tomatoes_rating(query)
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Rating not found"}), 404

if __name__ == '__main__':
    api = MovieAPI()
    api.app.run('127.0.0.1', 8080, debug=True)
