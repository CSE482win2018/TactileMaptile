import os
from flask import Flask, g, request, current_app, jsonify, abort, send_file, send_from_directory
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

@app.route('/api/map', methods=['POST'])
def create_map():
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
    stl_path = obj_out = os.path.join(os.getcwd(), 'map_files', 'map.stl').replace("\\", "/")

    # convert to obj
    map_generator_dir = os.path.join(os.getcwd(), 'map_generator', 'build', 'install', 'map_generator', 'bin', 'map_generator').replace("\\", "/")
    print(map_generator_dir)
    args = [osm_path, obj_path, json_path]
    a = [map_generator_dir] + args
    print(a)
    obj_convert_result = subprocess.run(' '.join(a), shell=True)
    print(obj_convert_result.returncode)

    blender_args = ['--scale', str(scale), '--size', str(size), obj_path, json_path, blend_path, stl_path]
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
    return jsonify({'foo': 'bar'})

if __name__ == '__main__':
    app.debug = True
    app.run()

