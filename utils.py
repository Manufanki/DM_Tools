from this import d
import bpy

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

def CreateDarknessMaterial(self, context):
    if bpy.data.materials.get("DND_Darkness"):
        material_darkness = bpy.data.materials.get("DND_Darkness")
    else:
        material_darkness = bpy.data.materials.new("DND_Darkness")
        material_darkness.use_nodes = True
        material_darkness.node_tree.nodes.remove(material_darkness.node_tree.nodes.get('Principled BSDF'))
        
        material_out = material_darkness.node_tree.nodes.get('Material Output')
        material_out.location = (300,0)

        diffuse1_node = material_darkness.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        diffuse1_node.location = (-1000,0)

        shaderRGB_node = material_darkness.node_tree.nodes.new('ShaderNodeShaderToRGB')
        shaderRGB_node.location = (-800,0)

        seperateRGB_node = material_darkness.node_tree.nodes.new('ShaderNodeSeparateRGB')
        seperateRGB_node.location = (-600,0)

        colorRamp1_node = material_darkness.node_tree.nodes.new('ShaderNodeValToRGB')
        colorRamp1_node.location = (-400,0)

        colorRamp2_node = material_darkness.node_tree.nodes.new('ShaderNodeValToRGB')
        colorRamp2_node.location = (-400,-250)

        shaderMix1_node = material_darkness.node_tree.nodes.new('ShaderNodeMixShader')
        shaderMix1_node.location = (300,0)

        shaderMix2_node = material_darkness.node_tree.nodes.new('ShaderNodeMixShader')
        shaderMix2_node.location = (100,0)

        diffuse2_node = material_darkness.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        diffuse2_node.location = (-100,-250)
        diffuse2_node.inputs[0].default_value = (0,0,0,1)

        transparent_node = material_darkness.node_tree.nodes.new('ShaderNodeBsdfTransparent')
        transparent_node.location = (-100,-400)
        
        #Linking
        material_darkness.node_tree.links.new(diffuse1_node.outputs[0], shaderRGB_node.inputs[0])
        material_darkness.node_tree.links.new(shaderRGB_node.outputs[0], seperateRGB_node.inputs[0])
        material_darkness.node_tree.links.new(seperateRGB_node.outputs[2], colorRamp1_node.inputs[0])
        material_darkness.node_tree.links.new(seperateRGB_node.outputs[0], colorRamp2_node.inputs[0])
        material_darkness.node_tree.links.new(colorRamp2_node.outputs[0], shaderMix2_node.inputs[0])
        material_darkness.node_tree.links.new(diffuse2_node.outputs[0], shaderMix2_node.inputs[1])
        material_darkness.node_tree.links.new(transparent_node.outputs[0], shaderMix2_node.inputs[2])
        material_darkness.node_tree.links.new(colorRamp1_node.outputs[0], shaderMix1_node.inputs[0])
        material_darkness.node_tree.links.new(diffuse2_node.outputs[0], shaderMix1_node.inputs[1])
        material_darkness.node_tree.links.new(shaderMix2_node.outputs[0], shaderMix1_node.inputs[2])
        material_darkness.node_tree.links.new(shaderMix1_node.outputs[0], material_out.inputs[0])
        
        material_darkness.blend_method = 'BLEND'
    return material_darkness


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

def CreatePlayerMaterial(self, context, color):
    material_player = bpy.data.materials.new(name="Player MATERIAL")
    material_player.use_nodes = True
    
    material_player.node_tree.nodes.remove(material_player.node_tree.nodes.get('Principled BSDF'))

    material_out = material_player.node_tree.nodes.get('Material Output')
    material_out.location = (0,0)

    rgb_node = material_player.node_tree.nodes.new('ShaderNodeRGB')
    rgb_node.location = (-200,0)
    rgb_node.outputs[0].default_value = color
    material_player.node_tree.links.new(rgb_node.outputs[0], material_out.inputs[0])

    material_player.shadow_method = 'NONE'
    return material_player

def CreateDistanceMaterial(self, context, color):
    material_dist = bpy.data.materials.new(name="Distance MATERIAL")
    material_dist.use_nodes = True
    
    shaderMix_node = material_dist.node_tree.nodes.new('ShaderNodeMixShader')
    shaderMix_node.location = (100,0)
    material_dist.node_tree.nodes.remove(material_dist.node_tree.nodes.get('Principled BSDF'))
    
    material_out = material_dist.node_tree.nodes.get('Material Output')
    material_out.location = (0,0)

    transparent_node = material_dist.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    transparent_node.location = (-100,-400)

    emit_node = material_dist.node_tree.nodes.new('ShaderNodeEmission')
    emit_node.location = (-200,0)

    emit_node.inputs[0].default_value = color
    shaderMix_node.inputs[0].default_value = .985
    material_dist.node_tree.links.new(emit_node.outputs[0], shaderMix_node.inputs[1])
    material_dist.node_tree.links.new(transparent_node.outputs[0], shaderMix_node.inputs[2])
    material_dist.node_tree.links.new(shaderMix_node.outputs[0], material_out.inputs[0])

    material_dist.shadow_method = 'NONE'
    material_dist.blend_method = 'BLEND'
    return material_dist

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

def CreateExtrudeGeoNode(self, context,obj):

    if bpy.data.node_groups.get("DND_Extruder") is not None:
        node_group = bpy.data.node_groups["DND_Extruder"]
        obj.modifiers.new(type='NODES', name="Test").node_group = node_group
    else:
        bpy.ops.object.modifier_add(type='NODES')

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

    dm_property.playerlist.clear()

    for player in collection.all_objects:
        if player.player_property.name != "":
                player_pointer = dm_property.playerlist.add()
                player_pointer.player = player
                player_pointer.player_property = player.player_property


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

            try:
                map_pointer.annotation.layers[floor.name]
            except:
                layer = map_pointer.annotation.layers.new(name = floor.name)
                layer.color = (0,0,0)    
    
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

def selectEnemy(self, context):
    bpy.ops.object.select_all(action='DESELECT')
    if self.enemylist_data_index != -1:
        for en in self.enemylist:
            en.enemy.select_set(False)
        self.enemylist[self.enemylist_data_index].enemy.select_set(True)
        bpy.context.view_layer.objects.active =  self.enemylist[self.enemylist_data_index].enemy

def selectPlayer(self, context):
    bpy.ops.object.select_all(action='DESELECT')
    if self.playerlist_data_index != -1:
        for pl in self.playerlist:
            pl.player.select_set(False)
        self.playerlist[self.playerlist_data_index].player.select_set(True)
        bpy.context.view_layer.objects.active =  self.playerlist[self.playerlist_data_index].player

def selectMap(self, context):
    if self.maplist_data_index != -1:
        for item in self.maplist:
            item.map.hide_viewport = True
        self.maplist[self.maplist_data_index].map.hide_viewport = False
        context.scene.grease_pencil = self.maplist[self.maplist_data_index].annotation

def selectFloor(self, context):
    dm_property = context.scene.dm_property

    if self.floorlist_data_index != -1:
        for item in self.floorlist:
            item.floor.hide_viewport = True
        self.floorlist[self.floorlist_data_index].floor.hide_viewport = False
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
