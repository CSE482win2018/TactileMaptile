import os
from flask import Flask, g, request, current_app, jsonify, send_from_directory
import sqlite3
import subprocess

from get_osm import *

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(current_app.config['DATABASE'])
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
        """Closes the database again at the end of the request."""
        if hasattr(g, 'sqlite_db'):
            g.sqlite_db.close()

# @app.route('/add', methods=['POST'])
# def add_entry():
#     db = get_db()
#     db.execute('insert into entries (title, text) values (?, ?)',
#                [request.form['title'], request.form['text']])
#     db.commit()
#     return 
      
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
'''
routes
'''

@app.route('/api/map', methods=['POST'])
def create_map():
    print('creatting map')
    print(request.form)
    width = float(request.form['width'])
    height = float(request.form['height'])
    lat = float(request.form['lat'])
    lng = float(request.form['lng'])

    bounds = {
        'min_lat': lat - 0.003,
        'max_lat': lat + 0.003,
        'min_lng': lng - 0.003,
        'max_lng': lng + 0.003
    }

    # get osm file
    store_map('map_files/map.osm', bounds)

    print("Got osm file.")

    osm_path = os.path.join(os.getcwd(), 'map_files', 'map.osm').replace("\\", "/")
    obj_path = os.path.join(os.getcwd(), 'map_files', 'map.obj').replace("\\", "/")
    blend_path = os.path.join(os.getcwd(), 'map_files', 'map.blend').replace("\\", "/")
    stl_path = obj_out = os.path.join(os.getcwd(), 'map_files', 'map.stl').replace("\\", "/")

    # convert to obj
    appArgs = "-PappArgs=\"['" + osm_path + "', '" + obj_path + "']\""
    print(appArgs)
    obj_convert_result = subprocess.run(['gradle', 'run', appArgs], cwd='map_generator')
    print(obj_convert_result.returncode)

    blender_result = subprocess.run(['blender', '-b', '-P', 'convert.py', '--', obj_path, blend_path, stl_path])
    print(blender_result.returncode)

    return jsonify({'success': True})

@app.route('/api/map/stl')
def get_stl():
    return send_from_directory('map_files', 'map.stl')

@app.route('/foo', methods=['GET'])
def get_foo():
    db = get_db()
    cur = db.execute('select * from foo')
    r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
    print(r)
    return jsonify(r)