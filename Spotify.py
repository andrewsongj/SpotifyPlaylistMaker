#Andrew Song
from SpotifyAPI import SpotifyAPI
import json
import random

client_id = 'a404a52bb12346f59321453476a47e4f'
client_secret = 'bf47396b86134e88adfd2cb0fcf2d1c8'
user_id = 'andrewsong.j'
#initial_request: 
#   https://accounts.spotify.com/login?continue=https%3A%2F%2Faccounts.spotify.com%2Fauthorize%3Fscope%3Dplaylist-modify-public%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fspotify.com%26client_id%3Da404a52bb12346f59321453476a47e4f
url = input("Enter URL After Log-In: ")
code = url.split('code=')[1]
client = SpotifyAPI(client_id, client_secret, code)

songs = []
artists = ['Lil Yachty', 'Gucci Mane', 'A$AP Twelvyy', 'Lil Uzi Vert']
songs_per_artist = 100 // len(artists)
for artist in artists:
    filter = {
            'artist' : artist
            #, 'genre' : "k-pop"
        }
    list = client.search(filter, 'track') 
    tracks = list['tracks']['items']
    if len(tracks) < songs_per_artist:
        raise Exception("Not enough search results for " + artist)
    for i in range(0, songs_per_artist):
        r = random.randint(0, len(tracks)-1)
        while tracks[r]['uri'] in songs:
            r = random.randint(0, len(tracks)-1)
        songs.append(tracks[r]['uri'])
resp = client.create_playlist(user_id, 'Random Mix', desc='Randomly generated with Spotify API')
playlist_id = resp['id']
client.add_to_playlist(playlist_id, songs)

#Eventually, I need to be able to change my offset based on the number of tracks 
#an artist has. Basically, I need to make sure that even with an offset, I still
#get enough tracks from my search function to be able to add (tracks_per_artist) 
#number of songs from that one artist. In this program, I simply remain conservative 
#with my offset and throw an exception is the offset is too much

#ANOTHER IDEA: For each artist, you can make multiple searches in order to get a 
#wider selection of songs. Then just keep track of how times you have added for 
#that artist

