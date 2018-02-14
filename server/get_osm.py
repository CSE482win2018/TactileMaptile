import urllib.request
import subprocess

def store_map(osm_path, bounds):
  coord = ",".join([str(x) for x in [bounds['min_lng'], bounds['min_lat'], bounds['max_lng'], bounds['max_lat']]])
  url = "http://api.openstreetmap.org/api/0.6/map?bbox=" + coord
  osm_data = urllib.request.urlopen(url, timeout=120).read()
  with open(osm_path, 'wb') as f:
    f.write(osm_data)