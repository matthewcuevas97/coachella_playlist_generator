import csv
import json
import os

import redis
import requests
from datetime import timedelta

redis_client = redis.Redis()


def get_related_artists(access_token, artist_id, timeout=60, ex_weeks=10):
    """
    get request related artists from spotify api, checks redis server first
    :param access_token: specific string to user and scope
    :param artist_id: string id
    :return: array of artist objects
    """
    related_artists_key = f"{artist_id}_related_artists"
    related_artists = redis_client.get(related_artists_key)
    if related_artists is None:
        spotify_related_artists_url = "https://api.spotify.com/v1/artists/" + artist_id + "/related-artists"
        response = requests.get(spotify_related_artists_url, headers={"Authorization": f"Bearer {access_token}"},
                                timeout=timeout)
        json_resp = response.json()
        redis_client.set(related_artists_key, json.dumps(json_resp), ex=timedelta(weeks=ex_weeks))
    else:
        json_resp = json.loads(related_artists)
    return json_resp


# TODO: generalize search function

def search_artist_top_result(access_token, artist_string, timeout=60):
    response = requests.get("https://api.spotify.com/v1/search",
                            headers={"Authorization": f"Bearer {access_token}"},
                            params={"q": artist_string, "type": "artist", "limit": 1},
                            timeout=timeout)
    search_result = json.loads(response.content)['artists']['items']
    return search_result[0] if search_result else None


def get_artist(access_token, artist_id, timeout=60, ex_weeks=10):
    """
    get request artist info from spotify api
    :param access_token: specific string to user and scope
    :param artist_id: string id
    :return: artist object
    """
    get_artist_key = f"{artist_id}_get_artist"
    artist = redis_client.get(get_artist_key)
    if artist is None:
        spotify_artist_url = "https://api.spotify.com/v1/artists/" + artist_id
        response = requests.get(spotify_artist_url, headers={"Authorization": f"Bearer {access_token}"},
                                timeout=timeout)
        json_resp = response.json()
        redis_client.set(get_artist_key, json.dumps(json_resp), ex=timedelta(weeks=ex_weeks))
    else:
        json_resp = json.loads(artist)
    return json_resp


def get_artists(access_token, artist_ids, timeout=60):
    """
    get request artist info from spotify api, maximum 50 ids
    :param access_token: specific string to user and scope
    :param artist_ids: list of ids
    :return: list of artist objects
    """
    responses = []
    for artist_id in artist_ids:
        artist = get_artist(access_token, artist_id, timeout)
        responses += [artist]
    return responses


def get_my_top(access_token, item="artists", limit=50, offset=0, time_range="long_term"):
    """
    get request top artists or top tracks for user
    :param access_token: specific string to user and scope
    :param item: string "artists" or "tracks"
    :param limit: 0 -> 50
    :param offset: int
    :param time_range: "long_term", "short_term", "medium_term"
    :return: body
    """
    spotify_my_top_url = "https://api.spotify.com/v1/me/top/" + item
    response = requests.get(spotify_my_top_url, headers={"Authorization": f"Bearer {access_token}"},
                            params={"limit": limit, "offset": offset, "time_range": time_range})
    json_resp = response.json()
    return json_resp


def get_artists_top_tracks(access_token, artist_id, market='US', ex_weeks=10, timeout=60):
    """
    get request top tracks for given artist
    :param market: specific string to user and scope
    :param access_token: specific string to user and scope
    :param artist_id: string
    :return: json object
    """
    get_top_tracks_key = f"{artist_id}_top_tracks"
    top_tracks = redis_client.get(get_top_tracks_key)
    if top_tracks is None:
        spotify_artist_url = "https://api.spotify.com/v1/artists/" + artist_id + "/top-tracks"
        response = requests.get(spotify_artist_url,
                                headers={"Authorization": f"Bearer {access_token}"},
                                params={"market": market},
                                timeout=timeout)
        json_resp = response.json()
        redis_client.set(get_top_tracks_key, json.dumps(json_resp), ex=timedelta(weeks=ex_weeks))
    else:
        json_resp = json.loads(top_tracks)
    return json_resp


def put_tracks_in_playlist(access_token, playlist_id, json_data):
    """
    :param access_token: specific string to user and scope
    :param playlist_id:
    :param json_data:
    :return:
    """
    spotify_artist_url = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"
    response = requests.put(spotify_artist_url,
                            headers={"Authorization": f"Bearer {access_token}"},
                            data=json_data)
    json_resp = response.json()
    return json_resp


def generate_lineup(access_token, festival_name, artist_csv_filepath):
    # //TODO: account for artists with commas in their names
    if os.path.isfile(f'data/{festival_name}_artists.json'):
        f = open(f'data/{festival_name}_artists.json', 'r')
        artists = json.load(f)
    else:
        artist_strings = []
        with open(artist_csv_filepath) as f:
            _ = csv.reader(f)
            for artist in _:
                artist_strings += artist
        artists = [search_artist_top_result(access_token, artist, 60) for artist in artist_strings]
        with open(f'data/{festival_name}_artists.json', 'w') as f:
            json.dump(artists, f)
    if os.path.isfile(f'data/{festival_name}_related.json'):
        f = open(f'data/{festival_name}_related.json', 'r')
        json.load(f)
    else:
        related_artists = {}
        for artist in artists:
            related = get_related_artists(access_token, artist['id'])
            related_artists[artist['id']] = related
        with open(f'data/{festival_name}_related.json', 'w') as f:
            json.dump(related_artists, f)
    if os.path.isfile(f'data/{festival_name}_songs.json'):
        f = open(f'data/{festival_name}_tracks.json')
        json.load(f)
    else:
        id_to_top_tracks = {}
        for artist in artists:
            artist_id = artist['id']
            top_tracks = get_artists_top_tracks(access_token, artist['id'])
            id_to_top_tracks[artist_id] = top_tracks
        with open(f'data/{festival_name}_songs.json', 'w') as f:
            json.dump(id_to_top_tracks, f)

    return "success"
