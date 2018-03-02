import bpy
import bmesh
import mathutils
import math
import sys
from collections import namedtuple
import re
import time
import json
import argparse

ROAD_HEIGHT_CAR_MM = 0.82 # 3 x 0.25-0.3mm layers
ROAD_HEIGHT_PEDESTRIAN_MM = 2
BUILDING_HEIGHT_MM = 2.9
BASE_HEIGHT_MM = 2
BASE_OVERLAP_MM = 0.01
WATER_AREA_DEPTH_MM = 1.5
WATER_WAVE_DISTANCE_MM = 10.3
WATERWAY_DEPTH_MM = 0.55 # 2 x 0.25-0.3mm layers
BORDER_WIDTH_MM = 1.2 # 3 shells
BORDER_HEIGHT_MM = (ROAD_HEIGHT_PEDESTRIAN_MM + BUILDING_HEIGHT_MM) / 2
BORDER_HORIZONTAL_OVERLAP_MM = 0.05
MARKER_HEIGHT_MM = BUILDING_HEIGHT_MM + 2
MARKER_RADIUS_MM = MARKER_HEIGHT_MM * 0.5
CONE_SCALE = [8, 8, 8]

scene_data = None
verbose = False

def debug_print(*args, **kwargs):
    if verbose:
        print(*args, file=sys.stdout, **kwargs)

def get_obj_bounds(obj):
    me = obj.data
    if not hasattr(me, 'vertices') or len(me.vertices) == 0:
        return obj.location[0], obj.location[1], obj.location[0], obj.location[1]

    verts_sel = [v.co for v in me.vertices]
    min_obj_x = min(verts_sel, key=lambda x:x[0])[0]
    min_obj_y = min(verts_sel, key=lambda x:x[1])[1]
    max_obj_x = max(verts_sel, key=lambda x:x[0])[0]
    max_obj_y = max(verts_sel, key=lambda x:x[1])[1]

    return (min_obj_x, min_obj_y, max_obj_x, max_obj_y)

def get_scene_bounds():
    obj_bounds = [get_obj_bounds(x) for x in bpy.context.scene.objects if x.name.startswith('SurfaceArea@0')]
    min_x = min(obj_bounds, key=lambda x:x[0])[0]
    min_y = min(obj_bounds, key=lambda x:x[1])[1]
    max_x = max(obj_bounds, key=lambda x:x[2])[2]
    max_y = max(obj_bounds, key=lambda x:x[3])[3]
    return min_x, min_y, max_x, max_y

def get_minimum_coordinate(ob):
    bbox_corners = [ob.matrix_world * mathutils.Vector(corner) for corner in ob.bound_box]
    min_x = 1000000
    min_y = 1000000
    min_z = 1000000
    for corner in bbox_corners:
        min_x = min(min_x, corner[0])
        min_y = min(min_y, corner[1])
        min_z = min(min_z, corner[2])
    return (min_x, min_y, min_z)

def move_everything(move_by):
    vector = mathutils.Vector(move_by)
    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH':
            ob.location += vector

def all_mesh_objects():
    out = []
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH':
            continue
        if ob.name == 'map':
            # Happens when there is nothing on the map
            continue
        out.append(ob)
    return out

ob_name_matcher = re.compile('^([a-z]+)( *)(.*)$', re.IGNORECASE)

def rgb(r, g, b):
    return 'rgb(%d, %d, %d)' % (round(r*2.55), round(g*2.55), round(b*2.55))

def add_polygons(dwg, g, ob):
    mesh = ob.data
    verts = mesh.vertices
    for polygon in mesh.polygons:
        points = []
        for vert_index in polygon.vertices:
            vx, vz, vy = (verts[vert_index].co)
            points.append(('%.1f' % vx, '%.1f' % vy))
        g.add(dwg.polygon(points=points))

def add_svg_object(dwg, main_g, ob, color):
    g = dwg.g(stroke=color, fill=color)
    g['stroke-width'] = 0.3 # removes gaps between objects
    main_g.add(g)

    m = ob_name_matcher.match(ob.name)
    if m:
        ob_type = re.sub('area$', '', m.group(1).lower())
        if m.group(2):
            title = re.sub('::[a-z]+$', '', m.group(3)) + ' (' + ob_type + ')'
            g.set_desc(title)
        else:
            #g.set_desc(ob_type)
            pass
        if ob_type == 'road':
            g['stroke-width'] = 0.8 # Make roads a bit thicker so embosser draws them
    add_polygons(dwg, g, ob)

def add_road_overlay_object(dwg, main_g, ob):
    g = dwg.g(opacity=0.0, fill='red', stroke='blue')
    g['stroke-width'] = 5.0
    main_g.add(g)

    m = ob_name_matcher.match(ob.name)
    if m:
        ob_type = re.sub('area$', '', m.group(1).lower())
        if m.group(2):
            title = re.sub('::[a-z]+$', '', m.group(3)) + ' (' + ob_type + ')'
            g.set_desc(title)
            add_polygons(dwg, g, ob)

