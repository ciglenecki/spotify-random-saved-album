import random
import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
ID = os.getenv("ID")
SEC = os.getenv("SEC")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=ID,
        client_secret=SEC,
        redirect_uri="http://127.0.0.1:9090",
        scope="user-library-read",
    )
)

results = sp.current_user_saved_albums()
albums = results['items']
while results['next']:
    results = sp.next(results)
    albums.extend(results['items'])

random_index = random.randint(0, len(albums) - 1)
album = albums[random_index]["album"]
album_name = album["name"]
album_url = album["external_urls"]["spotify"]

# print(album_name, album_url) # If you want to print album's name as well
print(album_url)
