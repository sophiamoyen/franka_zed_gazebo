import bpy

# define materials
def define_material(id, r, g, b):
    mat= bpy.data.materials.get(id)
    if mat is None:
        mat=bpy.data.materials.new(name=id)
        mat.use_nodes=False
    mat.diffuse_color=(r, g, b, 1)
    return mat

def clear_the_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
def project_to_cube(axis, target):
    bpy.ops.object.modifier_add(type='SHRINKWRAP')
    bpy.context.object.modifiers["Shrinkwrap"].wrap_method = 'PROJECT'
    if axis==2:
        bpy.context.object.modifiers["Shrinkwrap"].use_project_z = True
    if axis==1:
        bpy.context.object.modifiers["Shrinkwrap"].use_project_y = True
    if axis==0:
        bpy.context.object.modifiers["Shrinkwrap"].use_project_x = True
    bpy.context.object.modifiers["Shrinkwrap"].target = bpy.data.objects[target]
    bpy.context.object.modifiers["Shrinkwrap"].use_negative_direction = True
    bpy.context.object.modifiers["Shrinkwrap"].use_positive_direction = True
    bpy.context.object.modifiers["Shrinkwrap"].wrap_mode = 'OUTSIDE_SURFACE'

def update_location(location, projection_axis):
    location=list(location)
    if location[projection_axis]>0:
        location[projection_axis]+=0.0001
    else:
        location[projection_axis]-=0.0001
    location=tuple(location)
    return location

wood=define_material('Wood', 158/255, 129/255, 113/255)
def paint_surface(id, color, location, rotation, projection_axis):
    if id!=4 and id!=5:
        bpy.ops.mesh.primitive_plane_add(size=0.045, location=location, rotation=rotation)
        bpy.context.active_object.data.materials.append(color)
        bpy.context.active_object.name=f'plane_{id}'
        location=update_location(location, projection_axis)
        # project_to_cube(projection_axis, 'cube')
        bpy.ops.mesh.primitive_circle_add(radius=0.02, fill_type='TRIFAN', location=location, rotation=rotation)
        bpy.context.active_object.data.materials.append(wood)
        location=update_location(location, projection_axis)
        # project_to_cube(projection_axis, f'plane_{id}')
    bpy.ops.object.text_add(radius=0.03, location=location, rotation=rotation)
    bpy.context.active_object.data.materials.append(color)
    bpy.context.active_object.name=f'Text{id}'

def convert_to_mesh(name):
    obj1=bpy.data.objects[name]
    for obj2 in bpy.context.scene.objects:
        obj2.select_set( obj2 == obj1 )
    bpy.context.view_layer.objects.active=  obj1
    bpy.ops.object.convert(target="MESH")

def update_text(id, letter):
    bpy.ops.object.editmode_toggle()
    bpy.data.objects[f'Text{id}'].data.name=f'Text{id}'
    bpy.data.objects[f'Text{id}'].data.body = letter
    bpy.data.objects[f'Text{id}'].data.align_x = 'CENTER'
    bpy.data.objects[f'Text{id}'].data.align_y = 'CENTER'
    bpy.data.objects[f'Text{id}'].data.extrude=0.0001
    bpy.ops.object.editmode_toggle()
    convert_to_mesh(f'Text{id}')
    bpy.ops.object.modifier_add(type='DECIMATE')
    bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
    bpy.ops.object.modifier_apply(modifier="Decimate")

def generate_cube():
    bpy.ops.mesh.primitive_cube_add(size=0.045, location=(0, 0, 0), rotation=(0.0, 0, 0))
    bpy.context.active_object.name='cube'
    bpy.context.active_object.data.materials.append(wood)
    # paint the surfaces
    red=define_material('Red', 198/255, 45/255, 39/255)
    blue=define_material('Blue', 28/255, 69/255, 83/255)
    green=define_material('Green', 21/255, 110/255,70/255)
    yellow=define_material('Yellow', 218/255, 176/255,63/255)
    paint_surface(0, red, location=(0, 0, 0.0227), rotation=(0.0, 0, 0), projection_axis=2)
    paint_surface(1, blue, location=(0, 0, -0.0227), rotation=(0.0, 0, 0), projection_axis=2)
    paint_surface(2, green, location=(0, 0.0227, 0), rotation=(1.5708, 0, 0), projection_axis=1)
    paint_surface(3, yellow, location=(0, -0.0227, 0), rotation=(1.5708, 0, 0), projection_axis=1)
    paint_surface(4, blue, location=(0.0227, 0, 0), rotation=( 0, 1.5708, 0), projection_axis=0)
    paint_surface(5, blue, location=(-0.0227, 0, 0), rotation=( 0, 1.5708, 0), projection_axis=0)

import numpy as np
letters=np.array(['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'])
faces=np.chararray((6,26))
for i in range(6):
    np.random.shuffle(letters)
    faces[i]=letters.copy()
for c in range(28):
    clear_the_scene()
    generate_cube()
    for i in range(6):
        letter=faces[i][c%len(letters)].decode("utf-8")
        update_text(i,letter)
    bpy.data.objects.remove(bpy.data.objects['Text5'], do_unlink=True)
    bpy.context.view_layer.objects.active= bpy.data.objects["cube"]
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    bpy.ops.object.modifier_add(type='DECIMATE')
    bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
    bpy.ops.object.modifier_apply(modifier="Decimate")
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.mesh.dissolve_limited(angle_limit=0.261799)
    bpy.ops.object.editmode_toggle()
    bpy.ops.wm.collada_export(filepath=f'meshes/cube_{c}.dae', export_mesh_type_selection='render', apply_modifiers=True, include_children=True)