def export_svg(base_path, args):
    return
    t = time.clock()
    min_x, min_y, max_x, max_y = (args.min_x, args.min_y, args.max_x, args.max_y)
    one_cm_units = (max_y - min_y) / args.size

    import svgwrite
    dwg = svgwrite.Drawing(base_path + '.svg', profile = 'basic')
    dwg['width']  = "%.2f" % (args.size) + 'cm'
    dwg['height'] = "%.2f" % (args.size + 1) + 'cm'
    dwg['viewBox'] = "%f %f %f %f" % (min_x, min_y - one_cm_units, max_x - min_x, max_y - min_y + one_cm_units)
    dwg['shape-rendering'] = 'geometricPrecision'
    dwg['stroke-linejoin'] = 'round' # greatly reduces protruding edges caused by non-zero stroke-width

    # Group objects into different layers
    objs = all_mesh_objects()
    buildings = []
    roads_car = []
    roads_ped = []
    rails = []
    rivers = []
    water_areas = []
    for ob in objs:
        try:
            if ob.name.startswith('Road'):
                if is_pedestrian(ob.name):
                    roads_ped.append(ob)
                    print("{0} is a pedestrian path.".format(ob.name))
                else:
                    roads_car.append(ob)
            elif ob.name.startswith('Rail'):
                rails.append(ob)
            elif ob.name.startswith('Waterway') or ob.name.startswith('River'):
                rivers.append(ob)
            elif ob.name.startswith('Water') or ob.name.startswith('AreaFountain'):
                water_areas.append(ob)
            elif ob.name.startswith('Building'):
                buildings.append(ob)
            else:
                debug_print("UNHANDLED TYPE IN SVG CREATION: " + ob.name)
        except Exception as e:
            debug_print("SVG export failed {}: {}".format(ob.name, str(e)))

    # White background
    dwg.add(dwg.rect(insert=(min_x - 5, min_y - 5 - one_cm_units), size=(max_x - min_x + 10, max_y - min_y + 10 + one_cm_units), fill=rgb(100, 100, 100)))

    # A group for main content
    clip_path = dwg.defs.add(dwg.clipPath(id='main_clip'))
    clip_path.add(dwg.rect(insert=(min_x, min_y), size=(max_x - min_x, max_y - min_y)))
    main_g = dwg.add(dwg.g(clip_path='url(#main_clip)'))

    for ob in rails:
        add_svg_object(dwg, main_g, ob, rgb(0, 50, 0))
    for ob in rivers:
        add_svg_object(dwg, main_g, ob, rgb(20, 20, 100))
    for ob in water_areas:
        add_svg_object(dwg, main_g, ob, rgb(20, 20, 100))
    for ob in roads_car:
        add_svg_object(dwg, main_g, ob, rgb(70, 0, 0))
    for ob in roads_ped:
        add_svg_object(dwg, main_g, ob, rgb(0, 0, 0))
    for ob in buildings:
        add_svg_object(dwg, main_g, ob, rgb(80, 20, 100))

    # Add overlays
    for ob in objs:
        try:
            if ob.name.startswith('Road') or ob.name.startswith('Rail') or ob.name.startswith('Waterway') or ob.name.startswith('River'):
                add_road_overlay_object(dwg, main_g, ob)
        except Exception as e:
            debug_print("SVG export failed2 {}: {}".format(ob.name, str(e)))

    # Add north marker to top-right corner
    g = dwg.g(fill='black')
    g['stroke-width'] = 0
    g.set_desc('North-east corner')
    g.add(dwg.polygon(points=[
        ('%.2f' % (max_x),                      '%.2f' % (min_y - one_cm_units*0.3)),
        ('%.2f' % (max_x - one_cm_units*0.7),   '%.2f' % (min_y - one_cm_units*0.3)),
        ('%.2f' % (max_x - one_cm_units*0.7/2), '%.2f' % (min_y - one_cm_units)),
    ]))
    dwg.add(g)

    dwg.save()
    debug_print("creating SVG took " + (str(time.clock() - t)))

