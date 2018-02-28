import os
from flask import Flask, g, request, current_app, jsonify, abort, send_file, send_from_directory
import sqlite3
import math
from werkzeug.exceptions import BadRequest
import subprocess
import io
import random
import json
import itertools

from bus_utils import get_bus_stop_ids, bus_stops_for_node
from get_osm import store_map

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(current_app.config['DATABASE'], isolation_level=None)
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    rv.row_factory = dict_factory
    return rv

def init_db():
    """Initializes the database."""
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def register_cli(app):
    @app.cli.command('initdb')
    def initdb_command():
        """Creates the database tables."""
        init_db()
        print('Initialized the database.')

def register_teardowns(app):
    @app.teardown_appcontext
    def close_db(error):
        print("closing app!")
        """Closes the database again at the end of the request."""
        if hasattr(g, 'sqlite_db'):
            g.sqlite_db.close()
      
app = Flask(__name__, static_folder='react_app/build')
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flask.db'),
    DEBUG=True,
    SECRET_KEY='secret',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

register_cli(app)
register_teardowns(app)

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if(path == ""):
        return send_from_directory('react_app/build', 'index.html')
    else:
        if(os.path.exists("react_app/build/" + path)):
             return send_from_directory('react_app/build', path)
        else:
             return send_from_directory('react_app/build', 'index.html')

@app.route('/api/map/init', methods=['POST'])
def init_map():
    print('creating map')
    print(request.form)

    scale = int(request.form['scale'])
    size = int(request.form['size'])        

    bounds = {
        'min_lat': float(request.form['min_lat']),  
        'max_lat': float(request.form['max_lat']), 
        'min_lng': float(request.form['min_lng']),
        'max_lng': float(request.form['max_lng'])
    }
    # get osm file
    store_map('map_files/map.osm', bounds)

    print("Got osm file.")

    osm_path = os.path.join(os.getcwd(), 'map_files', 'map.osm').replace("\\", "/")
    obj_path = os.path.join(os.getcwd(), 'map_files', 'map.obj').replace("\\", "/")
    json_path = os.path.join(os.getcwd(), 'map_files', 'map.json').replace("\\", "/")
    blend_path = os.path.join(os.getcwd(), 'map_files', 'map.blend').replace("\\", "/")

    # convert to obj
    map_generator_dir = os.path.join(os.getcwd(), 'map_generator', 'build', 'install', 'map_generator', 'bin', 'map_generator').replace("\\", "/")
    print(map_generator_dir)
    args = [osm_path, obj_path, json_path]
    a = [map_generator_dir] + args
    print(a)
    obj_convert_result = subprocess.run(' '.join(a), shell=True)
    print(obj_convert_result.returncode)

    json_data = None
    bus_stops = {}
    with open(json_path, 'r') as json_file:
        json_data = json.load(json_file)
        bus_stop_ids = get_bus_stop_ids(json_data)
        db = get_db()
        query = 'SELECT * FROM bus_stops where node_id in ({0})'.format(','.join('?'*len(bus_stop_ids)))
        print(query)
        cur = db.execute(query, list(bus_stop_ids))
        rows = cur.fetchall()
        groups = {k: list(g) for k, g in itertools.groupby(rows, key=lambda x: x['node_id'])}
        print("groups:", groups)
        for bus_stop_id in bus_stop_ids:
            if bus_stop_id in groups:
                print("found {0} in db".format(bus_stop_id))
                bus_stops = groups[bus_stop_id]
            else:
                print("could not find {0} in db".format(bus_stop_id))
                bus_stops_res = bus_stops_for_node(bus_stop_id)
                bus_stops = [{'node_id': bus_stop_id, 'name': x['name'], 'ref': int(x['ref'])} for x in bus_stops_res]
                bus_stop_queries = [(x['node_id'], x['name'], x['ref']) for x in bus_stops]
                # insert into database
                query = 'INSERT INTO bus_stops(node_id, name, ref) VALUES (?, ?, ?)'
                db.executemany(query, bus_stop_queries)
            
            # add bus stops to json data
            json_data[str(bus_stop_id)]['busRoutes'] = bus_stops
        
        db.commit()
        bus_stops = {}
        for bus_stop_id in bus_stop_ids:
            bus_stops[bus_stop_id] = json_data[str(bus_stop_id)]
        print('final bus stops:', bus_stops)

    # write bus stops to new json file
    bus_stop_json_path = os.path.join(os.getcwd(), 'map_files', 'map_extra.json').replace("\\", "/")
    with open(bus_stop_json_path, 'w') as file:
        print('writing extra json to', bus_stop_json_path)
        json.dump(json_data, file)

    obj = None
    with open(obj_path, 'rb') as obj_file:
        obj = obj_file.read()

    db = get_db()
    id = random.randint(1, 100000)
    db.execute('DELETE FROM map_files WHERE id = ?', (id,))
    db.execute('INSERT INTO map_files(id, map_obj, size, scale) VALUES(?, ?, ?, ?)', (id, obj, size, scale))
    db.commit()

    return jsonify({'success': True, 'id': id, 'mapData': {'busStops': bus_stops}})

@app.route('/api/map/<int:id>/create', methods=['POST'])
def create_map(id):
    obj_path = os.path.join(os.getcwd(), 'map_files', 'map.obj').replace("\\", "/")
    json_path = os.path.join(os.getcwd(), 'map_files', 'map.json').replace("\\", "/")
    blend_path = os.path.join(os.getcwd(), 'map_files', 'map.blend').replace("\\", "/")
    stl_path = os.path.join(os.getcwd(), 'map_files', 'map.stl').replace("\\", "/")

    # change to read obj file from database
    db = get_db()
    cur = db.execute('SELECT size, scale from map_files WHERE id = ?', (id,))
    row = cur.fetchone()
    size = row['size']
    scale = row['scale']
    db.commit()

    data = request.get_json()
    print("request data:", data)
    bus_stops = ','.join(data['busStops'])

    blender_args = ['--scale', str(scale), '--size', str(size), '--bus-stops', bus_stops, obj_path, json_path, blend_path, stl_path]
    blender_result = subprocess.run(['blender', '-b', '-P', 'convert.py', '--'] + blender_args)
    print(blender_result.returncode)

    stl = None
    with open(stl_path, 'rb') as stl_file:
        stl = stl_file.read()

    db.execute('UPDATE map_files SET map_stl=? where id = ?', (stl, id))
    db.commit()

    return jsonify({'success': True})


@app.route('/api/map/<int:id>/stl')
def get_stl(id):
    print(id)
    db = get_db()
    cur = db.execute('select map_stl from map_files where id = ?', (id,))
    row = cur.fetchone()
    if row is None:
        raise BadRequest('No stl data for id {0} found.'.format(id))

    stl = row['map_stl']
    sio = io.BytesIO()
    sio.write(stl)
    sio.seek(0)
    return send_file(sio, mimetype='application/vnd.ms-pki.stl')


@app.route('/foo', methods=['GET'])
def get_foo():
    return jsonify({'foo': 'bar'})

if __name__ == '__main__':
    app.debug = True
    app.run()

