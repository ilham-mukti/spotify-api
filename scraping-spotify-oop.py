import requests
import base64
import datetime
import urllib.parse
import pandas as pd

class SpotifyAPI():
	def __init__(self, client_id, client_secret, keyword_artist):
		self.client_id = client_id
		self.client_secret = client_secret
		self.keyword_artist = urllib.parse.quote(keyword_artist)

	def get_access_token(self):
		client = f'{self.client_id}:{self.client_secret}'
		client_base64 = base64.b64encode(client.encode())
		header_basic = {'Authorization': f'Basic {client_base64.decode()}'}
		token_url = 'https://accounts.spotify.com/api/token'
		token_params = {'grant_type': 'client_credentials'}
		token_request = self.request_data(token_url, token_params, header_basic, type='post')
		access_token = token_request['access_token']
		#expires_in = token_request['expires_in']
		return access_token

	def get_artist(self, access_token):
		self.headers_bearer = {'Authorization': f'Bearer {access_token}'}
		url_search = f'https://api.spotify.com/v1/search?q={self.keyword_artist}&type=artist'
		r = self.request_data(url_search, header=self.headers_bearer)
		artists = r['artists']['items'][0]
		self.name_artist = artists['name']
		id_artist = artists['id']
		uri_artist = artists['uri']
		followers_artist = artists['followers']['total']
		spotify_link_artist = artists['external_urls']['spotify']
		print(self.name_artist, followers_artist, spotify_link_artist)
		return id_artist

	def get_albums(self, id_artist):
	    my_dict = []
	    url_get_album = f'https://api.spotify.com/v1/artists/{id_artist}/albums?limit=50'
	    r = self.request_data(url_get_album, header=self.headers_bearer)
	    albums = r['items']
	    count = 1
	    for album in albums:
	    	album_id = album['id']
	    	album_name = album['name'].lower()
	    	album_uri = album['uri']
	    	album_type = album['type']
	    	album_release_date = album['release_date']
	    	album_link = album['external_urls']['spotify']
	    	print(count, album_name, album_link)
	    	my_dict.append({'artist_name': self.name_artist, 'album_name': album_name, 'album_id': album_id, 'album_release_date': album_release_date, 'album_link': album_link, 'album_uri': album_uri})
	    	count+=1
	    df_album = self.save_to_dataframe(self.name_artist+'_album.csv', my_dict)
	    return df_album

	def get_tracks(self, df_album):
		my_dict = []
		for x in range(0, df_album.shape[0]):
			url_get_track = f'https://api.spotify.com/v1/albums/{df_album["album_id"][x]}/tracks?limit=50'
			r = self.request_data(url_get_track, header=self.headers_bearer)
			tracks = r['items']
			count = 1
			for track in tracks:
				track_id = track['id']
				track_name = track['name'].lower()
				track_uri = track['uri']
				track_link = track['external_urls']['spotify']
				print(count, track_name, track_id)
				count+=1
				my_dict.append({'artist_name': df_album['artist_name'][x], 'album_name': df_album['album_name'][x], 'album_id': df_album['album_id'][x], 'album_release_date': df_album['album_release_date'][x], 'album_link': df_album['album_link'][x], 'album_uri': df_album['album_uri'][x], 'track_id': track_id, 'track_name': track_name, 'track_link': track_link, 'track_uri': track_uri})
		df_tracks = self.save_to_dataframe(self.name_artist+'_tracks.csv', my_dict)
		return df_tracks

	def get_audio(self, df_tracks):
		my_dict = []
		for x in range(0, df_tracks.shape[0]):
			url_get_audio = f'https://api.spotify.com/v1/audio-features/{df_tracks["track_id"][x]}'
			audio = self.request_data(url_get_audio, header=self.headers_bearer)
			(print(f'Get Audio {df_tracks["track_name"][x]}'))
			my_dict.append(audio)
		df_audio = self.save_to_dataframe(self.name_artist+'_audio.csv', my_dict)
		result = pd.concat([df_tracks, df_audio], axis=1)
		result.to_csv(self.name_artist+'_completed.csv', index=False)
		print("end!")

	def save_to_dataframe(self, name_file, my_dict):
		df = pd.DataFrame(my_dict, columns=my_dict[0].keys())
		df.to_csv(name_file, index=False)
		return df

	def request_data(self, url, params=None, header=None, type='get'):
		if(type == 'post'):
			request = requests.post(url, data=params, headers=header)
		else:
			request = requests.get(url, data=params, headers=header)
		result = request.json()
		return result

client_id = 'xxxx'
client_secret = 'xxxx'
keyword_artist = 'Oasis'

spotify = SpotifyAPI(client_id, client_secret, keyword_artist)
token = spotify.get_access_token()
artist = spotify.get_artist(token)
album = spotify.get_albums(artist)
tracks = spotify.get_tracks(album)
audio = spotify.get_audio(tracks)
