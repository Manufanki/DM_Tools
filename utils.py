import re
import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

#region Methods
def GetCurrentUnits():
    lu = bpy.context.scene.unit_settings.length_unit

    if lu == 'KILOMETERS':
        return ('km', 1000)
    elif lu == 'METERS':
        return ('m', 1)
    elif lu == 'CENTIMETERS':
        return ('cm', 1/100)
    elif lu == 'MILLIMETERS':
        return ('mm', 1/1000)
    elif lu == 'MICROMETERS':
        return ('mcm', 1000000)
    elif lu == 'MILES':
        return ('mi', 1760)
    elif lu == 'FEET':
        return ('ft', 1/3.28084)
    elif lu == 'INCHES':
        return ('in', 1/39.37007874)
    elif lu == 'THOU':
        return ('thou', 1 / 39370.1)
    else:
        return ('bu', 1)

def check_if_collection_exists(name, i = 0, collection = None):
        
    tmp_name = name
    if i != 0:
        tmp_name = name + "." + str(i)
    if bpy.data.collections.get(tmp_name) is None:
        collection = bpy.data.collections.new(tmp_name)
        return collection
    else:
        i+=1
        collection = check_if_collection_exists(name, i)

    if collection is not None:
        return collection

def bu_to_unit(value, scale):
    return value / scale

def unit_to_bu(value, scale):
    return value * scale

def CreateMapMaterial(self, context,image):
    material_map = bpy.data.materials.new(name="Map MATERIAL")
    material_map.use_nodes = True
    
    material_map.node_tree.nodes.remove(material_map.node_tree.nodes.get('Principled BSDF'))

    material_out = material_map.node_tree.nodes.get('Material Output')
    material_out.location = (200,0)
    
    tex_node = material_map.node_tree.nodes.new('ShaderNodeTexImage')
    tex_node.location = (-400,0)
    
    tex_node.image = image

    transparent_node = material_map.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    transparent_node.location = (-200,100)

    shaderMix_node = material_map.node_tree.nodes.new('ShaderNodeMixShader')
    shaderMix_node.location = (0,0)
    shaderMix_node.inputs[0].default_value = 1.0

    material_map.node_tree.links.new(transparent_node.outputs[0], shaderMix_node.inputs[1])
    material_map.node_tree.links.new(tex_node.outputs[0], shaderMix_node.inputs[2])
    material_map.node_tree.links.new(shaderMix_node.outputs[0], material_out.inputs[0])
    
    material_map.blend_method = 'BLEND'
    material_map.shadow_method = 'NONE'
    return material_map

def  CreatePlayerMaterial(self, context, color):
    material_player = bpy.data.materials.new(name="Player MATERIAL")
    material_player.use_nodes = True
    
    material_player.node_tree.nodes.remove(material_player.node_tree.nodes.get('Principled BSDF'))

    material_out = material_player.node_tree.nodes.get('Material Output')
    material_out.location = (0,0)

    emit_node = material_player.node_tree.nodes.new('ShaderNodeEmission')
    emit_node.location = (-200,0)
    emit_node.inputs[0].default_value = color
    material_player.node_tree.links.new(emit_node.outputs[0], material_out.inputs[0])

    material_player.shadow_method = 'NONE'
    return material_player

def  CreateNPCMaterial(self, context, color):
    material_player = bpy.data.materials.new(name="NPC MATERIAL")
    material_player.use_nodes = True
    
    principled_node = material_player.node_tree.nodes.get('Principled BSDF')

    principled_node.inputs[0].default_value = color
    principled_node.inputs[19].default_value = color
    principled_node.inputs[20].default_value = 0
    material_player.shadow_method = 'NONE'
    return material_player

def CreateCaveMaterial(self, context):
    dm_property = context.scene.dm_property
    material_cave = dm_property.cave_Mat
    if material_cave is None:
        material_cave = bpy.data.materials.new(name="Cave MATERIAL")
        material_cave.use_nodes = True

        material_cave.node_tree.nodes.remove(material_cave.node_tree.nodes.get('Principled BSDF'))

        material_out = material_cave.node_tree.nodes.get('Material Output')
        material_out.location = (0,0)

        transparent_node = material_cave.node_tree.nodes.new('ShaderNodeBsdfTransparent')
        transparent_node.location = (-200,0)
        material_cave.node_tree.links.new(transparent_node.outputs[0], material_out.inputs[0])

        material_cave.blend_method = 'CLIP'
        dm_property.cave_Mat = material_cave
    return material_cave


def CreateTransparentMaterial(self, context):
    dm_property = context.scene.dm_property
    material_trans = dm_property.cave_Mat
    if material_trans is None:
        material_trans = CreateCaveMaterial(self, context)
    material_trans.shadow_method = 'NONE'
    return material_trans

