import requests
import json

with open('cookies.json','r') as f:
    cookies_dict = json.load(f)

headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    'Accept': 'application/json',
    'Referer': 'https://open.spotify.com/',
    'Origin': 'https://open.spotify.com'
}

url = "https://open.spotify.com/get_access_token?reason=init&productType=web-player"
response = requests.get(url,cookies=cookies_dict,headers=headers)

if response.status_code == 200:
    with open('access_token_cookies.json','w') as f:
        json.dump(obj=response.json(),fp=f,indent=2)
else:
    print(response.status_code)
    print(response.text)