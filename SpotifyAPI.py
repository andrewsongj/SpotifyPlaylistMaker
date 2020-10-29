import requests
import base64
import datetime
import json
import random
from urllib.parse import urlencode

class SpotifyAPI (object):
 
    client_id = None
    client_secret = None
    access_token = None
    code = None
    access_token_expires = datetime.datetime.now()
    login_url = 'https://accounts.spotify.com/authorize'
    token_url = 'https://accounts.spotify.com/api/token'

    def __init__ (self, client_id, client_secret, code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.code = code

    #Get Methods
    def get_client_id (self):
        if self.client_id == None:
            raise Exception("Client ID Needed")
        return self.client_id

    def get_client_secret (self):
        if self.client_secret == None:
            raise Exception("Client Secret Needed")
        return self.client_secret

    def get_code (self):
        if self.code == None:
            raise Exception("Authorization Code Needed")
        return self.code

    def get_token_data (self):
        return { 'grant_type' : 'authorization_code',
                 'code' : self.get_code(),
                 'redirect_uri' : 'https://spotify.com' }

    def get_token_header (self):
        client_id = self.get_client_id()
        client_secret = self.get_client_secret()
        client_cred = f'{client_id}:{client_secret}'
        client_cred_b64 = base64.b64encode(client_cred.encode())
        return { 'Authorization' : f'Basic {client_cred_b64.decode()}' }

    def get_access_token (self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now or token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_search_header (self) :
        access_token = self.get_access_token()
        header = {
                'Authorization' : f'Bearer {access_token}'
            }
        return header

    def perform_auth (self) :
        lookup_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_header()
        r = requests.post(lookup_url, data=token_data, headers=token_headers)

        if r.status_code not in range (200, 299):
            print(r.status_code)
            print(r.text)
            raise Exception("Did not authenticate client")

        token_response_data = r.json()  
        access_token = token_response_data['access_token']
        expires_in = token_response_data['expires_in']

        self.access_token = access_token
        self.access_token_expires = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

        #Obtain code
    def initial_request(self) :
        endpoint = self.login_url
        query_params = urlencode( {
                'client_id' : self.get_client_id(), 
                'response_type' : 'code',
                'redirect_uri' : 'https://spotify.com',
                'scope' : 'playlist-modify-public'
            } )
        lookup_url = f'{endpoint}?{query_params}'
        r = requests.get(lookup_url)
        return r.url

    def search (self, query=None, search_type='artist', offset=0) :
        if query == None:
            raise Exception("A query is required")
        if isinstance(query, dict) :
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
            #using field filters: album, artist, track
            #convert dict to list, join the list on spaces, which is encoded later
        query_params = urlencode( {
                'q' : query, 
                'type' : search_type.lower(),
                'limit' : 50,
                'offset' : random.randint(0, 30)
            } )
        headers = self.get_search_header()
        endpoint = 'https://api.spotify.com/v1/search'
        lookup_url = f'{endpoint}?{query_params}'
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299) :
            return {}
        return r.json()

    def create_playlist (self, user_id, name, public=True, desc=''):
        token = self.get_access_token()
        request_body = json.dumps({
            'name' : name,
            'description' : desc,
            'public' : public
        })
        query = f'https://api.spotify.com/v1/users/{user_id}/playlists'
        
        response = requests.post(
                query,
                data=request_body,
                headers={
                        'Content-Type' : 'application/json',
                        'Authorization' : f'Bearer {token}'
                    }
            )
        return response.json()
        
    def add_to_playlist (self, playlist_id, songs) :
        #songs should be an array of uris
        request_data = json.dumps(songs)
        query = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        token = self.get_access_token()
        response = requests.post(
            query,
            data=request_data,
            headers={
                'Content-Type' : 'application/json',
                'Authorization' : f'Bearer {token}'
            }
        )
        return response.json()
