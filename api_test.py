from config import *
import logging
import os
import time
import requests
from urllib import parse
import json
import dotenv
dotenv.load_dotenv(override=True)

logging.basicConfig(
    level=LOG_LEVEL,
    filename=LOG_FILE_PATH,
    format=LOG_FORMAT
)

headers = {
    'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
}

def retry(max_retry=10,retry_interval=6):
    def actual_decorator(func):
        def wrapper(*args,**kwargs):
            retry_count = 1
            res = func(*args,**kwargs)
            while res.status_code!=200:
                logging.warning(f'Unsuccesful response, retrying, retry number:{retry_count}')
                if retry_count>max_retry:
                    error = {
                        'code':res.status_code,
                        'text':res.text,
                        'reason':res.reason
                    }
                    logging.error(f'Unsuccesful response, max retries reached, error:{error}')
                    raise requests.exceptions.RetryError(f"Unsuccesful response, max retries reached, error:{error}")

                import time
                time.sleep(retry_interval)
                res = func(*args,**kwargs)
                retry_count += 1
            
            return res
        return wrapper
    return actual_decorator

def set_token_if_expired(func):
    def wrapper(*args,**kwargs):
        url = "https://api.spotify.com/v1/artists/0TnOYISbd1XYRBk9myaseg"
        response = requests.get(url,headers=headers)
        if response.status_code == 401:
            from access_token import get_access_token
            get_access_token()
            dotenv.load_dotenv(override=True)
            headers['Authorization'] = f'Bearer {os.environ['ACCESS_TOKEN']}'
        return func(*args,**kwargs)
    return wrapper

@set_token_if_expired
def get_artist_albums():
    params = {
        'include_groups': 'album,single'
    }
    artist_id='06HL4z0CvFAxyc27GXpf02'
    response = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}/albums?{parse.urlencode(params)}',headers=headers)

    if response.status_code == 200:
        with open('response_albums.json','w') as f:
            json.dump(obj=response.json(),fp=f,indent=2)
    else:
        print(response.status_code)
        print(response.json())

@retry()
def get_artist(artist_id):
    url = f"https://api-partner.spotify.com/pathfinder/v1/query?operationName=queryArtistOverview&variables=%7B%22uri%22%3A%22spotify%3Aartist%3A{artist_id}%22%2C%22locale%22%3A%22%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%221ac33ddab5d39a3a9c27802774e6d78b9405cc188c6f75aed007df2a32737c72%22%7D%7D"
    response = requests.get(url=url, headers=headers)
    return response

@set_token_if_expired
def get_charts_playlists(): # gives all the Top 50 songs charts across multiple regions, but only the playlist level data and not it's contents.
    # Access token copied from the network tab will work here and not the API generated one, coz this is a private endpoint 
    result = []
    offset = 0
    while offset is not None:
        url = f"https://api-partner.spotify.com/pathfinder/v1/query?operationName=browseSection&variables=%7B%22pagination%22%3A%7B%22offset%22%3A{offset}%2C%22limit%22%3A20%7D%2C%22uri%22%3A%22spotify%3Asection%3A0JQ5DAzQHECxDlYNI6xD1i%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%227aa784dcf5577e14311d45c4d36440b6e949bd4ff94742cc47aabde5ee913776%22%7D%7D"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result.append(response.json())
        else:
            print(response.status_code)
            print(response.text)
        offset = response.json()['data']['browseSection']['sectionItems']['pagingInfo']['nextOffset']

    with open('charts_playlists.json', 'w') as f:
        json.dump(obj=result, fp=f, indent=2)

@set_token_if_expired
def get_playlist(playlist_id):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    response = requests.get(url, headers=headers)
    return response

def get_all_playlists(path_to_charts):
    with open(path_to_charts,'r') as f:
        charts_dict = json.load(f)
    playlist_ids = []
    for item in charts_dict:
        playlists = item['data']['browseSection']['sectionItems']['items']
        for playlist in playlists:
            playlist_id = playlist['uri'].split(':')[-1]
            playlist_ids.append(playlist_id)
        
    response_playlist = []
    for id in playlist_ids:
        response = get_playlist(id)
        if response.status_code == 200:
            response_playlist.append(response.json())
        else:
            error = {
                'code': response.status_code,
                'body': response.json()
            }
            logging.error(f"Unsuccessful response, error:{error}")
    
    with open('playlist_data.json','w') as f:
        json.dump(response_playlist,f,indent=2)

def retrieve_artists_list(path_to_playlist_data): # Retrieves artist id and name as key:value and saves it to json file artists.json
    with open(path_to_playlist_data,'r') as f:
        playlists = json.load(f)
    artist_ids = {}
    for playlist in playlists:
        tracks = playlist['tracks']['items']
        for track_obj in tracks:
            artists = track_obj['track']['artists']
            for artist_obj in artists:
                artist_ids[artist_obj['id']] = artist_obj['name']
    with open('artists.json','w') as f:
        json.dump(artist_ids,f,indent=2)

def retrieve_artists(path_to_artists_list):
    with open(path_to_artists_list,'r') as f:
        artists = json.load(f)
    
    
    res = []
    for i,(artist_id,_) in enumerate(artists.items()):
        #Batching logic
        if i!=0 and i%100 == 0:
            logging.info(f"Batch size 100, Batch number {i} complete, Batch writing to disk")
            with open('artist_data.json', 'w') as f:
                json.dump(res,f,indent=2)


        logging.info(f"Iteration number {i}, Batch number {(i//100)+1}")
        response = get_artist(artist_id)

        if response.status_code == 200:
            res.append(response.json())


        
    


retrieve_artists('artists.json')