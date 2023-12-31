import base64
import random
import string
import requests
import urllib
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

spotify_client_id = "85c374790a0d4f119b2ade28c37931e0"
spotify_redirectUri = 'http://localhost:8080'
spotify_authUrl = "https://accounts.spotify.com/authorize"

youtube_client_key = "AIzaSyDEC6EKIdE-03qbBZlrH_7fkmURvDBocQQ"
youtube_client_auth= "136009703112-907m04u5ptovfo9qoqgfuta8okfcc0kh.apps.googleusercontent.com"
youtube_client_secret = "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"

driver = webdriver.Chrome()

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def sha256_hash(string):
    return hashlib.sha256(string.encode('utf-8')).digest()

def base64_encode(hash):
    base64_encoded = base64.urlsafe_b64encode(hash)
    return base64_encoded.decode().replace('=', '')

def get_spotify_token():
    code_verifier = generate_random_string(64)
    hashed = sha256_hash(code_verifier)
    code_challenge = base64_encode(hashed)
    
    params = {
        "response_type": 'code',
        "client_id": spotify_client_id,
        "code_challenge_method": 'S256',
        "code_challenge": code_challenge,
        "redirect_uri": spotify_redirectUri,
    }
    
    authorization_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    driver.get(authorization_url)
    uri_present = EC.url_contains(spotify_redirectUri)
    WebDriverWait(driver, 9999).until(uri_present)
    authorization_code = urllib.parse.urlparse(driver.current_url).query.split('=')[1]
    driver.quit()
    print("Loading tracks from playlist...")
    
    #webbrowser.open(authorization_url, new=1, autoraise=True)

    token_request_data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": spotify_redirectUri,
        "client_id": spotify_client_id,
        "code_verifier": code_verifier,
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=token_request_data)
    token = response.json()['access_token']
    return token

def get_playlist(token, id):
    return requests.get("https://api.spotify.com/v1/playlists/" + id + "/tracks", headers={"Authorization": "Bearer " + token}).json()

def get_tracks():
    token = get_spotify_token()
    # input("Enter playlist url: ")
    id = "https://open.spotify.com/playlist/4kROaFuLfVxaYSZT3WbJzw".split('/')[-1].split('?')[0]
    track_objects = get_playlist(token, id)["items"]
    tracks = [track_objects[i]["track"]["name"] for i in range(len(track_objects))]
    
    print("Songs loaded:")
    for track in tracks:
        print(track)
    
    return tracks

def get_youtube_id(song_name):
    base = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "maxResults": 1,
        "q": song_name,
        "key": youtube_client_key,
        "type": "video"
    }
    r = requests.get(base, params=params)
    video_id = r.json()["items"][0]["id"]["videoId"]
    print(f"found youtube video id: {video_id}")
    return video_id

def main():
    track_names = get_tracks()
    for name in track_names:
        get_youtube_id(name)
    
    


if __name__ == "__main__":
    main()


