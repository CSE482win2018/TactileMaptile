import urllib.request
import subprocess
import os
import json
import csv 

# request data about the bus stop from OSM
def bus_stops_for_node(node_id):
    node_id = str(node_id)
    print('bus stops for node id:', node_id)
    url = "http://overpass.osm.rambler.ru/cgi/interpreter?data=[out:json];node(" + node_id + ");rel(bn);out;"
    json_data = urllib.request.urlopen(url, timeout=120).read().decode('utf-8')
    data = json.loads(json_data)
    print(len(data['elements']))
    return [x['tags'] for x in data['elements'] if x['tags'].get('route') == 'bus']

# get and return bus stop id's
def get_bus_stop_ids(data):
    # print(data)
    keys = set()
    for key, dic in data.items():
        if dic.get("public_transport") == "platform":
            keys.add(int(key))

    return keys

def add_bus_stops(data):
    bus_stop_ids = get_bus_stop_ids(data)
    return {node_id: bus_stops_for_node(node_id) for node_id in bus_stop_ids}