def create_cube(min_x, min_y, max_x, max_y, min_z, max_z):
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent()
    bpy.ops.object.mode_set(mode = 'OBJECT')
    cube.location = [ (min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2 ]
    cube.scale = [ (max_x - min_x) / 2, (max_y - min_y) / 2, (max_z - min_z) / 2 ]
    bpy.context.scene.update() # flush changes to location and scale
    # bpy.ops.object.transform_apply(location=True, scale=True)
    return cube

def add_borders(min_x, min_y, max_x, max_y, width, bottom, height, corner_height):
    borders = []
    borders.append(create_cube(min_x, min_y, min_x + width, max_y, bottom, height))
    borders.append(create_cube(max_x, min_y, max_x - width, max_y, bottom, height))
    borders.append(create_cube(min_x + width*0.99, min_y, max_x - width*0.99, min_y + width, bottom, height))
    borders.append(create_cube(min_x + width*0.99, max_y, max_x - width*0.99, max_y - width, bottom, height))
    join_objects(borders, 'Borders')

    # Marker for north-east corner
    create_cube(max_x - width*0.99, max_y - width*0.99, max_x - width*2.7, max_y - width*2.7, 0, height).name = 'CornerInside'
    create_cube(max_x, max_y, max_x - width*3, max_y - width*3, height*0.99, corner_height).name = 'CornerTop'

def create_bounds(min_x, min_y, max_x, max_y, scale, no_borders):
    mm_to_units = scale / 1000
    if not no_borders:
        add_borders(min_x, min_y, max_x, max_y, BORDER_WIDTH_MM * mm_to_units, \
                    0, BORDER_HEIGHT_MM * mm_to_units, (BUILDING_HEIGHT_MM + 1) * mm_to_units)
    base_height = BASE_HEIGHT_MM * mm_to_units
    overlap = BASE_OVERLAP_MM * mm_to_units # move cube this much up so that it overlaps enough with objects they merge into one object
    base_cube = create_cube(min_x, min_y, max_x, max_y, -base_height + overlap, overlap)
    base_cube.name = 'Base'

    return base_cube

def add_marker1(args, scale):
    min_x, min_y, max_x, max_y = (args.min_x, args.min_y, args.max_x, args.max_y)
    if args.marker1 == 'center':
        marker_x, marker_y = (0.5, 0.5)
    else:
        coords = json.loads(args.marker1)
        marker_x = float(coords['x'])
        marker_y = float(coords['y'])

    mm_to_units = scale / 1000
    radius = MARKER_RADIUS_MM * mm_to_units
    height = MARKER_HEIGHT_MM * mm_to_units
    # If the cone has sharp top, three.js won't render it remotely properly, and it'll 3D print poorly too
    bpy.ops.mesh.primitive_cone_add(vertices = 16, radius1 = radius, radius2 = radius / 8, depth = height, \
        location = [ min_x + (max_x - min_x) * marker_x, min_y + (max_y - min_y) * marker_y, height / 2 ])
    bpy.context.active_object.name = 'SelectedAddress'

def remove_everything():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Import given file as .obj and return it
def import_obj_file(obj_path):
    t = time.clock()
    bpy.ops.import_scene.obj(filepath=obj_path, axis_forward='X', axis_up='Y')
    debug_print("importing STL took " + (str(time.clock() - t)))

# Extrude floor to a flat-roofed building
def extrude_building(ob, height):
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={ "value": (0.0, 0.0, height) })
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent()
    bpy.ops.object.mode_set(mode = 'OBJECT')

def clip_object_to_map(ob, min_co, max_co):
    try:
        #debug_print("Clipping {}".format(ob.name))
        bpy.context.scene.objects.active = ob
        bpy.ops.object.mode_set(mode = 'EDIT')

        # Clip from all sides
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=min_co, plane_no=(-1, 0, 0), clear_outer=True, use_fill=True)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=min_co, plane_no=(0, -1, 0), clear_outer=True, use_fill=True)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=max_co, plane_no=(1, 0, 0), clear_outer=True, use_fill=True)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=max_co, plane_no=(0, 1, 0), clear_outer=True, use_fill=True)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(plane_co=min_co, plane_no=(0, 0, -1), clear_outer=True, use_fill=True)

        bpy.ops.object.mode_set(mode = 'OBJECT')
        return True
    except Exception as e:
        debug_print("Failed to clip {}: {}".format(ob.name, str(e)))
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        ob.select = True
        bpy.context.scene.objects.active = ob
        try:
            bpy.ops.object.delete()
        except Exception as e:
            debug_print("Failed to remove {}: {}".format(ob.name, str(e)))
        return False

def join_selected(name):
    combined = bpy.context.selected_objects[0]
    bpy.context.scene.objects.active = combined
    combined.name = name
    bpy.ops.object.join()
    return combined

def join_objects(objects, name):
    if len(objects) == 0:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:
        ob.select = True
    return join_selected(name)

def join_and_clip(objects, min_co, max_co, name):
    if len(objects) == 0:

        return None
    combined = join_objects(objects, name)
    clip_object_to_map(combined, min_co, max_co)
    return combined

def raise_ob(objs, height):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = objs
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={ "value": (0.0, 0.0, height) })
    bpy.ops.object.mode_set(mode = 'OBJECT')

def water_remesh_and_extrude(object, extrude_height):
    # Extrude just enough that remeshing works
    bpy.context.scene.objects.active = object
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={ "value": (0.0, 0.0, extrude_height) })
    bpy.ops.mesh.normals_make_consistent()
    bpy.ops.object.mode_set(mode = 'OBJECT')

    # Remesh
    max_dimension = max(object.dimensions[0], object.dimensions[2])
    depth = min(max(math.log2(max_dimension) - 1, 2), 8) # Max vertex distance == 2m => max dimension 128 == remesh depth 6 (or so)
    modifier = object.modifiers.new('Modifier', 'REMESH')
    modifier.octree_depth = math.ceil(depth)
    modifier.use_remove_disconnected = False
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)

