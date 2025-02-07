import os
import yt_dlp
import spotipy
import requests
import json
import time
import re
from spotipy.oauth2 import SpotifyClientCredentials
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TALB
from dotenv import load_dotenv

# Load API credentials
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Spotify Authentication
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="9546839082dc47c087838ca160be2021",
    client_secret="e9e4f2b8360b4498aa92a3b1849c04e5"
))


# Output Folder
OUTPUT_FOLDER = "songs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def sanitize_filename(name):
    """Replace spaces with underscores and remove problematic characters."""
    name = re.sub(r'[\\/:*?"<>|!()@#&]', '', name)  # Remove special characters
    return "_".join(name.split())

def get_artist_songs(artist_name):
    """Fetch all songs of an artist from Spotify."""
    results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
    if not results['artists']['items']:
        print("❌ Artist not found!")
        return []
    
    artist_id = results['artists']['items'][0]['id']
    print(f"🎵 Fetching songs for {artist_name}...")
    
    songs = []
    albums = sp.artist_albums(artist_id, album_type='album', limit=50)
    
    for album in albums['items']:
        album_name = album['name']
        album_cover = album['images'][0]['url'] if album['images'] else None
        album_tracks = sp.album_tracks(album['id'])
        
        for track in album_tracks['items']:
            songs.append({
                "title": track['name'],
                "album": album_name,
                "album_cover": album_cover
            })
        time.sleep(1)
    
    return songs

def download_song(artist_name, song_title, index, total):
    """Download song from YouTube and return the sanitized file path."""
    sanitized_title = sanitize_filename(song_title)
    mp3_file = os.path.join(OUTPUT_FOLDER, f"{sanitized_title}.mp3")
    
    print(f"🔄 Processing download {index}/{total}: {song_title}")
    
    if os.path.exists(mp3_file):
        print(f"⚠️ Skipping {song_title} (already exists)")
        return mp3_file  

    # Set YouTube download options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(OUTPUT_FOLDER, f"{sanitized_title}.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    
    search_query = f"{artist_name} {song_title} audio"
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search_query}", download=True)['entries'][0]
            downloaded_filename = os.path.join(OUTPUT_FOLDER, f"{info['title']}.mp3")

            # Ensure correct renaming
            if downloaded_filename != mp3_file and os.path.exists(downloaded_filename):
                os.rename(downloaded_filename, mp3_file)

            print(f"✅ {song_title} downloaded successfully!")
            return mp3_file
    except Exception as e:
        print(f"❌ Failed to download {song_title}: {e}")
        return None


def main():
    artist_name = input("Enter the artist name: ")
    songs = get_artist_songs(artist_name)
    
    if not songs:
        print("❌ No songs found.")
        return
    
    metadata_list = []
    total_songs = len(songs)
    
    for index, song in enumerate(songs, start=1):
        print(f"🎵 Checking: {song['title']}...")

        mp3_file = download_song(artist_name, song['title'], index, total_songs)
        
        if not mp3_file or not os.path.exists(mp3_file):
            print(f"❌ Skipping {song['title']} due to download failure.")
            continue
        
        metadata_list.append({
            "id": len(metadata_list) + 1,
            "title": song["title"],
            "album": song["album"],
            "album_cover": song["album_cover"],
            "file_path": mp3_file
        })
        time.sleep(2)
    
    metadata_file = os.path.join(OUTPUT_FOLDER, f"{sanitize_filename(artist_name)}_songs.json")
    
    print("📂 Saving metadata...")
    with open(metadata_file, "w") as f:
        json.dump(metadata_list, f, indent=4)

    if os.path.exists(metadata_file):
        print(f"\n✅ Download complete! Metadata saved in {metadata_file}.")
    else:
        print("\n❌ Error: Metadata file was NOT created!")

if __name__ == "__main__":
    main()
