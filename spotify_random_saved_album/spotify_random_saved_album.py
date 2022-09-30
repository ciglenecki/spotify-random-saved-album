import argparse
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Tuple

import spotipy
from spotipy.oauth2 import SpotifyOAuth


def main():

    DAYS_CACHE_HOLD = 10
    FETCH_ALBUMS_LIMIT = 50
    RESOURCES_PATH = Path("resources")
    CACHE_PATH = Path(RESOURCES_PATH, ".cache.json")
    CACHE_OAUTH_PATH = Path(RESOURCES_PATH, ".cache")

    ID = os.getenv("SPOTIFY_ID")
    SEC = os.getenv("SPOTIFY_SECRET")

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
    cache_filename = Path(dir_path, CACHE_PATH)
    cache_oauth_filename = Path(dir_path, CACHE_OAUTH_PATH)

    def get_album_properties(album: Any) -> Tuple[str, str, str]:
        """
        Extracts album's properties:
            1. artist's name
            2. album's name
            3. album's url
            4. album's uri
        https://developer.spotify.com/documentation/web-api/reference/#/operations/get-multiple-albums
        """
        album = album["album"]
        album_name = album["name"]
        album_url = album["external_urls"]["spotify"]
        album_artist = album["artists"][0]["name"]
        album_uri = album["uri"]
        return album_artist, album_name, album_url, album_uri

    def get_albums_spotify_accumulate(spotify: spotipy.Spotify) -> List:
        """
        Accumulates all saved albums into a list.
        "next" returns the next subset of albums in a while loop until all albums are accumulated.
        """
        subset_albums = spotify.current_user_saved_albums(limit=FETCH_ALBUMS_LIMIT)
        albums = list(map(get_album_properties, subset_albums["items"]))
        while subset_albums["next"]:
            subset_albums = spotify.next(subset_albums)
            album_info = list(map(get_album_properties, subset_albums["items"]))
            albums.extend(album_info)
        return albums

    def save_albums_to_cache(albums, cache_filename):
        """
        Dumps albums list object as JSON and saves it to the cache file (.cache.json)
        """
        with open(cache_filename, "w") as cache:
            cache.write(json.dumps(albums))
        cache.close()

    def get_saved_albums():
        """
        Returns list of albums either by:
            a) using existing cache file
            b) calling Spotify's API:
        [
            ("Album Name 1", "https://open.spotify.com/album/20r762YmB5HeofjMCiP"),
            ("Album Name 2", "https://open.spotify.com/album/98SDG9ngq9nDAHASlap"),
            ...
        ]
        """

        def is_older_than_hold_days():
            return (
                datetime.today() - timedelta(days=DAYS_CACHE_HOLD)
            ).timestamp() > os.path.getmtime(cache_filename)

        if (
            not os.path.exists(cache_filename)
            or is_older_than_hold_days()  # call here instead of storing because cache might not exist yet
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


if __name__ == "__main__":
    main()
