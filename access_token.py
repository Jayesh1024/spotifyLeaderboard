import base64
import dotenv
import os
import requests
import json
dotenv.load_dotenv()

body = {
    'grant_type': 'refresh_token',
    'client_id': os.environ['CLIENT_ID'],
    'refresh_token': os.environ['REFRESH_TOKEN']
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': f"Basic {base64.b64encode(f'{os.environ['CLIENT_ID']}:{os.environ['CLIENT_SECRET']}'.encode()).decode()}"
}
def get_access_token():
    response = requests.post(url='https://accounts.spotify.com/api/token', data=body, headers=headers)
    token = response.json()['access_token']
    dotenv.set_key('.env','ACCESS_TOKEN',token)
    return









