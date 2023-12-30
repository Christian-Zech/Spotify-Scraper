import base64
import random
import string
import requests
import urllib
import hashlib
import webbrowser


client_id = "85c374790a0d4f119b2ade28c37931e0"
redirectUri = 'http://localhost:8080'

authUrl = "https://accounts.spotify.com/authorize"



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
    webbrowser.open(authorization_url, new=1, autoraise=True)
    
    
    
    authorization_code = input("Enter the authorization code: ")

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
    return requests.get("https://api.spotify.com/v1/playlists/" + id, headers={"Authorization": "Bearer " + token}).json()


def main():
    token = get_token()
    print(get_playlist(token, "4kROaFuLfVxaYSZT3WbJzw"))
    
    


if __name__ == "__main__":
    main()


