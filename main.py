import pandas as pd
import folium
import re
import gpxpy
import json
from dateutil import parser
from datetime import datetime, timedelta

# Load TA site GPX (for towers + markers)
with open("/home/zane/Documents/GPX/TA_AllSites_20221114.gpx", "r") as f:
    gpx = gpxpy.parse(f)

# Load GPS waypoints with timestamps for WiFi matching
with open("/home/zane/software/wifiMap/src/Current_location.gpx", "r") as f:
    gpx_wifi = gpxpy.parse(f)

# Extract waypoints with timestamps
gpx_points = []
for wp in gpx_wifi.waypoints:
    if wp.time:
        gpx_points.append((wp.time, wp.latitude, wp.longitude))


def get_closest_gpx_point(scan_time):
    # Only consider GPS points after the scan_time, and within 60 seconds
    candidates = [p for p in gpx_points if timedelta(seconds=0) <= (p[0] - scan_time) <= timedelta(seconds=60)]
    if not candidates:
        raise ValueError("No matching GPS point within 60 seconds after scan time.")
    return min(candidates, key=lambda p: p[0])


# Coordinates of Telescope Array
telescope_array_coords = [39.3, -112.9]
towers = {
    "SNCT": [39.442911, -112.844229],
    "SKCT": [39.422425, -112.852434],
    "LRCT": [39.226160, -113.072571],
    "BRCT": [39.224425, -112.757766],
}

# Load WiFi scan data
with open("wifi_scan_log.json") as f:
    wifi_data = json.load(f)

# Color scheme by SSID
ssid_colors = {
    "TALESDAP": "blue",
    "TAX4SDAPSR": "green",
    "TAX4SDAPSN": "green",
    "TAX4SDAPBR": "green",
    "MCSOStarlink": "red",
    "Hotspot65BA": "purple",
    "HotspotGn2f": "pink",
    "PROJ871290": "brown",
    "conectelabtem": "orange",
    "": "gray"  # hidden networks
}

# Default fallback location
default_lat, default_lon = telescope_array_coords
unmatched = 0

# Build DataFrame rows from matched points
records = []
for entry in wifi_data:
    try:
        scan_time = parser.isoparse(entry["timestamp"])  # Already UTC-aware
        _, lat, lon = get_closest_gpx_point(scan_time)
    except Exception as e:
        unmatched += 1
        print(f"Match failed: {entry['timestamp']} -> {e}")
        lat, lon = default_lat, default_lon

    records.append({
        "lat": lat,
        "lon": lon,
        "distance": entry.get("estimated_distance_m", 0),
        "signal_strength": entry.get("signal", 0),
        "name": entry.get("ssid", ""),
        "color": ssid_colors.get(entry.get("ssid", ""), "gray"),
        "channel": entry.get("channel", 0),
    })

print(f"Matched {len(records) - unmatched} WiFi scans to GPS waypoints. {unmatched} unmatched.")

# Create DataFrame
df = pd.DataFrame(records)

# Create Folium map
# map = folium.Map(location=telescope_array_coords, zoom_start=12, tiles="OpenTopoMap")
map = folium.Map(location=telescope_array_coords, zoom_start=11, tiles=None)
folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="Map data: &copy; <a href='https://opentopomap.org'>OpenTopoMap</a> contributors",
    name="OpenTopoMap",
    max_zoom=17).add_to(map)

# Add WiFi signal circles
for _, row in df.iterrows():
    folium.Circle(
        location=(row['lat'], row['lon']),
        radius=max(50, ((row['signal_strength'] + 100) * 40)),
        color=row['color'],
        fill=True,
        fill_color=row['color'],
        fill_opacity=0.3,
        popup=f"SSID: {row['name']}\nSignal: {row['signal_strength']} dB\nChannel: {row['channel']}"
    ).add_to(map)

# Add tower markers
for name, coords in towers.items():
    folium.Marker(
        location=coords,
        popup=name,
        icon=folium.Icon(icon='star', color='red')
    ).add_to(map)

# Add TA SD markers from GPX waypoints
tasd = re.compile(r'^(SK|BR|LR)\d{4}$')
for wp in gpx.waypoints:
    if wp.name and tasd.match(wp.name):
        folium.Circle(
            location=(wp.latitude, wp.longitude),
            radius=100,
            color="gray",
            fill=True,
            fill_color="gray",
            fill_opacity=0.6,
            popup=wp.name
        ).add_to(map)

# Save interactive HTML
map.save("wifi_locations_map.html")
