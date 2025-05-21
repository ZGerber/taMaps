import folium
import gpxpy
import re
import json

telescope_array_coords = [39.32, -112.8]
towers = {"SNCT": [39.442911, -112.844229], "SKCT": [39.422425, -112.852434], 'LRCT': [39.226160, -113.072571],}

with open("utils/TA_AllSites_20221114.gpx", "r") as f:
    gpx = gpxpy.parse(f)

# Loop through and print all waypoint attributes
# for i, wp in enumerate(gpx.waypoints):
#     print(f"\nWaypoint {i + 1}")
#     print(f"  Name:        {wp.name}")
#     print(f"  Latitude:    {wp.latitude}")
#     print(f"  Longitude:   {wp.longitude}")
#     print(f"  Elevation:   {wp.elevation}")
#     print(f"  Description: {wp.description}")
#     print(f"  Symbol:      {wp.symbol}")
#     print(f"  Type:        {wp.type}")
#
#     if wp.extensions:
#         print("  Extensions:")
#         for k, v in wp.extensions.items():
#             print(f"    {k}: {v}")

map = folium.Map(location=telescope_array_coords, zoom_start=9.9, tiles=None)

tasd = re.compile(r'^(SK|BR|LR)\d{4}$')
txsd = re.compile(r'^(SN|SR|BF|DM|KM|SC)\d{4}$')

for wp in gpx.waypoints:
    if not wp.name:
        continue

    if tasd.match(wp.name):
        color = "blue"
        color = "grey"
    elif txsd.match(wp.name):
        color = "orange"
        color = "grey"
    else:
        color = 'orange'  # skip others

    folium.Circle(
        location=[wp.latitude, wp.longitude],
        radius=150,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=wp.name
    ).add_to(map)

folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="Map data: &copy; <a href='https://opentopomap.org'>OpenTopoMap</a> contributors",
    overlay=False,
    control=True,
    name="OpenTopoMap",
    max_zoom=17).add_to(map)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    name="Esri World Imagery",
    overlay=False,
    control=True).add_to(map)

folium.TileLayer(
    tiles="https://map1.vis.earthdata.nasa.gov/wmts-webmerc/VIIRS_CityLights_2012/default/2012-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg",
    attr='Imagery © NASA GIBS, Blue Marble, Earthdata',
    name="NASA Earth at Night (2012)",
    overlay=False,
    control=True,
    max_zoom=8).add_to(map)

folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
    attr='Tiles © Esri — Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community',
    name='Esri World Topo Map',
    overlay=False,
    control=True
).add_to(map)

# folium.TileLayer(
#     tiles="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_DNB_Radiance_Brightness_Temp_BandI2_M3_I1_Night/default/2019-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg",
#     attr="NASA GIBS – VIIRS Nighttime Radiance (2019)",
#     name="Light Pollution (VIIRS Radiance)",
#     overlay=True,
#     control=True,
#     opacity=0.9,
#     max_zoom=8).add_to(map)

folium.TileLayer(
    tiles="https://tiles.lightpollutionmap.info/night/2020/{z}/{x}/{y}.png",
    attr="© Jurij Stare, VIIRS 2020",
    name="Light Pollution (Jurij Stare)",
    overlay=True,
    control=True,
    opacity=0.7,
    max_zoom=12).add_to(map)


with open('utils/gz_2010_us_040_00_5m.json', "r") as f:
    geojson_data = json.load(f)

folium.GeoJson(
    geojson_data,
    name="State Borders",
    style_function=lambda feature: {
        'fillOpacity': 0,
        'color': 'white',
        'weight': 1
    }).add_to(map)

# for tower, _ in towers.items():
#     folium.Marker(
#         location=towers[tower],
#         popup=f"{tower}",
#         icon=folium.Icon(icon='star', color='red')).add_to(map)

folium.LayerControl().add_to(map)

# Save the map as an HTML file
map.save("ta_map.html")
