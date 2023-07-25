import json
import logging
import secrets
import string
import urllib

import requests
import suggestion

import utils
from flask_session import Session
from flask import Flask, request, make_response, redirect, abort, session, render_template, url_for
from urllib.parse import urlencode
from tabulate import tabulate

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

CLIENT_ID = "stored in local file"
CLIENT_SECRET = "stored in local file"
REDIRECT_URI = "http://127.0.0.1:8080/callback"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = 'https://accounts.spotify.com/api/token'
ME_URL = 'https://api.spotify.com/v1/me'

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
# //TODO: use this link to change session type

Session(app)


@app.route('/')
def index():

    return render_template('index.html')


@app.route("/login")
def login():
    state = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )
    scope = 'user-top-read'
    data = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': state,
        'scope': scope,
        'show_dialog': True,
    }
    response = make_response(redirect(f'{AUTH_URL}/?{urlencode(data)}'))
    response.set_cookie('spotify_auth_state', state)
    return response


@app.route("/callback")
def callback():
    query_string = request.query_string.decode("utf-8")
    query_params = urllib.parse.parse_qs(query_string)
    auth_code = query_params["code"][0]
    auth_state = query_params["state"][0]
    stored_state = request.cookies.get('spotify_auth_state')
    if auth_state is None or auth_state != stored_state:
        app.logger.error('State mismatch: %s != %s', stored_state, auth_state)
        abort(400)

    access_token_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
    }

    access_token_response = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=access_token_data).json()
    access_token, refresh_token = access_token_response["access_token"], access_token_response['refresh_token']

    # session['tokens'] = {
    #     'access_token': access_token,
    #     'refresh_token': refresh_token,
    # }
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    # data = session['tokens']
    return redirect(url_for('.success', data = json.dumps(data)))


@app.route("/success")
def success():
    data_json = request.args.get('data')
    tokens_dict = json.loads(data_json)
    access_token, refresh_token = tokens_dict['access_token'], tokens_dict['refresh_token']
    lineup = utils.generate_lineup(access_token, "Lollapalooza", "data/Lollapalooza_artists.csv")


    playlist_id = "6w5ifHKifKO91S8zM923vG"
    data = f"https://open.spotify.com/embed/playlist/{playlist_id}?utm_source=generator"
    return render_template('success.html', data=data)

if __name__ == "__main__":
    app.run(port='8080')
