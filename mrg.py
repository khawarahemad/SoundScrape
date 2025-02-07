
import json
import glob

# Base URL to prepend to file_path
base_url = "https://pub-b03428fdf2a349f384cb1a14c6700866.r2.dev/"

# List of all JSON files (e.g., faheem_abdullah.json, amir_ameer.json)
json_files = glob.glob("songs-api/public/songs/*.json")  # This will match all JSON files in the current directory

merged_data = []
current_id = 1  # Start the ID sequence from 1

for file in json_files:
    with open(file, "r", encoding="utf-8") as f:
        songs = json.load(f)
        
        # If the file contains a list of songs
        if isinstance(songs, list):
            for song in songs:
                # Prepend the base URL to the file_path
                if "file_path" in song:
                    song["file_path"] = base_url + song["file_path"]
                
                # Replace the existing ID with a sequential numeric ID
                song["id"] = current_id
                merged_data.append(song)
                current_id += 1
        
        # If the file contains a dictionary with artist names as keys
        elif isinstance(songs, dict):
            for artist_name, artist_songs in songs.items():
                for song in artist_songs:
                    # Prepend the base URL to the file_path
                    if "file_path" in song:
                        song["file_path"] = base_url + song["file_path"]
                    
                    # Replace the existing ID with a sequential numeric ID
                    song["id"] = current_id
                    merged_data.append(song)
                    current_id += 1

# Save the merged data into one file
with open("all_songs.json", "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=4)

print("Merged all JSON files into all_songs.json with sequential numeric IDs and updated file paths!")
