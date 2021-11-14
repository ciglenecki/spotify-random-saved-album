import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import os
from dotenv import load_dotenv

load_dotenv()
ID = os.getenv("ID")
SEC = os.getenv("SEC")


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=ID, client_secret=SEC, redirect_uri="http://127.0.0.1:9090", scope="user-library-read")
)

results = sp.current_user_saved_albums()
random_num = random.randint(0, len(results["items"]) - 1)
random_album = results["items"][random_num]["album"]
name = random_album["name"]
url = random_album["external_urls"]["spotify"]

print(url)
