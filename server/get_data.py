import urllib.request
import subprocess

# osm_path = "C:\\Users\\liuz3\\Desktop\\Winter 2018\\CSE482\\example.osm"
# url = "http://api.openstreetmap.org/api/0.6/map?bbox=11.54,48.14,11.543,48.145"

def store_map(osm_path="C:\\Users\\liuz3\\Desktop\\Winter 2018\\CSE482\\example2.osm", 
		coord="-122.31216,47.65468,-122.30580,47.65722"):
	print("fetching data")
	url = "http://api.openstreetmap.org/api/0.6/map?bbox=" + coord
	osm_data = urllib.request.urlopen(url, timeout=120).read()
	print("reading data...")
	with open(osm_path, 'wb') as f:
		f.write(osm_data)
	print("reading done")

def osm_to_obj(osm_path="C:\\Users\\liuz3\\Desktop\\Winter 2018\\CSE482\\example2.osm",
		obj_path="C:\\Users\\liuz3\\Desktop\\Winter 2018\\CSE482\\example2_latest.obj",
		osm2world_path="C:\\Users\\liuz3\\Desktop\\Winter 2018\\CSE482\\OSM2World-latest-bin\\OSM2World.jar"):
	
	cmd = [
		'java', '-Xmx1G',
		'-jar', osm2world_path,
		'-i', osm_path,
		'-o', obj_path]
	print("converting to obj file...")
	output = subprocess.check_output(cmd).decode("utf-8")
	print(output)

def obj_to_blend(obj_path="C:\\Users\\liuz3\\Desktop\\Winter 2018\\CSE482\\example2_latest.obj", 
		converter_path="C:\\Users\\liuz3\\Desktop\\Winter 2018\\CSE482\\TactileMaptile\\map_generator\\convert.py", 
		out_path="C:\\Users\\liuz3\\Desktop\\Winter 2018\\CSE482\\example2_latest.blend"):
	cmd = ['blender', '-b', 
			'-P', converter_path,
			'--', obj_path,
			out_path]
	print("converting to blend file...")
	output = subprocess.check_output(cmd).decode("utf-8")

def main():
	# The parameters needed for fetching data are:
	# 1. "coord": min longitude, min latitude, max longitude, max latitude 
	coord = "-122.31216,47.65468,-122.30580,47.65722"
	# 2. "osm_path": path for storing the osm file
	store_map(coord=coord)
	
	# Parameters for converting to .obj file:
	# 1. "osm_path": path to the .osm file
	# 2. "obj_path": path for storing the .obj file
	# 3. "osm2world_path": path for the .jar file for OSM2WORLD
	osm_to_obj()

	# Parameters for converting to .stl file:
	# 1. "obj_path": path for .obj file 
	# 2. "converter_path": path for the converter python file used by blender
	# 3. "out_path": path for the output .blend file
	obj_to_blend()

if __name__ == '__main__':
	main()