def water_wave_pattern(object, depth, scale):
    extrude_height = 1.0
    water_remesh_and_extrude(object, extrude_height)

    # Start creating wave pattern
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bm = bmesh.from_edit_mesh(object.data)
    bm.verts.ensure_lookup_table()

    # Record x,z positions of edge verts (verts of non-horizontal edges)
    edge_verts = {}
    for edge in bm.edges:
        verts = edge.verts
        if abs(verts[0].co.y - verts[1].co.y) > extrude_height / 2:
            edge_verts[str(verts[0].co.x) + ',' + str(verts[0].co.z)] = True

    # Set top verts' y positions. Bottom verts are at 0.
    density = math.pi * 2 / WATER_WAVE_DISTANCE_MM / (scale/1000)
    for v in bm.verts:
        if v.co.y > extrude_height / 2:
            min_height = -10000
            if str(v.co.x) + ',' + str(v.co.z) in edge_verts:
                min_height = depth / 4
            v.co.y = max(min_height, (math.sin(v.co.x * density) + math.sin(v.co.z * density)) * depth / 4 + depth / 2)
        else:
            v.co.y = 0
    bmesh.update_edit_mesh(object.data, tessface=False, destructive=False)

    bpy.ops.object.mode_set(mode = 'OBJECT')

def is_pedestrian(road_name, scene_data):
    road_id = road_name[road_name.index('@') + 1:]
    print("checking", road_id)
    print("   ", scene_data[road_id])
    return scene_data[road_id].get('highway') == 'footway'

## Disable stdout buffering
#class Unbuffered(object):
#   def __init__(self, stream):
#       self.stream = stream
#   def write(self, data):
#       self.stream.write(data)
#       self.stream.flush()
#   def __getattr__(self, attr):
#       return getattr(self.stream, attr)
#
#sys.stdout = Unbuffered(sys.stdout)


# Join edges that seem to form two ends of the same logical road or railway
def join_matching_edges(ob, min_x, min_y, max_x, max_y):
    lt = 0.2  # length difference + -
    dt = 0.15  # max distance
    at = 0.5  # max sin(angle)  (30°)

    bpy.context.scene.objects.active = ob
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    from math import sin
    bm = bmesh.from_edit_mesh( bpy.context.object.data )
    bm.edges.ensure_lookup_table()

    center   = lambda e : ( e.verts[0].co + e.verts[1].co ) / 2
    length   = lambda e : ( e.verts[0].co - e.verts[1].co ).length
    dist     = lambda v1, v2: (  v2 -  v1 ).length
    sinAngle = lambda e1, e2: abs(sin((e1.verts[1].co - e1.verts[0].co).angle(e2.verts[1].co - e2.verts[0].co)))

    def point_between_edge_neighbor_verts(e):
        # Return middle of the verts adjacent to the edge
        verts = []
        for v in e.verts:
            for linked_e in v.link_edges:
                verts.extend((vv for vv in linked_e.verts if vv != e.verts[0] and vv != e.verts[1]))
        if len(verts) != 2:
            #debug_print("edge has non-2 adjacent verts: " + str(len(verts)))
            return None
        return ((verts[0].co[0] + verts[1].co[0]) / 2, \
                (verts[0].co[1] + verts[1].co[1]) / 2, \
                (verts[0].co[2] + verts[1].co[2]) / 2)

    class CEdge:
        def __init__(self, e, into_edge):
            self.e = e
            self.center = center(e)
            self.length = length(e)
            self.into_edge = into_edge
            self.welded = False

    # Lengthen an edge that is supposedly at the end of a road, in an attempt to make roads'
    # widths consistent, instead of being the more narrow the greater the angle of their end edge.
    radians_90degrees = math.pi / 2
    def lengthen_edges(ce1, ce2):
        for ce in (ce1, ce2):
            verts = ce.e.verts
            edge_v = mathutils.Vector(verts[0].co) - mathutils.Vector(verts[1].co)
            angle = ce.into_edge.angle(edge_v)
            if abs(angle - radians_90degrees) > radians_90degrees / 9:
                multiplier = 1 / math.sin(angle)
                debug_print("angle: %f, mult: %f" % (angle * (90 / radians_90degrees), multiplier))
                if multiplier > 3:
                    debug_print("abnormally high multiplier, not lengthening")
                else:
                    verts[0].co = ce.center + (verts[0].co - ce.center) * multiplier
                    verts[1].co = ce.center + (verts[1].co - ce.center) * multiplier

    def filter_edges(edges):
        out = []
        for e in edges:
            if len(e.link_faces) != 1:
                continue
            # Because roads are clipped at the edges, funny coincidences can happen, so ignore those edges
            c = center(e)
            if abs(c[0] - min_x) < 0.1 or abs(c[0] - max_x) < 0.1 or abs(c[2] - min_y) < 0.1 or abs(c[2] - max_y) < 0.1:
                continue
            point_between_edges = point_between_edge_neighbor_verts(e)
            if not point_between_edges:
                continue
            vector_into_edge_face = center(e) - mathutils.Vector(point_between_edges)
            if vector_into_edge_face.length == 0:
                continue
            out.append(CEdge(e, vector_into_edge_face / vector_into_edge_face.length))
        return out
    candidate_edges = filter_edges(bm.edges)

    # Index edges into search tree
    edge_index_to_ce = {} # enable finding CEdge by edge
    kd = mathutils.kdtree.KDTree(len(candidate_edges))
    for i, ce in enumerate(candidate_edges):
        kd.insert(ce.center, i)
        edge_index_to_ce[ce.e.index] = ce
    kd.balance()

    def mark_all_t_junction_edges_welded(cedge):
        face_edges = cedge.e.link_faces[0].edges
        if len(face_edges) == 6:
            # Faces with 6 edges are probably T junctions. If we allow multiple roads
            # to connect to them, we often get a road that intersects itself (because X junctions are disabled in OSM2World)
            for fe in face_edges:
                fe_ce = edge_index_to_ce.get(fe.index, None)
                if fe_ce:
                    fe_ce.welded = True

    to_weld = {}
    for i, ce in enumerate(candidate_edges[:-1]):
        if ce.welded:
            continue
        ce.welded = True
        lmin = ce.length - lt
        lmax = ce.length + lt
        matches = []
        for (_co, oe_index, _dist) in kd.find_range(ce.center, dt):
            oe = candidate_edges[oe_index]
            if not oe.welded and lmin < oe.length < lmax and sinAngle(ce.e, oe.e) < at:
                turn_angle = ce.into_edge.angle(-oe.into_edge)
                if turn_angle > math.pi * 0.6: # pi * 0.5 is 90%
                    #debug_print("not merging edges (%s, %s) pointing to opposite directions, angle is %f" % (ce.e, oe.e, turn_angle))
                    continue
                matches.append(oe)
                oe.welded = True

        if len(matches) == 1:
            # Join nothing where >2 ways meet, else all roads in the scene may become joined and intersect itself
            ev1, ev2 = ce.e.verts[:]
            oev1, oev2 = matches[0].e.verts[:]
            if dist(ev1.co, oev1.co) < dist(ev1.co, oev2.co) :
                if ev1 != oev1: to_weld[ev1] = oev1
                if ev2 != oev2: to_weld[ev2] = oev2
            else :
                if ev1 != oev2: to_weld[ev1] = oev2
                if ev2 != oev1: to_weld[ev2] = oev1
                # TODO: move welded verts to locations between the originals?
            lengthen_edges(ce, matches[0])
            mark_all_t_junction_edges_welded(ce)
            mark_all_t_junction_edges_welded(matches[0])

    debug_print("%s: melding %d out of %d edges" % (ob.name, len(to_weld) / 2, len(bm.edges)))
    bmesh.ops.weld_verts(bm, targetmap = to_weld)
    bmesh.update_edit_mesh(bpy.context.object.data ,True)
    bpy.ops.object.mode_set(mode = 'OBJECT')

