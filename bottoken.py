import os

import requests

import botsecrets


REFRESH_URL = "https://id.twitch.tv/oauth2/token"
REFRESH_FILE = "data/refresh_token.txt"


def refresh_token():
    """Use the Refresh Token to get a new Access Token"""

    # If the token file does not exist, create it with the default Refresh Token
    if not os.path.exists(REFRESH_FILE):
        with open(REFRESH_FILE, 'w+') as f:
            f.write(botsecrets.REFRESH_TOKEN)
            f.close()

    # Read the Refresh token from file
    with open(REFRESH_FILE, 'r') as f:
        file_token = f.readlines()[0]
        f.close()

    # Prepare the URL request data
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': file_token,
        'client_id': botsecrets.CLIENT_ID,
        'client_secret': botsecrets.CLIENT_SECRET
    }

    # Submit the request for a new Access token
    json_resp = requests.post(REFRESH_URL, data=data).json()

    # Read the new Access token and the Refresh token (Refresh tokens can change over time)
    new_access_token = ""
    try:
        new_access_token = json_resp['access_token']
        new_refresh_token = json_resp['refresh_token']

        # Save the Refresh token to the token file
        with open(REFRESH_FILE, 'w') as f:
            f.write(new_refresh_token)
            f.close()

    except KeyError:
        print("Error reading JSON response (missing key 'access_token' and/or 'refresh_token'):")
        print(json_resp)

    return new_access_token
