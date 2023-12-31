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

client_id = "85c374790a0d4f119b2ade28c37931e0"
redirectUri = 'http://localhost:8080'

authUrl = "https://accounts.spotify.com/authorize"
driver = webdriver.Chrome()


def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

def sha256_hash(string):
    return hashlib.sha256(string.encode('utf-8')).digest()

def base64_encode(hash):
    base64_encoded = base64.urlsafe_b64encode(hash)
    return base64_encoded.decode().replace('=', '')


def get_token():
    code_verifier = generate_random_string(64)
    hashed = sha256_hash(code_verifier)
    code_challenge = base64_encode(hashed)
    
    params = {
        "response_type": 'code',
        "client_id": client_id,
        "code_challenge_method": 'S256',
        "code_challenge": code_challenge,
        "redirect_uri": redirectUri,
    }
    
    authorization_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    driver.get(authorization_url)
    uri_present = EC.url_contains(redirectUri)
    WebDriverWait(driver, 9999).until(uri_present)
    authorization_code = urllib.parse.urlparse(driver.current_url).query.split('=')[1]
    driver.quit()
    print("Logging in...")
    
    #webbrowser.open(authorization_url, new=1, autoraise=True)

    token_request_data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirectUri,
        "client_id": client_id,
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


def main():
    token = get_token()
    # input("Enter playlist url: ")
    id = "https://open.spotify.com/playlist/4kROaFuLfVxaYSZT3WbJzw".split('/')[-1].split('?')[0]
    track_objects = get_playlist(token, id)["items"]
    tracks = [track_objects[i]["track"]["name"] for i in range(len(track_objects))]
    
    print(tracks)
    
    


if __name__ == "__main__":
    main()