# Decimating gets rid of useless and harmful lane edges, as well as changing
# tris to n-gons (important to find edge's "direction")
def decimate(ob):
    # Decimating gets rid of useless lanes
    bpy.context.scene.objects.active = ob
    modifier = ob.modifiers.new('Modifier', 'DECIMATE')
    modifier.decimate_type = 'DISSOLVE'
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)

# Fatten slightly to cause overlap and avoid faces too close to each other
def fatten(ob):
    bpy.context.scene.objects.active = ob
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.shrink_fatten(value=-0.05) # less than this and programs start to "remove double vertices"
    bpy.ops.object.mode_set(mode = 'OBJECT')

def do_ways(ways, height, min_x, min_y, max_x, max_y):
    if ways == None:
        return
    t = time.clock()
    decimate(ways)
    join_matching_edges(ways, min_x, min_y, max_x, max_y)
    raise_ob(ways, height)
    fatten(ways)
    debug_print("processing %s took %.2f" % (ways.name, time.clock() - t))

def do_road_areas(roads, height):
    if roads == None:
        return
    t = time.clock()
    decimate(roads)
    raise_ob(roads, height)
    fatten(roads)
    #debug_print("processing %s took %.2f" % (roads.name, time.clock() - t))

def depress_buildings(buildings, min_x, max_x, min_y, max_y, min_z, max_z):
    base = bpy.context.scene.objects['Base']
    z_max_base = max(v.co[2] for v in base.data.vertices)
    debug_print('z_max_base:', z_max_base)
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    building_bases = {b.name: None for b in buildings}
    for building in buildings:
        # remove faces
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        building.select = True
        bpy.context.scene.objects.active = building
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.dissolve_limited()
        bpy.ops.mesh.delete(type='ONLY_FACE')
        building.select = False

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # identify base vertices
        def is_base_vertex(z_min, vertex):
            return abs(vertex.co[2] - z_min) < 0.0001

        vertices = building.data.vertices
        z_min = min(v.co[2] for v in vertices)
        base_vertices = [v for v in vertices if is_base_vertex(z_min, v)]
        other_vertices = [v for v in vertices if not is_base_vertex(z_min, v)]

        building_bases[building.name] = [(v.co[0], v.co[1], v.co[2]) for v in base_vertices]

        # remove all other vertices
        sel_mode = bpy.context.tool_settings.mesh_select_mode
        bpy.context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        for v in other_vertices:
            v.select = True

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.delete(type='VERT')

        building.location += mathutils.Vector((0, 0, 5))

        debug_print('extruding')

        # extrude building down
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = building
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={ "value": (0.0, 0.0, -(5 + base.dimensions[2] - 0.4)) })

        bpy.context.tool_settings.mesh_select_mode = sel_mode

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

    # join all buildings to base
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    base.select = True
    bpy.context.scene.objects.active = base
    for b in buildings:
        b.select = True
    bpy.ops.object.join()

    # intersect the joined buildigs with the base
    bpy.context.scene.objects.active = base
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.intersect()
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'DESELECT')

    bpy.ops.object.mode_set(mode = 'OBJECT')

    # remove vertices above base
    for v in base.data.vertices:
        if v.co[2] > 4:
            v.select = True
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.delete(type='VERT')

    for name,base_vertices in building_bases.items():
        debug_print(">>>", name, "base vertices")
        # for v in base_vertices:
        #     debug_print(v)

    # delete faces of building outlines
    def get_building_face(face_verts, building_bases):
        # do all vertices of a face lie on the same building base?
        # debug_print("Checking: ", face_verts)
        for name,base_verts in building_bases.items():
            if len(face_verts) > len(base_verts):
                continue
            matches = 0
            for f in face_verts:
                match = False
                for b in base_verts:
                    if abs(f[0] - b[0]) < 0.001 and abs(f[1] - b[1]) < 0.001 and abs(f[2] - z_max_base) < 0.001:
                        match = True
                if match:
                    matches += 1
            if matches == len(face_verts):
                return name
        return None

    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.context.tool_settings.mesh_select_mode = [False, False, True]
    for f in base.data.polygons:
        face_verts = [base.data.vertices[i].co for i in f.vertices]
        building = get_building_face(face_verts, building_bases)
        if building is not None:
            debug_print("<><><> building:", building)
            f.select = True

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

    # remove all vertices at bottom level of base (that aren't the base's corners)
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    return

    def base_cube_vertex(vertex):
        x_side = abs(vertex.co[0] - min_x) < 0.1 or abs(vertex.co[0] - max_x) < 0.1
        y_side = abs(vertex.co[1] - min_y) < 0.1 or abs(vertex.co[1] - max_y) < 0.1
        if x_side and y_side:
            print("Bottom base vertex:", vertex.co)
        return x_side and y_side

    print("deleting rogue vertices:")
    print(min_x, max_x, min_y, max_y, min_z, max_z)
    for v in base.data.vertices:
        if abs(v.co[2] - min_z) < 0.3 and not base_cube_vertex(v):
            v.select = True
            # print("NON BASE VERTEX:", v.co)

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

