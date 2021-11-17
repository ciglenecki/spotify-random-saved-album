import random
import os
from typing import Any, Tuple
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from pathlib import Path
from datetime import datetime, timedelta
import json
import argparse

DAYS_CACHE_HOLD = 10
CACHE_FILENAME_STR = ".cache.json"

parser = argparse.ArgumentParser()
parser.add_argument("--no-cache", dest="no_cache",
                    action="store_true", help="Force cache update")
parser.add_argument(
    "--update-cache", dest="update_cache", action="store_true", help="Force cache update"
)
parser.set_defaults(update_cache=False, no_cache=False)
args = parser.parse_args()

if args.no_cache and args.update_cache:
    parser.error("--update-cache and --no-cache can't be called together")

dir_path = os.path.dirname(os.path.realpath(__file__))
cache_filename = Path(dir_path, CACHE_FILENAME_STR)
cache_oauth_filename = Path(dir_path, ".cache")

load_dotenv(str(Path(dir_path, ".env")))
ID = os.getenv("ID")
SEC = os.getenv("SEC")


def get_album_name_url(album: Any) -> Tuple[str, str]:
    """ 
    Extracts album's name and url from the Album object
    https://developer.spotify.com/documentation/web-api/reference/#/operations/get-multiple-albums
    """
    album = album["album"]
    album_name = album["name"]
    album_url = album["external_urls"]["spotify"]
    return album_name, album_url


def save_albums_to_cache(albums, cache_filename):
    """
    Dumps albums object as JSON and saves it to cache file
    """
    with open(cache_filename, "w") as cache:
        cache.write(json.dumps(albums))
    cache.close()


def get_saved_albums():
    """
    Returns list of albums either by using existing cache file or by calling Spotify's API:
    [
        ("Album Name 1", "https://open.spotify.com/album/20r762YmB5HeofjMCiP"),
        ("Album Name 2", "https://open.spotify.com/album/98SDG9ngq9nDSlap"),
        ...
    ]
    """
    hold_timestamp = (datetime.today() -
                      timedelta(days=DAYS_CACHE_HOLD)).timestamp()
    if (
        not os.path.exists(cache_filename)
        or hold_timestamp > os.path.getmtime(cache_filename)
        or args.update_cache
        or args.no_cache
    ):
        """
        Spotify's API is called for the following conditions:
            1. cache doesn't exist
            2. cache is older than DAYS_CACHE_HOLD days (and now will be updated)
            3. cache is force updated by user via --update-cache argument
            4. cache isn't being used via --no-cache argument
        """
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=ID,
                client_secret=SEC,
                redirect_uri="http://127.0.0.1:9090",
                scope="user-library-read",
                cache_path=cache_oauth_filename)
        )

        results: Any = sp.current_user_saved_albums()
        albums = list(map(get_album_name_url, results["items"]))

        while results["next"]:
            results = sp.next(results)
            pair_name_url = list(map(get_album_name_url, results["items"]))
            albums.extend(pair_name_url)

        if not args.no_cache:
            save_albums_to_cache(albums, cache_filename)
        return albums
    else:
        """
        Cache file is read instead of calling Spotify's API (faster)
        """
        with open(cache_filename, "r") as cache:
            albums = json.load(cache)
        cache.close()
        return albums


albums = get_saved_albums()
random_index = random.randint(0, len(albums) - 1)
album_name, album_url = albums[random_index]

# print(name, url) # If you want to print album's name as well
print(album_url)
