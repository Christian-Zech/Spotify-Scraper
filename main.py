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
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os


spotify_client_id = "85c374790a0d4f119b2ade28c37931e0"
spotify_redirectUri = 'http://localhost:8080'
spotify_authUrl = "https://accounts.spotify.com/authorize"

youtube_api_key = "AIzaSyDEC6EKIdE-03qbBZlrH_7fkmURvDBocQQ"
youtube_redirect_uri = "http://localhost:8080"

username = os.getlogin()
options = webdriver.ChromeOptions() 
options.add_argument('--profile-directory=Default')
options.add_argument(f"user-data-dir=C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data")
driver = webdriver.Chrome(options=options)

# following four functions authenticate the user with spotify's api
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
    
    # opens a chrome window to authenticate the user
    authorization_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    driver.get(authorization_url)
    uri_present = EC.url_contains(spotify_redirectUri)
    WebDriverWait(driver, 9999).until(uri_present)
    authorization_code = urllib.parse.urlparse(driver.current_url).query.split('=')[1]
    

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

# Uses spotify's api to get the tracks from the playlist
def get_playlist(token, id):
    return requests.get("https://api.spotify.com/v1/playlists/" + id + "/tracks", headers={"Authorization": "Bearer " + token}).json()

def get_tracks():
    token = get_spotify_token()
    id = input("Enter spotify playlist url: ").split('/')[-1].split('?')[0]
    track_objects = get_playlist(token, id)["items"]
    tracks = [track_objects[i]["track"]["name"] for i in range(len(track_objects))]
    
    for track in tracks:
        print(track)
    
    return tracks

# Uses youtube's api to get the video id of a given spotify song name
def get_youtube_id(song_name):
    base = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "maxResults": 1,
        "q": song_name,
        "key": youtube_api_key,
        "type": "video"
    }
    r = requests.get(base, params=params)
    video_id = r.json()["items"][0]["id"]["videoId"]
    return video_id


def main():
    print("Make sure that chrome is completely closed. This program won't work if chrome is already open.")
    track_names = get_tracks()
    print("loading tracks from spotify...")
    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes=['https://www.googleapis.com/auth/youtube'])
    flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message="")
    credentials = flow.credentials
    youtube = build('youtube', 'v3', credentials=credentials)
    print("Creating youtube playlist...")
    playlist = youtube.playlists().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": "Spotify Playlist",
            "description": "A private playlist created with the YouTube API"
          },
          "status": {
            "privacyStatus": "private"
          }
        }
    ).execute()
    print("Playlist created!")
    playlist_id = playlist["id"]
    
    for track in track_names:
        video_id = get_youtube_id(track)
        youtube.playlistItems().insert(
            part="snippet",
            body={
              "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                  "kind": "youtube#video",
                  "videoId": video_id
                }
              }
            }
        ).execute()
        print(f"Added video with id {video_id} to playlist")
    
    print("Done!")
        

    

if __name__ == "__main__":
    main()


