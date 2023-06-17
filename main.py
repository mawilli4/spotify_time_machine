import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.billboard.com/charts/hot-100/"
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = "http://example.com"

# Scraping Billboard 100
list_date = input("What year would you like to travel to? Type date in this format YYYY-MM-DD\n")

URL = f"{BASE_URL}{list_date}"
response = requests.get(URL)
website_html = response.text

soup = BeautifulSoup(website_html, "html.parser")
all_titles = soup.find_all(name="h3", id="title-of-a-story", class_="a-no-trucate")
song_names = [song.getText()[14:][:-5] for song in all_titles]

# Spotipy Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",
    )
)

user_id = sp.current_user()["id"]

# Searching Spotify for songs by title
song_uris = []
year = list_date.split("-")[0]
for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{list_date} Billboard 100", public=False)
print(playlist)

# Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
