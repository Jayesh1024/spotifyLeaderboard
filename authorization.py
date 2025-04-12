import webbrowser
import base64
import requests
import json
import os
import dotenv
dotenv.load_dotenv()
# scopes = ['ugc-image-upload user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-follow-modify user-follow-read user-read-playback-position user-top-read user-read-recently-played user-library-modify user-library-read user-read-email user-read-private']
params = {
    'client_id': os.environ['CLIENT_ID'],
    'response_type': 'code', 
    'redirect_uri': 'https://spotify.com/'
}

auth_link = requests.get('https://accounts.spotify.com/authorize', params=params).url
print(auth_link)

# Open the browser to the authorization link and wait for the user to authorize the app
# Then copy the code parameter from the redirect URL and replace the value of CODE in the .env file
# Then run the access-token.py script

