import bpy
import bmesh
from mathutils import Vector
import math
import sys

ROAD_HEIGHT_CAR_MM = 0.82 # 3 x 0.25-0.3mm layers
ROAD_HEIGHT_PEDESTRIAN_MM = 1.5
BUILDING_HEIGHT_MM = 2.9
BASE_HEIGHT_MM = 10
BASE_OVERLAP_MM = 0.01
WATER_AREA_DEPTH_MM = 1.5
WATER_WAVE_DISTANCE_MM = 10.3
WATERWAY_DEPTH_MM = 0.55 # 2 x 0.25-0.3mm layers
BORDER_WIDTH_MM = 1.2 # 3 shells
BORDER_HEIGHT_MM = (ROAD_HEIGHT_PEDESTRIAN_MM + BUILDING_HEIGHT_MM) / 2
BORDER_HORIZONTAL_OVERLAP_MM = 0.05
MARKER_HEIGHT_MM = BUILDING_HEIGHT_MM + 2
MARKER_RADIUS_MM = MARKER_HEIGHT_MM * 0.5

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
    obj_bounds = [get_obj_bounds(x) for x in bpy.context.scene.objects]
    min_x = min(obj_bounds, key=lambda x:x[0])[0]
    min_y = min(obj_bounds, key=lambda x:x[1])[1]
    max_x = max(obj_bounds, key=lambda x:x[2])[2]
    max_y = max(obj_bounds, key=lambda x:x[3])[3]
    return min_x, min_y, max_x, max_y

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
    return cube

def import_obj_file(obj_path):
    bpy.ops.import_scene.obj(filepath=obj_path, axis_forward='X', axis_up='Y')

def export_blend_file(blend_path):
    bpy.ops.wm.save_as_mainfile(filepath=blend_path, check_existing=False, compress=True)

def depress_buildings(base):
    z_max_base = max(v.co[2] for v in base.data.vertices)
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    buildings = [o for o in bpy.context.scene.objects if o.name.startswith('Building') and 'Entrance' not in o.name]
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
            return abs(vertex.co[2] - z_min) < 0.1

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

        building.location += Vector((0, 0, 5))

        print('extruding')

        # extrude building down
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = building
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={ "value": (0.0, 0.0, -(5 + base.dimensions[2])) })

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

    # intersect the joined buildigns with the base
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

    # for name,base_vertices in building_bases.items():
    #     print(">>>", name, "base vertices")
    #     for v in base_vertices:
    #         print(v)

    # delete faces of building outlines
    def get_building_face(face_verts, building_bases):
        # do all vertices of a face lie on the same building base?
        for name,base_verts in building_bases.items():
            if len(face_verts) > len(base_verts):
                continue
            matches = 0
            for f in face_verts:
                match = False
                for b in base_verts:
                    if abs(f[0] - b[0]) < 0.0001 and abs(f[1] - b[1]) < 0.0001 and abs(f[2] - b[2]) < 1:
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
            f.select = True

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.delete(type='ONLY_FACE')

def convert_osm(osm_obj_path, osm_blend_path):
    scale = 1000
    import_obj_file(osm_obj_path)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(rotation=True)
    # bpy.context.scene.update()
    box = get_scene_bounds()
    min_x, min_y, max_x, max_y = box
    mm_to_units = scale / 1000
    # add_borders(min_x, min_y, max_x, max_y, BORDER_WIDTH_MM * mm_to_units, 0, BORDER_HEIGHT_MM * mm_to_units, (BUILDING_HEIGHT_MM + 1) * mm_to_units)
    base_height = BASE_HEIGHT_MM * mm_to_units
    overlap = BASE_OVERLAP_MM * mm_to_units # move cube this much up so that it overlaps enough with objects they merge into one object
    base_cube = create_cube(min_x, min_y, max_x, max_y, -base_height + overlap, overlap)
    base_cube.name = 'Base'
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=True, scale=True)

    depress_buildings(base_cube)
    export_blend_file(osm_blend_path)

def main(argv):
    if len(argv) != 2:
        print("usage: convert.py [path to input .obj file] [path to output .blend file]")
        return
    
    convert_osm(argv[0], argv[1])

if __name__ == '__main__':
    main(sys.argv[sys.argv.index('--') + 1:])