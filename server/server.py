import os
from flask import Flask, g, request, current_app, jsonify, abort, send_file
import sqlite3
import math
from werkzeug.exceptions import BadRequest
import subprocess
import io
import random

from get_osm import store_map

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(current_app.config['DATABASE'], isolation_level=None)
    rv.row_factory = sqlite3.Row
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
      
app = Flask(__name__)
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

@app.route('/api/map', methods=['POST'])
def create_map():
    print('creatting map')
    print(request.form)
    width = float(request.form['width'])
    height = float(request.form['height'])
    lat = float(request.form['lat'])
    lng = float(request.form['lng'])

    miles_per_lat = 69.172
    miles_per_lng = miles_per_lat * math.cos(math.radians(lat))

    lat_width = width / miles_per_lng
    lng_height = height / miles_per_lat
    bounds = {
        'min_lat': lat - lat_width/2,
        'max_lat': lat + lat_width/2,
        'min_lng': lng - lng_height/2,
        'max_lng': lng + lng_height/2
    }
    print(bounds)

    # get osm file
    store_map('map_files/map.osm', bounds)

    print("Got osm file.")

    osm_path = os.path.join(os.getcwd(), 'map_files', 'map.osm').replace("\\", "/")
    obj_path = os.path.join(os.getcwd(), 'map_files', 'map.obj').replace("\\", "/")
    json_path = os.path.join(os.getcwd(), 'map_files', 'map.json').replace("\\", "/")
    blend_path = os.path.join(os.getcwd(), 'map_files', 'map.blend').replace("\\", "/")
    stl_path = obj_out = os.path.join(os.getcwd(), 'map_files', 'map.stl').replace("\\", "/")

    # convert to obj
    map_generator_dir = os.path.join(os.getcwd(), 'map_generator', 'build', 'install', 'map_generator', 'bin').replace("\\", "/")
    args = [osm_path, obj_path, json_path]
    obj_convert_result = subprocess.run(['map_generator'] + args, cwd=map_generator_dir, shell=True)
    print(obj_convert_result.returncode)

    blender_args = ['--scale', '1000', '--size', '15', obj_path, json_path, blend_path, stl_path]
    blender_result = subprocess.run(['blender', '-b', '-P', 'convert.py', '--'] + blender_args)
    print(blender_result.returncode)

    stl = None
    with open(stl_path, 'rb') as stl_file:
        stl = stl_file.read()

    db = get_db()
    id = random.randint(1, 100000)
    db.execute('INSERT INTO map_files VALUES(?, ?)', (id, stl))
    db.commit()

    return jsonify({'success': True, 'id': id})

@app.route('/api/map/stl/<id>')
def get_stl(id):
    print(id)
    db = get_db()
    cur = db.execute('select map_obj from map_files where id = ?', (id,))
    row = cur.fetchone()
    if row is None:
        raise BadRequest('No stl data for id {0} found.'.format(id))

    stl = row['map_obj']
    # print(type(stl))
    # print(stl)
    sio = io.BytesIO()
    sio.write(stl)
    sio.seek(0)
    return send_file(sio, mimetype='application/vnd.ms-pki.stl')
    # r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
    # print(r)
    # return jsonify(r)
    # return send_from_directory('map_files', 'map.stl')

@app.route('/foo', methods=['GET'])
def get_foo():
    db = get_db()
    cur = db.execute('select * from foo')
    r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
    print(r)
    return jsonify(r)