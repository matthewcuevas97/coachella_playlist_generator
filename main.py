import itertools
import json
import requests
import utils
import suggestion

ACCESS_TOKEN = "BQDLAvY8ybIdj7ZMx73NtSkzQiBjAf6o5RBJwzSy-ds0x-1vly1wLpH9Qna2oFLZvdcLhfSpXucUIMYAvMEmg2mMBDONBxXtaQRxM" \
               "-B4H89fXbDplrM2QhdnhS3iLheNYodLca0XI08xNsFstG9rhkcNIcQ3U45-K5gKMg-rRS8TPMLap_WKcqVi5ympdj28jAT" \
               "-hdSDqbVtjMxobA"


def initialize(access_token):
    # TODO: check against coachella_artists.txt, throw error
    with open('data/coachella_artists.txt') as f:
        artists_strings = [line.strip('\n') for line in f]

    with open('data/all_spotify_artists.json', 'w') as f:
        json.dump(artists_strings, f)

    # TODO: put this function in utils

    with open('data/all_spotify_artists.json') as f:
        artists = json.load(f)

    artist_search_results = [utils.search_artist_top_result(access_token, artist) for artist in artists[:10]]
    artist_search_results_filtered = [x for x in artist_search_results if x is not None]

    coachella_2023_official_playlist_id = "1RIp2yQ4yyNuFHqP80pCpz"
    artists_from_playlist = []
    #  TODO: for loop for generality, check for api rate limiting, put get playlist tracks in utils
    for i in range(4):
        response = requests.get(f"https://api.spotify.com/v1/playlists/{coachella_2023_official_playlist_id}/tracks",
                                headers={"Authorization": f"Bearer {access_token}"},
                                params={"limit": 50, "offset": 50 * i})
        playlist = json.loads(response.content)
        artists_from_playlist += itertools.chain(*[item['track']['artists'] for item in playlist['items']])

    artists_from_playlist_ids = [artist['id'] for artist in artists_from_playlist]
    confirmed_artists = list(filter(lambda x: x['id'] in artists_from_playlist_ids, artist_search_results_filtered))
    with open('data/all_spotify_artists.json', 'w') as f:
        json.dump(confirmed_artists, f)


def main():
    # initialize(ACCESS_TOKEN)
    # print(suggestion.generate_playlist())
    temp = utils.generate_lineup("Lollapalooza", "data/Lollapalooza_artists.csv")
    return temp


if __name__ == '__main__':
    main()
