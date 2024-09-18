# CineReduxAPI
CineRedux is a Flask-based REST API that provides information about trending movies, movie ratings (from Rotten Tomatoes and TMDB), and trailers. It also includes search functionality to find similar movies. The API is designed to fetch movie data from TMDB and Rotten Tomatoes, and it supports secure API access through an API key.

## Features

- **Trending Movies**: Get the top 10 trending movies from TMDB.
- **Movie Search**: Search for movies by title and retrieve detailed information about similar titles.
- **Rotten Tomatoes Ratings**: Get movie ratings from Rotten Tomatoes.
- **Movie Trailers**: Retrieve official movie trailers from TMDB.

## Requirements

- Python 3.7+
- Flask
- Requests
- BeautifulSoup4
- Python-dotenv

## Environment Variables

rename the `.env.sample` file to `.env` and edit the following keys accordingly:

```bash
expected_key=YOUR_SECURE_API_KEY
api_key=YOUR_TMDB_API_KEY
```
## Installation
1. Git clone the repository:</br> 
```
git clone https://github.com/CineRedux/CineReduxAPI.git
cd CineReduxAPI
```
2. Install dependencies: </br> 
```
pip install -r requirements.txt
```
3. Set up environment variables in the ``` .env``` file as shown above
4. Run the app: </br>
```
python app.py
```
By default, the app will be available at http://127.0.0.1:8080/

## Example usage
### Get trending movies
```
curl "http://127.0.0.1:8080/api/trending?api_key=YOUR_API_KEY"
```
### Search for movie
```
curl "http://127.0.0.1:8080/api/movie?query=Inception&api_key=YOUR_API_KEY"
```
