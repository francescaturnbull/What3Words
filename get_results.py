import requests
import time
import numpy as np
from tqdm import tqdm
import folium

# Set the API key taken from https://what3words.com
API_KEY = "[API_KEY]"

# Set the bounding area to search within.
min_lat, max_lat = 51.501, 51.502
min_lng, max_lng = -0.120, -0.119

# Create a list of words to be looked for within the What3Words results.
target_words = {"fish", "sea", "aquarium", "aquatic", "shark", "seal", "water", "coral"}

# Function to generate a list of all the co-ordinates to check. Set spacing_m to be the number of metres apart each co-ordinate should be. 
# 3 metres will check every What3Words word in the bounding area.
def generate_grid(min_lat, max_lat, min_lng, max_lng, spacing_m=3):
    coords = []
    lat = min_lat
    while lat <= max_lat:
        lng = min_lng
        while lng <= max_lng:
            coords.append((round(lat, 6), round(lng, 6)))
            lng += spacing_m / (111320 * np.cos(np.radians(lat)))
        lat += spacing_m / 110540
    return coords

# Function to get the What3Words word for the latitude and longitude provided.
def get_w3w(lat, lng):
    url = f"https://api.what3words.com/v3/convert-to-3wa?coordinates={lat},{lng}&key={API_KEY}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json().get("words")
    except Exception as e:
        print (f"Error at ({lat}, {lng}): {e}")
        return None

# Create the list where the results will be stored.
results = []

# Output the number of locations to be checked.
grid = generate_grid(min_lat, max_lat, min_lng, max_lng)
print (f"Checking {len(grid)} locations...")

# For every latitdue/longitude pair in the bounding area, get the What3Words word. If any of the words appear in the list of target
# words, then add the full word, latitude, and longitude to the results list.
# Use tqdm() to generate a progress bar.
for lat, lng in tqdm(grid):
    w3w = get_w3w(lat, lng)
    if w3w:
        words = w3w.split(".")
        if any(word in target_words for word in words):
            results.append((w3w, lat, lng))
    time.sleep(0.5)

# Output how many matches were found and print all the matches.
print (f"\n Found {len(results)} matches:")
for r in results:
    print (f"{r[0]} at ({r[1]}, {r[2]})")

# Visualise the results on a map and save to a html file.
map_centre = [(min_lat + max_lat) / 2, (min_lng + max_lng) / 2]
m = folium.Map(location=map_centre, zoom_start=19)

for address, lat, lng in results:
    folium.Marker(
        location=[lat, lng],
        popup=address,
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

m.save("wsw_matches_map.html")