def CreateBackfaceWallMaterial(self, context):
    dm_property = context.scene.dm_property
    material_bf_wall = dm_property.bf_wall_Mat
    if material_bf_wall is None:
        material_bf_wall = bpy.data.materials.new(name="BACKFACE WALL MATERIAL")
        material_bf_wall.use_nodes = True
        shaderMix_node = material_bf_wall.node_tree.nodes.new('ShaderNodeMixShader')
        shaderMix_node.location = (100,0)
        material_bf_wall.node_tree.nodes.remove(material_bf_wall.node_tree.nodes.get('Principled BSDF'))
        
        material_out = material_bf_wall.node_tree.nodes.get('Material Output')
        material_out.location = (0,0)

        transparent_node = material_bf_wall.node_tree.nodes.new('ShaderNodeBsdfTransparent')
        transparent_node.location = (-100,-400)

        emit_node = material_bf_wall.node_tree.nodes.new('ShaderNodeEmission')
        emit_node.location = (-200,0)

        geometry_node = material_bf_wall.node_tree.nodes.new('ShaderNodeNewGeometry')
        geometry_node.location = (-200,0)

        emit_node.inputs[0].default_value = (0,0,0,1)
        material_bf_wall.node_tree.links.new(geometry_node.outputs[6],  shaderMix_node.inputs[0])
        material_bf_wall.node_tree.links.new(emit_node.outputs[0], shaderMix_node.inputs[1])
        material_bf_wall.node_tree.links.new(transparent_node.outputs[0], shaderMix_node.inputs[2])
        material_bf_wall.node_tree.links.new(shaderMix_node.outputs[0], material_out.inputs[0])

        material_bf_wall.shadow_method = 'CLIP'
        dm_property.bf_wall_Mat = material_bf_wall
    return material_bf_wall

def CreateExtrudeGeoNode(self, context,obj):

    if bpy.data.node_groups.get("DND_Extruder") is not None:
        node_group = bpy.data.node_groups["DND_Extruder"]
        obj.modifiers.new(type='NODES', name="Test").node_group = node_group
    else:
        bpy.ops.object.modifier_add(type='NODES')
        bpy.ops.node.new_geometry_node_group_assign()

        node_group = obj.modifiers[-1].node_group
        node_group.name = "DND_Extruder" 
        nodes = node_group.nodes

        group_in = nodes.get('Group Input')
        group_out = nodes.get('Group Output')

        transform_node = nodes.new('GeometryNodeTransform')
        transform_node.inputs[1].default_value[2] = -2
        transform_node.location = (-200,150)

        extrude_node = nodes.new('GeometryNodeExtrudeMesh')
        extrude_node.mode = 'EDGES'
        extrude_node.inputs[3].default_value = 4

        vector_node = nodes.new('FunctionNodeInputVector')
        vector_node.location = (-200,-200)
        vector_node.vector[2] = 1

        node_group.links.new(group_in.outputs['Geometry'], transform_node.inputs['Geometry'])
        node_group.links.new(transform_node.outputs['Geometry'], extrude_node.inputs['Mesh'])
        node_group.links.new(vector_node.outputs['Vector'], extrude_node.inputs['Offset'])
        node_group.links.new(extrude_node.outputs['Mesh'], group_out.inputs['Geometry'])


def update_players(self,context, collection):
    dm_property = context.scene.dm_property

    dm_property.characterlist.clear()
    for player in collection.all_objects:
        if player.player_property.name != "":
                player_pointer = dm_property.characterlist.add()
                player_pointer.obj = player
                player_pointer.player_property = player.player_property
    sort_player_list(self, context)

def sort_player_list(self,context):
    dm_property = context.scene.dm_property
    initiative_list = {}
    for i in range(len(dm_property.characterlist)):
        initiative_list[i]  =  dm_property.characterlist[i].obj.player_property.list_index


    initiative_list = dict(sorted(initiative_list.items(), key=lambda item: item[1],reverse=True))
    
    print("sorted : ",initiative_list)

    print(list(initiative_list.keys()).index(i))

    for i in range(len(dm_property.characterlist)):
        dif = i - list(initiative_list.keys()).index(i) 
        print("before:" ,i, " : " , dif)
        k = i
        
        if dif > 0:
            for j in range(abs(dif)):
                dm_property.characterlist.move(k, k-1)
                k = k-1
                print("move up ", j)
        if dif < 0:
            for j in range(abs(dif)-1):
                dm_property.characterlist.move(k, k+1)
                k = k+1
                print("move down " , j)
        dif = k - list(initiative_list.keys()).index(i) 
        print("after:" ,i, " : " , dif)
        print()
        print()

def update_collection_name(self, contex, collection):
    try:
        self.annotation.name = self.name
    except:
        try:
            self.annotation.layers[collection.name].name = self.name
        except Exception as e:
            print(e)
    collection.name = self.name