def process_objects(min_x, max_x, min_y, max_y, min_z, max_z, scale, no_borders, scene_data, bus_stops):
    base_min_x = min_x
    base_max_x = max_x
    base_min_y = min_y
    base_max_y = max_y
    t = time.clock()
    mm_to_units = scale / 1000
    if not no_borders:
        space = (BORDER_WIDTH_MM - BORDER_HORIZONTAL_OVERLAP_MM) * mm_to_units
        min_x = min_x + space
        min_y = min_y + space
        max_x = max_x - space
        max_y = max_y - space
    min_co = (min_x, min_y, min_z)
    max_co = (max_x, max_y, max_z)

    print("BUS STOPS:", bus_stops)

    # First find out everything that we can join together into combined objects and do join,
    # because CPU usage is dominated by each Blender operation iterating through every object in the scene.
    roads_car = []
    roads_ped = []
    road_areas_car = []
    road_areas_ped = []
    buildings = []
    rails = []
    clippable_waterways = []
    clippable_water_areas = []
    surfaces = []
    joinable_waterways = []
    inner_water_areas = []
    deleteables = []
    other_clippables = []
    for ob in all_mesh_objects():
        if ob.name.startswith('BuildingEntrance'):
            deleteables.append(ob)
        elif ob.name.startswith('Building'):
            buildings.append(ob)
        elif ob.name.startswith('Road'):
            if is_pedestrian(ob.name, scene_data):
                print(ob.name, "is a pedestrian path")
                if ob.name.startswith('RoadArea'):
                    road_areas_ped.append(ob)
                else:
                    roads_ped.append(ob)
            else:
                if ob.name.startswith('RoadArea'):
                    road_areas_car.append(ob)
                else:
                    roads_car.append(ob)
        elif ob.name.startswith('Rail'):
            rails.append(ob)
        elif ob.name.startswith('Surface'):
            surfaces.append(ob)
        else:
            if ob.name.startswith('Bridge'):
                other_clippables.append(ob)
            n_total = len(ob.data.vertices)
            n_outside = 0
            for vert in ob.data.vertices:
                vx, vy, vz = ((ob.matrix_world * vert.co))
                if vx < min_x or vx > max_x or vy < min_y or vy > max_y:
                    n_outside = n_outside + 1

            if n_outside == 0:
                if ob.name.startswith('Waterway') or ob.name.startswith('River'):
                    joinable_waterways.append(ob)
                elif ob.name.startswith('Water') or ob.name.startswith('AreaFountain'):
                    inner_water_areas.append(ob)
                else:
                    debug_print("UNHANDLED INNER OBJECT TYPE: " + ob.name)
            elif n_outside == n_total and ob.name != 'Base':
                debug_print('deleting:', ob.name)
                deleteables.append(ob)
            else:
                if ob.name.startswith('Waterway') or ob.name.startswith('River'):
                    clippable_waterways.append(ob)
                elif ob.name.startswith('Water') or ob.name.startswith('AreaFountain'):
                    clippable_water_areas.append(ob)
                elif not ob.name.startswith('Base') and not ob.name.startswith('Corner') and not ob.name.startswith('Borders'):
                    other_clippables.append(ob)

    debug_print("initial steps took %.2f" % (time.clock() - t))

    # Delete
    t = time.clock()
    if len(deleteables) > 0:
        bpy.ops.object.select_all(action='DESELECT')
        for ob in deleteables:
            ob.select = True
        bpy.ops.object.delete()
        #debug_print("deleting %d objects took %.2f" % (len(deleteables), time.clock() - t))

    # Pre-join stuff for performance
    joined_roads_car = join_and_clip(roads_car, min_co, max_co, 'CarRoads')
    joined_roads_ped = join_and_clip(roads_ped, min_co, max_co, 'PedestrianRoads')
    joined_road_areas_car = join_and_clip(road_areas_car, min_co, max_co, 'CarRoadAreas')
    joined_road_areas_ped = join_and_clip(road_areas_ped, min_co, max_co, 'PedestrianRoadAreas')
    clipped_rails = join_and_clip(rails, min_co, max_co, 'Rails')
    # joined_buildings = join_and_clip(buildings, min_co, max_co, 'Buildings')

    # Buildings
    # debug_print('META-START:{"buildingCount":%d}:META-END\n' % (len(buildings)))
    if len(buildings):
        t = time.clock()
        depress_buildings(buildings, base_min_x, base_max_x, base_min_y, base_max_y, min_z, max_z)
        # extrude_building(joined_buildings, BUILDING_HEIGHT_MM * mm_to_units)
        # fatten(joined_buildings)
        debug_print("processing %d buildings took %.2f" % (len(buildings), time.clock() - t))

    # Bus stops
    if len(bus_stops):
        stop_nodes = {}
        for node_id, data in scene_data.items():
            if data.get('public_transport') == 'platform':
                print("routes through {0}: {1}".format(node_id, [x['ref'] for x in data.get('busRoutes', [])]))
                matching_routes = [x for x in data.get('busRoutes', []) if x['ref'] in bus_stops]
                if len(matching_routes):
                    stop_nodes[node_id] = matching_routes

        print("bus stop nodes:", stop_nodes)
        for stop_id in stop_nodes:
            bus_stop_obj = [o for o in bpy.context.scene.objects if o.name == 'BusStop@' + str(stop_id)]
            if len(bus_stop_obj) == 0:
                print("no object found for stop id: {0}...".format(stop_id))
            if len(bus_stop_obj) > 1:
                print("multiple objects for stop id: {0}...".format(stop_id))
            bus_stop_obj = bus_stop_obj[0]

            vcos = [ bus_stop_obj.matrix_world * v.co for v in bus_stop_obj.data.vertices ]
            findCenter = lambda l: ( max(l) + min(l) ) / 2

            x,y,z  = [ [v[i] for v in vcos] for i in range(3) ]
            center = [ findCenter(axis) for axis in [x,y,z] ]

            bpy.ops.mesh.primitive_cone_add()
            cube = bpy.context.active_object
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent()
            bpy.ops.object.mode_set(mode = 'OBJECT')
            cube.location = center
            cube.scale = CONE_SCALE
            bpy.context.scene.update() # flush changes to location and scale
            # bpy.ops.object.transform_apply(location=True, scale=True)

    # Waters
    t = time.clock()
    if len(joinable_waterways) > 0:
        debug_print("joinable water areas:", len(joinable_waterways))
        joined_waterways = join_objects(joinable_waterways, 'JoinedWaterways')
        raise_ob(joined_waterways, WATERWAY_DEPTH_MM * mm_to_units)
    if len(clippable_waterways) > 0:
        debug_print("clippable water ways:", len(clippable_waterways))
        clipped_waterways = join_and_clip(clippable_waterways, min_co, max_co, 'ClippedWaterways')
        raise_ob(clipped_waterways, WATERWAY_DEPTH_MM * mm_to_units)
    if len(clippable_water_areas) > 0:
        debug_print("clippable water areas:", len(clippable_water_areas))
        for water in clippable_water_areas:
            clip_object_to_map(water, min_co, max_co)
            water_wave_pattern(water, WATER_AREA_DEPTH_MM * mm_to_units, scale)
        join_objects(clippable_water_areas, 'ClippedWaterAreas')
    if len(inner_water_areas):
        debug_print("inner water areas:", len(inner_water_areas))
        for water in inner_water_areas:
            water_wave_pattern(water, WATER_AREA_DEPTH_MM * mm_to_units, scale)
        join_objects(inner_water_areas, 'InnerWaterAreas')

    for surface in surfaces:
        clip_object_to_map(surface, min_co, max_co)

    # base is already created, so remove base surfaces
    bpy.ops.object.select_all(action='DESELECT')
    for surface in surfaces:
        if surface.name.startswith('SurfaceArea@0'):
            surface.select = True
    bpy.ops.object.delete()

    for other in other_clippables:
        debug_print("Clipping:", other.name)
        clip_object_to_map(other, min_co, max_co)

    debug_print("processing waters took %.2f" % (time.clock() - t))

    # Rails
    if clipped_rails != None:
        do_ways(clipped_rails, ROAD_HEIGHT_CAR_MM * mm_to_units * 0.99, min_x, min_y, max_x, max_y) # 0.99 to avoid faces in the same coordinates with roads

    # Roads
    do_road_areas(joined_road_areas_car, ROAD_HEIGHT_CAR_MM * mm_to_units)
    do_road_areas(joined_road_areas_ped, ROAD_HEIGHT_PEDESTRIAN_MM * mm_to_units)
    do_ways(joined_roads_car, ROAD_HEIGHT_CAR_MM * mm_to_units, min_x, min_y, max_x, max_y)
    do_ways(joined_roads_ped, ROAD_HEIGHT_PEDESTRIAN_MM * mm_to_units, min_x, min_y, max_x, max_y)

