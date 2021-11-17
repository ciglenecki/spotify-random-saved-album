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
FETCH_ALBUMS_LIMIT = 50
CACHE_FILENAME_STR = ".cache.json"
CACHE_OAUTH_FILENAME_STR = ".cache"
ENV_FILENAME_STR = ".env"
ENV_ID_STR = "ID"
ENV_SECRET_STR = "SEC"


parser = argparse.ArgumentParser()
parser.add_argument(
    "--no-cache",
    dest="no_cache",
    action="store_true",
    help=".cache.json won't be created",
)
parser.add_argument(
    "--update-cache",
    dest="update_cache",
    action="store_true",
    help="force update cache file",
)
parser.add_argument(
    "--output-name",
    dest="output_name",
    action="store_true",
    help="append album's name to output",
)
parser.add_argument(
    "--output-artist",
    dest="output_artist",
    action="store_true",
    help="append artist's name to output",
)
parser.add_argument(
    "--uri",
    dest="is_uri",
    action="store_true",
    help="return URI instead of URL. You can pass URI to spotify.start_playback(context_uri=URI) to play the album instantly (premium required)",
)
parser.set_defaults(update_cache=False, no_cache=False, output_name=False)
args = parser.parse_args()
if args.no_cache and args.update_cache:
    parser.error("--update-cache and --no-cache can't be called together")


dir_path = os.path.dirname(os.path.realpath(__file__))
cache_filename = Path(dir_path, CACHE_FILENAME_STR)
cache_oauth_filename = Path(dir_path, CACHE_OAUTH_FILENAME_STR)
env_filename = Path(dir_path, ENV_FILENAME_STR)


load_dotenv(env_filename)
ID = os.getenv(ENV_ID_STR)
SEC = os.getenv(ENV_SECRET_STR)


def get_album_name_url(album: Any) -> Tuple[str, str, str]:
    """
    Extracts album's name and url from the Album object
    https://developer.spotify.com/documentation/web-api/reference/#/operations/get-multiple-albums
    """
    album = album["album"]
    album_name = album["name"]
    album_url = album["external_urls"]["spotify"]
    album_artist = album["artists"][0]["name"]
    album_uri = album["artists"][0]["name"]
    return album_artist, album_name, album_url, album_uri


def get_albums_spotify_accumulate(spotify: spotipy.Spotify):
    """
    Accumulates all saved albums.
    "next" returns the next subset of albums in a while loop until all albums are accumulated.
    """
    subset_albums = spotify.current_user_saved_albums(limit=FETCH_ALBUMS_LIMIT)
    albums = list(map(get_album_name_url, subset_albums["items"]))
    while subset_albums["next"]:
        subset_albums = spotify.next(subset_albums)
        album_info = list(map(get_album_name_url, subset_albums["items"]))
        albums.extend(album_info)
    return albums


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
        ("Album Name 2", "https://open.spotify.com/album/98SDG9ngq9nDAHASlap"),
        ...
    ]
    """
    is_older_than_hold_days = (
        datetime.today() - timedelta(days=DAYS_CACHE_HOLD)
    ).timestamp() > os.path.getmtime(cache_filename)
    if (
        not os.path.exists(cache_filename)
        or is_older_than_hold_days
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
        spotify = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=ID,
                client_secret=SEC,
                redirect_uri="http://127.0.0.1:9090",
                scope="user-library-read",
                cache_path=cache_oauth_filename,
            )
        )
        albums = get_albums_spotify_accumulate(spotify)
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
album_arist, album_name, album_url, album_uri = albums[random_index]

output = []
if args.output_artist:
    output.append(album_arist)
if args.output_name:
    output.append(album_name)
if args.is_uri:
    output.append(album_uri)
else:
    output.append(album_url)

print("\n".join(output))
