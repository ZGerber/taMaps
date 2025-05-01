import pandas as pd
import folium
import re
import gpxpy
with open("/home/zane/Documents/GPX/TA_AllSites_20221114.gpx", "r") as f:
    gpx = gpxpy.parse(f)

# Coordinates of the Telescope Array Cosmic Ray Observatory in Utah
telescope_array_coords = [39.3, -112.9]
towers = {"SNCT": [39.442911, -112.844229], "SKCT": [39.422425, -112.852434], 'LRCT': [39.226160, -113.072571],}

data = {
    'lat': [39.3530625, 39.39769, 39.405834, 39.437054, 39.429455, 39.419931, 39.406678, 39.406678,
            39.395621, 39.387368, 39.379681, 39.306629, 39.365581, 39.292074],
    'lon': [-112.7424375, -112.783797, -112.798416, -112.813919, -112.791071, -112.783867, -112.814408, -112.814408,
            -112.8767, -112.896441, -112.904940, -112.905895, -112.905017, -112.773461],
    'distance': [551, 492, 309, 87, 138, 309, 491, 309, 155, 310, 438, 310, 390, 110],  # Distance in meters88
    'signal_strength': [-95, -95, -79, -84, -79, -79, -95, -90, -84, -82, -93, -90, -92, -81],
    'name': ['TALESDAP', 'TALESDAP', 'TAX4SDAPSN', 'TAX4SDAPSN', 'TAX4SDAPSN', 'TAX4SDAPSN', 'TAX4SDAPSN', 'TAX4SDAPSN', 'TALESDAP', 'TALESDAP',
             'TALESDAP', 'TALESDAP', 'TALESDAP', 'conectelabtem'],
    'color': ['blue', 'blue', 'green', 'green', 'green', 'green', 'green', 'green',
              'blue', 'blue', 'blue', 'blue', 'blue', 'red'],
}

# Convert to DataFrame
df = pd.DataFrame(data)

# map = folium.Map(location=telescope_array_coords, zoom_start=12, tiles="OpenTopoMap")
map = folium.Map(location=telescope_array_coords, zoom_start=11, tiles=None)  # Start with no base tiles
folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="Map data: &copy; <a href='https://opentopomap.org'>OpenTopoMap</a> contributors",
    name="OpenTopoMap",
    max_zoom=17
).add_to(map)

for _, row in df.iterrows():
    folium.Circle(
        location=[row['lat'], row['lon']],
        radius=row['distance'],
        color=row['color'],
        fill=True,
        fill_color=row['color'],
        fill_opacity=0.3,
        popup=f"Signal Strength: {row['signal_strength']} dB\nDistance: {row['distance']} m\nName: {row['name']}"
    ).add_to(map)

for tower, _ in towers.items():
    folium.Marker(
        location=towers[tower],
        popup=f"{tower}",
        icon=folium.Icon(icon='star', color='red')  # You can use a built-in icon as well
    ).add_to(map)

tasd = re.compile(r'^(SK|BR|LR)\d{4}$')
for wp in gpx.waypoints:
    if not wp.name:
        continue

    if tasd.match(wp.name):
        color = "gray"
    else:
        continue

    # color="orange"
    folium.Circle(
        location=[wp.latitude, wp.longitude],
        radius=100,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        popup=wp.name
    ).add_to(map)

# Save the map as an HTML file
map.save("wifi_locations_map.html")
