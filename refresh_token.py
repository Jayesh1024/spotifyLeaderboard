import base64
import requests
import json
import dotenv
import os
dotenv.load_dotenv()



body = {
    'grant_type': 'authorization_code',
    'code': os.environ['CODE'],
    'redirect_uri': 'https://spotify.com/'
}

headers = {
    'Authorization': f"Basic {base64.b64encode(f"{os.environ['CLIENT_ID']}:{os.environ['CLIENT_SECRET']}".encode()).decode()}",
    'Content-Type': 'application/x-www-form-urlencoded'
}




token = requests.post(url=f"https://accounts.spotify.com/api/token", data=body, headers=headers)
with open('token.json','w') as f:
    json.dump(fp=f,obj=token.json(),indent=2)

                        