def make_tactile_map(args, scene_data):
    t = time.clock()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(rotation=True)
    bpy.context.scene.update()

    bounds = scene_data['meta']['bounds']
    min_x = bounds['minX']
    min_y = bounds['minY']
    max_x = bounds['maxX']
    max_y = bounds['maxY']
    debug_print('min x: {0}, min y: {1}, max_x: {2}, max_y: {3}'.format(min_x, min_y, max_x, max_y))
    # Create the support cube and borders
    base_cube = create_bounds(min_x, min_y, max_x, max_y, args.scale, False)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=True, scale=True)
    min_x = min(x.co[0] for x in base_cube.data.vertices)
    max_x = max(x.co[0] for x in base_cube.data.vertices)
    min_y = min(x.co[1] for x in base_cube.data.vertices)
    max_y = max(x.co[1] for x in base_cube.data.vertices)
    min_z = min(x.co[2] for x in base_cube.data.vertices)
    max_z = max(x.co[2] for x in base_cube.data.vertices)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=True, scale=True)
    bus_stops = set([int(x) for x in args.bus_stops.split(',')])
    process_objects(min_x, max_x, min_y, max_y, min_z, max_z, args.scale, False, scene_data, bus_stops)
    debug_print("process_objects() took " + (str(time.clock() - t)))

    # Add marker(s)
    if args.marker1 != None:
        add_marker1(args, args.scale)

    return base_cube

