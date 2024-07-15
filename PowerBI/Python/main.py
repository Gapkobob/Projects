import requests
import pandas as pd
from pathlib import Path

# TMDB API configuration
API_KEY = '5b8b9745fbdb42634074bec4d63c43c3'
BASE_URL = 'https://api.themoviedb.org/3'


# Function to fetch genre names from genre IDs
def get_genre_names():
    genre_url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=en-US"
    response = requests.get(genre_url)
    if response.status_code == 200:
        data = response.json()
        genres = {genre['id']: genre['name'] for genre in data['genres']}
        return genres
    return {}


# Function to fetch credits (director, up to 2 screenwriters, and top 5 actors)
def get_credits(movie_id):
    credits_url = f"{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}"
    response = requests.get(credits_url)
    if response.status_code == 200:
        data = response.json()
        credits = {
            'director': '',
            'screenwriters': [],
            'actors': []
        }
        # Fetch director
        for crew_member in data['crew']:
            if crew_member['job'] == 'Director':
                credits['director'] = crew_member['name']
                break

        # Fetch screenwriters (up to 2)
        count = 0
        for crew_member in data['crew']:
            if crew_member['job'] in ('Screenplay', 'Writer'):
                credits['screenwriters'].append(crew_member['name'])
                count += 1
                if count >= 2:
                    break

        # Fetch top 5 actors
        for actor in data['cast'][:5]:
            credits['actors'].append({
                'name': actor['name'],
                'profile_path': f"https://image.tmdb.org/t/p/w500{actor['profile_path']}" if actor[
                    'profile_path'] else None
            })

        return credits
    return None

movies_list = []

genres = get_genre_names()

#How many pages to read
for page in range(1, 401):
    url = f"{BASE_URL}/movie/top_rated?api_key={API_KEY}&language=en-US&page={page}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        for movie in data['results']:
            # Get details for each movie by ID
            movie_id = movie['id']
            movie_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US"
            movie_response = requests.get(movie_url)

            if movie_response.status_code == 200:
                movie_details = movie_response.json()

                # Replace genre IDs with genre names
                genre_names = [genres[genre['id']] for genre in movie_details['genres']]
                movie_details['genres'] = genre_names

                # Fetch credits (director, screenwriters, and actors)
                credits = get_credits(movie_id)
                if credits:
                    movie_details['director'] = credits['director']
                    movie_details['screenwriters'] = credits['screenwriters']
                    movie_details['actors'] = credits['actors']

                movies_list.append(movie_details)
            else:
                print(f'Failed to fetch details for movie ID {movie_id}: HTTP {movie_response.status_code}')
    else:
        print(f'Failed to fetch page {page}: HTTP {response.status_code}')
        break

# Prepare data for DataFrame
prepared_movies_list = []
for movie in movies_list:
    actors_info = []
    for actor in movie['actors']:
        actors_info.append(actor['name'])
        actors_info.append(actor['profile_path'] if actor['profile_path'] else "")

    prepared_movie = {
        'movie_id': movie['id'],
        'title': movie['title'],
        'poster_path': movie['poster_path'],
        'vote_average': movie['vote_average'],
        'vote_count': movie['vote_count'],
        'release_date': movie['release_date'],
        'genres': ', '.join(movie['genres']),
        'runtime': movie['runtime'],
        'budget': movie['budget'],
        'revenue': movie['revenue'],
        'director': movie['director'],
        'screenwriters': ', '.join(movie['screenwriters']),
        'actors': ', '.join(actors_info)
    }
    prepared_movies_list.append(prepared_movie)

# Convert the list of dictionaries to a DataFrame and save it to a file
movies_df = pd.DataFrame(prepared_movies_list)
columns_to_export = ['movie_id', 'title', 'poster_path', 'vote_average', 'vote_count', 'release_date', 'genres', 'runtime', 'budget', 'revenue', 'director', 'screenwriters', 'actors']
path = Path('output/1top_rated_movies_details.csv')
path.parent.mkdir(parents=True, exist_ok=True)
movies_df.to_csv(path, columns=columns_to_export, index=False)

print("DONE")