def update_maps(self,context, collection):
    dm_property = context.scene.dm_property

    for map in dm_property.maplist:
            map.floorlist.clear()
    dm_property.maplist.clear()

    for map in collection.children:
        map_pointer = dm_property.maplist.add()
        map_pointer.map = map
        map_pointer.name = map.name

        if map_pointer.annotation is None:

            try:
                map_pointer.annotation = bpy.data.grease_pencils[map.name]
            except:
                bpy.ops.gpencil.annotation_add()
                map_pointer.annotation = context.annotation_data
                map_pointer.annotation.name = map.name
                try:
                    map_pointer.annotation.layers.remove(map_pointer.annotation.layers["Note"])
                except:
                    print("no layer Note")
                    


        for floor in map.children:
            floor_pointer = map_pointer.floorlist.add()
            floor_pointer.floor = floor
            floor_pointer.name = floor.name
            floor_pointer.annotation = map_pointer.annotation
            try:
                map_pointer.annotation.layers[floor.name]
            except:
                layer = map_pointer.annotation.layers.new(name = floor.name)
                layer.color = (1,1,1)    
    
        # map = dm_property.maplist[dm_property.maplist_data_index]
        # floor = map.floorlist[map.floorlist_data_index]
        # context.scene.grease_pencil = map.annotation
        # context.scene.grease_pencil.layers.active = context.scene.grease_pencil.layers[floor.name]

def delete_hierarchy(obj):
    names = set([obj.name])
    
    # recursion
    def get_child_names(obj):
        for child in obj.children:
            names.add(child.name)
            if child.children:
                get_child_names(child)

    get_child_names(obj)

    for n in names:
        bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)


def selectCharacter(self, context):
    bpy.ops.object.select_all(action='DESELECT')
    if self.characterlist_data_index != -1:
        for char in self.characterlist:
            char.obj.select_set(False)
        self.characterlist[self.characterlist_data_index].obj.select_set(True)
        bpy.context.view_layer.objects.active =  self.characterlist[self.characterlist_data_index].obj



def get_rayhit_loc(self, context,reg,touch_pos):
        touch_pos = Vector((touch_pos[0], touch_pos[1]))
        dm_property = context.scene.dm_property

        if reg.type == 'WINDOW':
            region = reg
            rv3d = reg.data
        else:
            return

        view_vector_mouse = view3d_utils.region_2d_to_vector_3d(region, rv3d,touch_pos)# self.touch_pos)
        ray_origin_mouse = view3d_utils.region_2d_to_origin_3d(region, rv3d,touch_pos)# self.touch_pos)
        direction = ray_origin_mouse + (view_vector_mouse * 1000)
        direction =  direction - ray_origin_mouse
        
        result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph,ray_origin_mouse, direction)
          
        if result is None:
            return
        return location

def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found

def toggleDayNight(self, context):
    for char in self.characterlist:
        player = char.obj.player_property
        if player.is_npc:
            continue
        player.spot_day.hide_viewport = self.day_night
        player.point_day.hide_viewport = self.day_night
        player.spot_night.hide_viewport = not self.day_night
        player.point_night.hide_viewport = not self.day_night


def adjustCamera(self, context):
    self.camera.data.lens = self.camera_zoom


def obj_in_objectlist(obj, list):
    for item in list:
        if item.obj == obj:
            return True
    return False

def selectMap(self, context):
    print("SELECT MAP")
    if self.maplist_data_index != -1:
        for item in self.maplist:
            item.map.hide_viewport = True
        map = self.maplist[self.maplist_data_index]
        if len(map.floorlist) > 0:
            map.floorlist_data_index = 0
        self.maplist[self.maplist_data_index].map.hide_viewport = False
        context.scene.grease_pencil = self.maplist[self.maplist_data_index].annotation

def selectFloor(self, context):
    dm_property = context.scene.dm_property
    #print("SELECT FLOOR")
    if self.floorlist_data_index != -1:
        for item in self.floorlist:
            item.floor.hide_viewport = True
        self.floorlist[self.floorlist_data_index].floor.hide_viewport = False

        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = recurLayerCollection(layer_collection, self.floorlist[self.floorlist_data_index].floor.name)
        bpy.context.view_layer.active_layer_collection = layerColl
        map = dm_property.maplist[dm_property.maplist_data_index]

        for layer in map.annotation.layers:
            layer.annotation_hide = True
        context.scene.grease_pencil = map.annotation
        map.annotation.layers.active =  map.annotation.layers[self.floorlist[self.floorlist_data_index].name]
        map.annotation.layers.active.annotation_hide = False

def addToCollection(self,context, collectionName, obj):
    for coll in obj.users_collection:
            # Unlink the object
            coll.objects.unlink(obj)

    if bpy.data.collections.get(collectionName) is None:
        collection = bpy.data.collections.new(collectionName)
        bpy.context.scene.collection.children.link(collection)
    else:
        collection = bpy.data.collections.get(collectionName)
    collection.objects.link(obj)
    return collection