def import_obj_file(obj_path):
    bpy.ops.import_scene.obj(filepath=obj_path, axis_forward='X', axis_up='Y')

def export_blend_file(blend_path):
    bpy.ops.wm.save_as_mainfile(filepath=blend_path, check_existing=False, compress=True)

def export_stl_file(stl_path, scale):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_mesh.stl(filepath=stl_path, check_existing=False, axis_forward='Y', axis_up='Z', global_scale=(1000 / scale))

def raise_roads(scale):
    roads = [o for o in bpy.context.scene.objects if o.name.startswith('Road')]
    road_height = scale / 1000 * ROAD_HEIGHT_CAR_MM
    for r in roads:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = r
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={ "value": (0.0, 0.0, road_height) })

def convert_osm(args):
    osm_obj_path = args.obj_path
    osm_json_path = args.json_path
    osm_blend_path = args.blend_path
    osm_stl_path = args.stl_path

    import_obj_file(osm_obj_path)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(rotation=True)
    bpy.context.scene.update()

    scene_data = json.load(open(osm_json_path, 'r'))

    base_cube = make_tactile_map(args, scene_data)
    move_everything([-c for c in get_minimum_coordinate(base_cube)])

    # depress_buildings(base_cube)
    # raise_roads(scale)
    export_blend_file(osm_blend_path)
    export_stl_file(osm_stl_path, args.scale)

def do_cmdline():
    parser = argparse.ArgumentParser(description='''Read an OSM map as a .obj file, modify it to a tactile map, and export as .stl''')
    parser.add_argument('--scale', metavar='N', type=int, help="scale to export STL in, 4000 would mean one Blender unit (meter) = 0.25mm (STL file unit is normally mm)")
    parser.add_argument('-v', '--verbose', action='store_true', help="debug prints")
    parser.add_argument('--size', metavar='METERS', type=float, help="print size in cm")
    parser.add_argument('-s', '--stl-to-stdout', action='store_true', help="output stl file to stdout")
    parser.add_argument('--bus-stops', help="comma separated (no spaces) list of bus routes to include")
    parser.add_argument('--marker1', metavar='MARKER', help="first marker's position relative to top left corner")
    parser.add_argument('obj_path', help='.obj file to use as input')
    parser.add_argument('json_path', help='.obj file to use as input')
    parser.add_argument('blend_path', help='.blend file to output')
    parser.add_argument('stl_path', help='.stl file to output')
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    return args

def main(argv):
    global verbose
    args = do_cmdline()
    print("args:", args)
    verbose = args.verbose
    convert_osm(args)

if __name__ == '__main__':
    main(sys.argv[sys.argv.index('--') + 1:])
