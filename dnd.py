
import bpy
from bl_ui.properties_grease_pencil_common import (
    AnnotationDataPanel,
    AnnotationOnionSkin,
    GreasePencilMaterialsPanel,
    GreasePencilVertexcolorPanel,
)

from bpy_extras.io_utils import ImportHelper

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

    if(bpy.data.node_groups.get("DND_Extruder") is not None):
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
    dm_property.maps_coll = collection

    for map in dm_property.maplist:
            map.floorlist.clear()
    dm_property.maplist.clear()

    for map in collection.children:
        map_pointer = dm_property.maplist.add()
        map_pointer.map = map
        map_pointer.name = map.name
        for floor in map.children:
            floor_pointer = map_pointer.floorlist.add()
            floor_pointer.floor = floor
            floor_pointer.name = floor.name
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

def selectFloor(self, context):
    if self.floorlist_data_index != -1:
        for item in self.floorlist:
            item.floor.hide_viewport = True
        self.floorlist[self.floorlist_data_index].floor.hide_viewport = False
        context.active_annotation_layer = self.floorlist[self.floorlist_data_index].annotation

def addToCollection(self,context, collectionName, obj):
    for coll in obj.users_collection:
            # Unlink the object
            coll.objects.unlink(obj)

    if(bpy.data.collections.get(collectionName) is None):
        collection = bpy.data.collections.new(collectionName)
        bpy.context.scene.collection.children.link(collection)
    else:
        collection = bpy.data.collections.get(collectionName)
    collection.objects.link(obj)

#endregion Methods     

class FloorPointerProperties(bpy.types.PropertyGroup):
    floor : bpy.props.PointerProperty(type=bpy.types.Collection)

class MapPointerProperties(bpy.types.PropertyGroup):
    map : bpy.props.PointerProperty(type=bpy.types.Collection)
    floorlist_data_index : bpy.props.IntProperty(
        update=selectFloor
    )
    floorlist : bpy.props.CollectionProperty(type = FloorPointerProperties)
    annotation : bpy.props.PointerProperty(type=bpy.types.GreasePencil)


#region Properties
class PlayerPointerProperties(bpy.types.PropertyGroup):
    player : bpy.props.PointerProperty(type=bpy.types.Object)

class PlayerProperties(bpy.types.PropertyGroup):


    def update_player_color(self, context):
        if self.player_material != None:
            #print(self.player_material.node_tree.nodes.get('RGB'))
            rgb_node = self.player_material.node_tree.nodes.get('RGB')
            rgb_node.outputs[0].default_value = self.player_color
    def update_move_distance(self,context):
        unitinfo = GetCurrentUnits()
        unit_dist = self.move_distance*2
        distance = unit_to_bu(unit_dist,unitinfo[1])
        self.distance_circle.dimensions = (distance,distance,self.distance_circle.dimensions.z)


    move_distance : bpy.props.FloatProperty(
        #name = "MOVE_DISTANCE",
        description = "Distance in Meter the Player can move in one Turn",
        default = 9,
        min = 1,
        max = 100,
        update=update_move_distance
    )
    distance_circle : bpy.props.PointerProperty(type=bpy.types.Object)
    torch : bpy.props.PointerProperty(type=bpy.types.Object)
    spot_dark : bpy.props.PointerProperty(type=bpy.types.SpotLight)
    player_material : bpy.props.PointerProperty(type=bpy.types.Material)
    #name : bpy.props.StringProperty()
    player_color: bpy.props.FloatVectorProperty(
        name="player_color",
        description="Player color in RGBA.",
        size=4,
        subtype="COLOR",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        update=update_player_color,  # some sort of connected update method?
    )
    player : bpy.props.PointerProperty(type=bpy.types.Object)

class EnemyPointerProperties(bpy.types.PropertyGroup):
    enemy : bpy.props.PointerProperty(type=bpy.types.Object)

class EnemyProperties(bpy.types.PropertyGroup):

    def update_enemy_color(self, context):
        if self.enemy_material != None:
            #print(self.player_material.node_tree.nodes.get('RGB'))
            rgb_node = self.enemy_material.node_tree.nodes.get('RGB')
            rgb_node.outputs[0].default_value = self.enemy_color
    def update_move_distance(self,context):
        unitinfo = GetCurrentUnits()
        unit_dist = self.move_distance*2
        distance = unit_to_bu(unit_dist,unitinfo[1])
        self.distance_circle.dimensions = (distance,distance,self.distance_circle.dimensions.z)


    move_distance : bpy.props.FloatProperty(
        #name = "MOVE_DISTANCE",
        description = "Distance in Meter the Player can move in one Turn",
        default = 9,
        min = 1,
        max = 100,
        update=update_move_distance
    )
    distance_circle : bpy.props.PointerProperty(type=bpy.types.Object)
    enemy_material : bpy.props.PointerProperty(type=bpy.types.Material)
    #name : bpy.props.StringProperty()
    enemy_color: bpy.props.FloatVectorProperty(
        name="Enemy_color",
        description="Enemy color in RGBA.",
        size=4,
        subtype="COLOR",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        update=update_enemy_color,  # some sort of connected update method?
    )
    health_points : bpy.props.IntProperty(
        name="Enemy_health_points",
        description="Enemy color in RGBA.",
        default= 20,
        min=0,
        )
    enemy : bpy.props.PointerProperty(type=bpy.types.Object)

class DMProperties(bpy.types.PropertyGroup):

    playerlist_data_index : bpy.props.IntProperty(
        update=selectPlayer
    )
    playerlist : bpy.props.CollectionProperty(type = PlayerPointerProperties)

    enemylist_data_index : bpy.props.IntProperty(
        update=selectEnemy
    )
    enemylist : bpy.props.CollectionProperty(type = EnemyPointerProperties)

    maplist_data_index : bpy.props.IntProperty(
        update=selectMap
    )
    maplist : bpy.props.CollectionProperty(type = MapPointerProperties)
   
    camera :  bpy.props.PointerProperty(type=bpy.types.Object)
    camera_pan_toggle : bpy.props.BoolProperty()
    global_Sun : bpy.props.PointerProperty(type=bpy.types.SunLight)
    
    cave_Mat : bpy.props.PointerProperty(type= bpy.types.Material)

    master_coll : bpy.props.PointerProperty(type= bpy.types.Collection)
    maps_coll : bpy.props.PointerProperty(type= bpy.types.Collection)
#endregion Properties

#region UI
class _PT_SceneSetupPanel(bpy.types.Panel):
    bl_label = "Scene"
    bl_idname = "_PT_SceneSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        
        col = layout.column()
       
        col.operator("scene.setup", icon ="WORLD")
        col.prop(context.scene.unit_settings, 'system')
        col.operator("scene.grid_scale")
        col.prop(context.scene.tool_settings, "use_snap")

class _PT_CameraSetupPanel(bpy.types.Panel):
    bl_label = "Camera"
    bl_idname = "_PT_CameraSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        
        col = layout.column()

        if(dm_property.camera is None):
            col.operator("camera.dnd_add", icon ='OUTLINER_DATA_CAMERA')
        else:
            col.operator("camera.dnd_remove", icon ='PANEL_CLOSE')
            if dm_property.camera.data.ortho_scale < 40.0:
                col.operator("camera.dnd_zoom", icon ='ZOOM_OUT').scale = 80.0
            else:
                col.operator("camera.dnd_zoom", icon ='ZOOM_IN').scale = 35.0

            pan_row = col.row()
            pan_row.operator("camera.dnd_pan", icon="VIEW_PAN",text ="Panning")
            if dm_property.camera_pan_toggle:
                pan_row.label(text="Active")
            else:
                pan_row.label(text="Not Active")
            col.operator("view3d.view_camera",icon='OUTLINER_DATA_CAMERA')
     
class _PT_LightSetupPanel(bpy.types.Panel):
    bl_label = "Light"
    bl_idname = "_PT_LightSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        
        col = layout.column()
        if dm_property.global_Sun != None:
            col.prop(dm_property.global_Sun, 'diffuse_factor',text = "Sun Light")

class _PT_PlayerListPanel(bpy.types.Panel):
    """Creates a Panel for all Player Settings"""
    bl_label = "Player"
    bl_idname = "PT_ui_player_list"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout

        dm_property = context.scene.dm_property
        
        list_row_layout = layout.row()
        list_row_layout.template_list("_UL_Playerlist_player", "", dm_property, "playerlist", dm_property, "playerlist_data_index")
        menu_sort_layout_column = list_row_layout.column()
        menu_sort_layout = menu_sort_layout_column.column(align=True)
        menu_sort_layout.operator("player.update", text="", icon="FILE_REFRESH")
        menu_sort_layout.operator("player.dnd_add", text="", icon="ADD")
        #menu_sort_layout.operator("list.list_o", text="", icon="ADD").menu_active = 6
        menu_sort_layout.operator("list.list_op", text="", icon="REMOVE").menu_active = 7
        menu_sort_layout2 = menu_sort_layout_column.column(align=True)
        menu_sort_layout.separator(factor=3.0)
        menu_sort_layout2.operator("list.list_op", text="", icon="TRIA_UP").menu_active = 4
        menu_sort_layout2.operator("list.list_op", text="", icon="TRIA_DOWN").menu_active = 5


        col = layout.column()
        row = layout.row()

        i = 0
        for pl in dm_property.playerlist:
            if bpy.context.object == pl.player:
                player_property = pl.player.player_property
                layout.prop(player_property, "name")
                layout.prop(player_property.spot_dark, "cutoff_distance", text="Darkvision")
                list_row = layout.row()
                if player_property.distance_circle.hide_get():
                    list_row.operator("player.distance_toggle", text="", icon="HIDE_ON")
                    list_row.label(text="Distance Measure")
                else:
                    list_row.operator("player.distance_toggle",text ="",  icon="HIDE_OFF")
                    list_row.label(text="Distance Measure")
                    list_row.prop(player_property, "move_distance", text="")
                    list_row.label(text=GetCurrentUnits()[0])

                list1_row = layout.row()
                if player_property.torch.hide_get():
                    list1_row.operator("player.torch", text="", icon="HIDE_ON")
                    list1_row.label(text="Use Torch")
                else:
                    list1_row.operator("player.torch", text="", icon="HIDE_OFF")
                    list1_row.label(text="Use Torch")
                    list1_row.prop(player_property.torch.data, "cutoff_distance", text="")
                
                layout.prop(player_property, "player_color")
                break

class _UL_Playerlist_player(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item.player.player_property
        ma = slot.name
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ma:
                layout.prop(slot, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class PLAYER_List_Button(bpy.types.Operator):
    bl_idname = "list.list_op"
    bl_label = "Action List Operator"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    menu_active: bpy.props.IntProperty(name="Button Index")

    def execute(self, context):
        dm_property = context.scene.dm_property

        list = dm_property.playerlist
        index = dm_property.playerlist_data_index


  
        if self.menu_active == 1:
            print("Select")
            pass
			
        if self.menu_active == 2:
            anim_entry = list[index]
            #anim_entry = dm_property.playerlist
            anim_entry.width = anim_entry.width + 1

        if self.menu_active == 3:
            list.clear()

		# Move entry up
        if self.menu_active == 4:
            if index > 0:
                list.move(index, index-1)
                index -= 1

		# Move entry down
        if self.menu_active == 5:
            if index < len(list)-1:
                list.move(index, index+1)
                index += 1
        
        # Add entry
        if self.menu_active == 6:
            item = index.add()
            if len(bpy.data.actions) > 0:
                item.action = bpy.data.actions[0]
            if index < len(list)-1:
                list.move(len(list)-1, index+1)
                index += 1


		# Remove Item
        if self.menu_active == 7:
            if index >= 0 and index < len(list):
                player = list[index].player
                player.player_property.distance_circle.parent = player
                delete_hierarchy(player)
                list.remove(index)
                index = min(index, len(list)-1)
        return {"FINISHED"}      

class _PT_EnemyListPanel(bpy.types.Panel):
    """Creates a Panel for all Player Settings"""
    bl_label = "Enemies"
    bl_idname = "PT_ui_Enemy_list"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout

        dm_property = context.scene.dm_property
        
        list_row_layout = layout.row()
        list_row_layout.template_list("_UL_Enemylist", "", dm_property, "enemylist", dm_property, "enemylist_data_index")
        menu_sort_layout_column = list_row_layout.column()
        menu_sort_layout = menu_sort_layout_column.column(align=True)
        menu_sort_layout.operator("enemy.dnd_add", text="", icon="ADD")
        #menu_sort_layout.operator("list.list_o", text="", icon="ADD").menu_active = 6
        menu_sort_layout.operator("list.enemylist_op", text="", icon="REMOVE").menu_active = 7
        menu_sort_layout2 = menu_sort_layout_column.column(align=True)
        menu_sort_layout.separator(factor=3.0)
        menu_sort_layout2.operator("list.enemylist_op", text="", icon="TRIA_UP").menu_active = 4
        menu_sort_layout2.operator("list.enemylist_op", text="", icon="TRIA_DOWN").menu_active = 5


        col = layout.column()
        row = layout.row()

        i = 0
        for en in dm_property.enemylist:
            if bpy.context.object == en.enemy:
                enemy_property = en.enemy.enemy_property
                layout.prop(enemy_property, "name")
                list_row = layout.row()
                if enemy_property.distance_circle.hide_get():
                    list_row.operator("enemy.distance_toggle", text="", icon="HIDE_ON")
                    list_row.label(text="Distance Measure")
                else:
                    list_row.operator("enemy.distance_toggle",text ="",  icon="HIDE_OFF")
                    list_row.label(text="Distance Measure")
                    list_row.prop(enemy_property, "move_distance", text="")
                    list_row.label(text=GetCurrentUnits()[0])
                    
               
                layout.prop(enemy_property, "enemy_color")
                layout.prop(enemy_property,"health_points")
                break

class _UL_Enemylist(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item.enemy.enemy_property
        ma = slot.name
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ma:
                layout.prop(slot, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class Enemy_List_Button(bpy.types.Operator):
    bl_idname = "list.enemylist_op"
    bl_label = "Action List Operator"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    menu_active: bpy.props.IntProperty(name="Button Index")

    def execute(self, context):
        if self.menu_active == 1:
            print("Select")
            pass
			
        if self.menu_active == 2:
            anim_entry = context.scene.dm_property.enemylist[context.scene.dm_property.enemylist_data_index]
            #anim_entry = context.scene.dm_property.playerlist
            anim_entry.width = anim_entry.width + 1

        if self.menu_active == 3:
            context.scene.dm_property.enemylist.clear()

		# Move entry up
        if self.menu_active == 4:
            if context.scene.dm_property.enemylist_data_index > 0:
                context.scene.dm_property.enemylist.move(context.scene.dm_property.enemylist_data_index, context.scene.dm_property.enemylist_data_index-1)
                context.scene.dm_property.enemylist_data_index -= 1

		# Move entry down
        if self.menu_active == 5:
            if context.scene.dm_property.enemylist_data_index < len(context.scene.dm_property.enemylist)-1:
                context.scene.dm_property.enemylist.move(context.scene.dm_property.enemylist_data_index, context.scene.dm_property.enemylist_data_index+1)
                context.scene.dm_property.enemylist_data_index += 1
        
        # Add entry
        if self.menu_active == 6:
            item = context.scene.dm_property.enemylist.add()
            if len(bpy.data.actions) > 0:
                item.action = bpy.data.actions[0]
            if context.scene.dm_property.enemylist_data_index < len(context.scene.dm_property.enemylist)-1:
                context.scene.dm_property.enemylist.move(len(context.scene.dm_property.enemylist)-1, context.scene.dm_property.enemylist_data_index+1)
                context.scene.dm_property.enemylist_data_index += 1

		# Remove Item
        if self.menu_active == 7:
            if context.scene.dm_property.enemylist_data_index >= 0 and context.scene.dm_property.enemylist_data_index < len(context.scene.dm_property.enemylist):
                enemy = context.scene.dm_property.enemylist[context.scene.dm_property.enemylist_data_index].enemy
                enemy.enemy_property.distance_circle.parent = enemy
                delete_hierarchy(enemy)
                context.scene.dm_property.enemylist.remove(context.scene.dm_property.enemylist_data_index)
                context.scene.dm_property.enemylist_data_index = min(context.scene.dm_property.enemylist_data_index, len(context.scene.dm_property.enemylist)-1)
        return {"FINISHED"}      

class _PT_AddSetupPanel(bpy.types.Panel):
    bl_label = "Map"
    bl_idname = "_PT_MapSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property


        row = layout.row()
        
        col = row.column()
        gpd_owner = context.annotation_data_owner  
        gpd = context.annotation_data
        #col.template_ID(gpd_owner, "grease_pencil", new="gpencil.annotation_add", unlink="gpencil.data_unlink")

        col.label(text="Maps")

        list_row_layout = col.row()
        list_row_layout.template_list("_UL_Maplist", "", dm_property, "maplist", dm_property, "maplist_data_index")
        menu_sort_layout_column = list_row_layout.column()
        menu_sort_layout = menu_sort_layout_column.column(align=True)
        menu_sort_layout.operator("map.update", text="", icon="FILE_REFRESH")
        menu_sort_layout.operator("map.add", text="", icon="ADD")
        #menu_sort_layout.operator("list.list_o", text="", icon="ADD").menu_active = 6
        menu_sort_layout.operator("list.map_op", text="", icon="REMOVE").menu_active = 7
        menu_sort_layout2 = menu_sort_layout_column.column(align=True)
        menu_sort_layout.separator(factor=3.0)
        menu_sort_layout2.operator("list.map_op", text="", icon="TRIA_UP").menu_active = 4
        menu_sort_layout2.operator("list.map_op", text="", icon="TRIA_DOWN").menu_active = 5

        if(dm_property.maplist_data_index >= 0):
            map = dm_property.maplist[dm_property.maplist_data_index]

            col = row.column()
            col.label(text="Floors")
            list_row_layout = col.row()
            list_row_layout.template_list("_UL_Floorlist", "", map, "floorlist", map, "floorlist_data_index")
            menu_sort_layout_column = list_row_layout.column()
            menu_sort_layout = menu_sort_layout_column.column(align=True)
            menu_sort_layout.operator("floor.add", text="", icon="ADD")
            #menu_sort_layout.operator("list.list_o", text="", icon="ADD").menu_active = 6
            menu_sort_layout.operator("list.floor_op", text="", icon="REMOVE").menu_active = 7
            menu_sort_layout2 = menu_sort_layout_column.column(align=True)
            menu_sort_layout.separator(factor=3.0)
            menu_sort_layout2.operator("list.floor_op", text="", icon="TRIA_UP").menu_active = 4
            menu_sort_layout2.operator("list.floor_op", text="", icon="TRIA_DOWN").menu_active = 5


            if(len(map.floorlist) > 0):
                col = layout.column()
                col.label(text="Add Map")
                col.operator(ImportMapImage.bl_idname, icon="IMAGE_DATA")
                col.operator("mesh.map_scale", icon="SETTINGS")    


                col.label(text="Add Geometry")
                col.operator("mesh.wall_add", icon="MOD_BUILD")
                col.operator("mesh.cave_add") 
                col.operator("mesh.pillar_add",icon="MESH_CYLINDER") 
                col.label(text="Add Light")
                col.operator("light.torch_add",icon="LIGHT_POINT")
        


class _UL_Maplist(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item
        ma = slot.name
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ma:
                layout.prop(slot, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class _UL_Floorlist(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item
        ma = slot.name
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ma:
                layout.prop(slot, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class Map_List_Button(bpy.types.Operator):
    bl_idname = "list.map_op"
    bl_label = "Action List Operator"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    menu_active: bpy.props.IntProperty(name="Button Index")

    def execute(self, context):
        dm_property = context.scene.dm_property

        list = dm_property.maplist
        index = dm_property.maplist_data_index

        
        if self.menu_active == 1:
            print("Select")
            pass
			
        if self.menu_active == 2:
            anim_entry = list[index]
            #anim_entry = dm_property.playerlist
            anim_entry.width = anim_entry.width + 1

        if self.menu_active == 3:
            list.clear()

		# Move entry up
        if self.menu_active == 4:
            if index > 0:
                list.move(index, index-1)
                index -= 1

		# Move entry down
        if self.menu_active == 5:
            if index < len(list)-1:
                list.move(index, index+1)
                index += 1
        
        # Add entry
        if self.menu_active == 6:
            item = index.add()
            if len(bpy.data.actions) > 0:
                item.action = bpy.data.actions[0]
            if index < len(list)-1:
                list.move(len(list)-1, index+1)
                index += 1

		# Remove Item
        if self.menu_active == 7:
            if index >= 0 and index < len(list):
                collection = list[index].map
                for coll in collection.children:
                    collection.children.unlink(coll)
                dm_property.maps_coll.children.unlink(collection)
                list.remove(index)
                index = min(index, len(list)-1)
        return {"FINISHED"}      

class Floor_List_Button(bpy.types.Operator):
    bl_idname = "list.floor_op"
    bl_label = "Action List Operator"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    menu_active: bpy.props.IntProperty(name="Button Index")

    def execute(self, context):
        dm_property = context.scene.dm_property
        map = dm_property.maplist[dm_property.maplist_data_index]
        list = map.floorlist
        index = map.floorlist_data_index

        
        if self.menu_active == 1:
            print("Select")
            pass
			
        if self.menu_active == 2:
            anim_entry = list[index]
            #anim_entry = dm_property.playerlist
            anim_entry.width = anim_entry.width + 1

        if self.menu_active == 3:
            list.clear()

		# Move entry up
        if self.menu_active == 4:
            if index > 0:
                list.move(index, index-1)
                index -= 1

		# Move entry down
        if self.menu_active == 5:
            if index < len(list)-1:
                list.move(index, index+1)
                index += 1
        
        # Add entry
        if self.menu_active == 6:
            item = index.add()
            if len(bpy.data.actions) > 0:
                item.action = bpy.data.actions[0]
            if index < len(list)-1:
                list.move(len(list)-1, index+1)
                index += 1

		# Remove Item
        if self.menu_active == 7:
            if index >= 0 and index < len(list):
                collection = list[index].floor
                for obj in collection.all_objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
                dm_property.maplist[dm_property.maplist_data_index].map.children.unlink(collection)
                list.remove(index)
                index = min(index, len(list)-1)
        return {"FINISHED"}      


class _PT_WindowSetupPanel(bpy.types.Panel):
    bl_label = "Window"
    bl_idname = "_PT_WindowSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        
        col = layout.column()

        col.operator("window.dnd_new", icon ='WINDOW')
        col.operator("wm.window_fullscreen_toggle",icon ="FULLSCREEN_ENTER")


#region Operatior
class PLAYER_Distance_Button(bpy.types.Operator):
    bl_idname = "player.distance_toggle"
    bl_label = "Toggle Visibility of Distance Circle"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.object.player_property.distance_circle.hide_get():
            context.object.player_property.distance_circle.parent = None
            context.object.player_property.distance_circle.hide_set(False)
        else:
            context.object.player_property.distance_circle.parent = context.object
            context.object.player_property.distance_circle.hide_set(True)
        loc = context.object.location
        loc.z = context.object.player_property.distance_circle.location.z
        context.object.player_property.distance_circle.location = loc
        return {"FINISHED"} 

class PLAYER_Torch_Button(bpy.types.Operator):
    bl_idname = "player.torch"
    bl_label = "Toggle Visibility of Torch Light"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.object.player_property.torch.hide_get():
            context.object.player_property.torch.hide_set(False)
        else:
            context.object.player_property.torch.hide_set(True)
        return {"FINISHED"} 

class PLAYER_add(bpy.types.Operator):
    "Add Player Mesh and Lights to the Scene"
    bl_idname = "player.dnd_add"
    bl_label = "Add Player"
    
    def update_tmp_darkvision(self, context):
        unitinfo = GetCurrentUnits()
        unit_dist = self.tmp_darkvision
        self.tmp_darkvision = unit_to_bu(unit_dist,unitinfo[1])
    def update_tmp_move_distance(self, context):
        unitinfo = GetCurrentUnits()
        unit_dist = self.tmp_move_distance
        self.tmp_move_distance = unit_to_bu(unit_dist,unitinfo[1])

    tmp_name : bpy.props.StringProperty(name ="Enter Name", default= "player")
    tmp_darkvision : bpy.props.FloatProperty(name = "See in Dark", default= 0,update=update_tmp_move_distance)
    tmp_move_distance : bpy.props.FloatProperty(name = "Move in Turn", default= 9,update=update_tmp_move_distance)
    tmp_player_color: bpy.props.FloatVectorProperty(
        name="player_color",
        description="Default cell color in RGBA. Can be overwritten by creating your own material named 'custom_default_material'",
        size=4,
        subtype="COLOR",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        #update=update_player_color,  # some sort of connected update method?
    )

    def invoke(self, context, event):
                
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        dm_prop = bpy.context.scene.dm_property
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=2, enter_editmode=False, align='WORLD', location=(0, 0, 0.0), scale=(1, 1, 1))
        player = bpy.context.object
        list = []
        list.append(player)


        player.name = self.tmp_name
        player_property = player.player_property
        player.data.vertices[0].co.y += 0.3
        player.data.vertices[1].co.y += 0.3

        player_pointer = dm_prop.playerlist.add()
        player_property.name = self.tmp_name
        player_property.move_distance = self.tmp_move_distance
        player_property.player_color = self.tmp_player_color
        player_pointer.player = player

        player_property.player_material = CreatePlayerMaterial(self, context, self.tmp_player_color)
        player.data.materials.append(player_property.player_material)
        player.lock_location = (False, False, True)
        player.lock_rotation = (True, True, False)
        
        bpy.ops.mesh.primitive_cylinder_add(radius= 1, depth=2, enter_editmode=False, align='WORLD', location=(0, 0, 1), scale=(1, 1, 1))
        distance_circel = bpy.context.object
        distance_circel.name = "Distance Circle"
        distance_circel.parent = player
        distance_circel.lock_location = (False, False, True)

        player_property.distance_circle = distance_circel
        player_property.move_distance = player_property.move_distance
        distance_circel.data.materials.append(CreateDistanceMaterial(self, context, (0,1,0,0.2)))
        list.append(distance_circel)


        bpy.ops.object.light_add(type='SPOT', align='WORLD', location=(0, 0, 0), rotation=(1.5708, 0, 0), scale=(1, 1, 1))
        spot = bpy.context.object
        spot.name = "Player Vision Day"
        spot.parent = player
        spot.data.spot_size = 1.74
        spot.data.shadow_soft_size = 100
        spot.data.energy = 500000
        spot.data.spot_blend = 1
        spot.data.color = (1, 0, 0)
        list.append(spot)

        bpy.ops.object.light_add(type='SPOT', align='WORLD', location=(0, 0, 0), rotation=(1.5708, 0, 0), scale=(1, 1, 1))
        spotDark = bpy.context.object
        spotDark.name = "Player Vision Dark"
        spotDark.parent = player
        spotDark.data.spot_size = 1.74
        spotDark.data.shadow_soft_size = 100
        spotDark.data.energy = 500000
        spotDark.data.color = (0, 0, 1)
        spotDark.data.spot_blend = 1
        spotDark.data.use_shadow = False
        spotDark.data.use_custom_distance = True
        spotDark.data.cutoff_distance = self.tmp_darkvision
        list.append(spotDark)
        
        
        bpy.ops.object.light_add(type='POINT', align='WORLD', location=(0, 0, 5), rotation=(0, 0, 0), scale=(1, 1, 1))
        torch = bpy.context.object
        torch.name = "Torch"
        torch.parent = player
        torch.data.energy = 10000
        torch.data.shadow_soft_size = 9.144
        torch.data.color = (0, 0, 1)
        torch.data.use_shadow = False
        torch.data.use_custom_distance = True
        torch.data.cutoff_distance = 18.288
        player_property.torch = torch
        list.append(torch)

        for obj in list:
            addToCollection(self, context, "Player", obj)

        spot.hide_select = True
        torch.hide_set(True)
        torch.hide_select = True
        spotDark.hide_select = True
        player_property.spot_dark = spotDark.data
        distance_circel.hide_select = True
        distance_circel.hide_set(True)
        bpy.context.view_layer.objects.active = player
        player.select_set(True)
        return {'FINISHED'}
class PLAYER_update(bpy.types.Operator):
    "Add Map Collection to the Scene"
    bl_idname = "player.update"
    bl_label = "Update players"
    
    def execute(self, context):
        dm_property = context.scene.dm_property
        if(bpy.data.collections.get("Player") is None):
            collection = bpy.data.collections.new("Player")
            bpy.context.scene.collection.children.link(collection)
        else:
            collection = bpy.data.collections.get("Player")
            update_players(self,context,collection)
        return {'FINISHED'}

class ENEMY_add(bpy.types.Operator):
    "Add Player Mesh and Lights to the Scene"
    bl_idname = "enemy.dnd_add"
    bl_label = "Add Enemy"
    
    def update_tmp_move_distance(self, context):
        unitinfo = GetCurrentUnits()
        unit_dist = self.tmp_move_distance
        self.tmp_move_distance = unit_to_bu(unit_dist,unitinfo[1])

    tmp_name : bpy.props.StringProperty(name ="Enter Name", default= "enemy")
    tmp_move_distance : bpy.props.FloatProperty(name = "Move in Turn", default= 9,update=update_tmp_move_distance)
    tmp_enemy_color: bpy.props.FloatVectorProperty(
        name="player_color",
        description="Default cell color in RGBA. Can be overwritten by creating your own material named 'custom_default_material'",
        size=4,
        subtype="COLOR",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        #update=update_player_color,  # some sort of connected update method?
    )

    def invoke(self, context, event):
                
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        dm_prop = bpy.context.scene.dm_property
        bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=2, enter_editmode=False, align='WORLD', location=(0, 0, 0.0), scale=(1, 1, 1))
        enemy = bpy.context.object
        list = []
        list.append(enemy)

        enemy.name = self.tmp_name
        enemy_propery = enemy.enemy_property
        enemy.data.vertices[0].co.y += 0.3
        enemy.data.vertices[1].co.y += 0.3

        enemy_pointer = dm_prop.enemylist.add()
        enemy_propery.name = self.tmp_name
        enemy_propery.move_distance = self.tmp_move_distance
        enemy_propery.enemy_color = self.tmp_enemy_color
        enemy_pointer.enemy = enemy

        enemy_propery.enemy_material = CreatePlayerMaterial(self, context, self.tmp_enemy_color)

        enemy.data.materials.append(enemy_propery.enemy_material)
        enemy.lock_location = (False, False, True)
        enemy.lock_rotation = (True, True, False)
        
        bpy.ops.mesh.primitive_cylinder_add(radius= 1, depth=2, enter_editmode=False, align='WORLD', location=(0, 0, 1), scale=(1, 1, 1))
        distance_circel = bpy.context.object
        distance_circel.name = "Distance Circle"
        distance_circel.parent = enemy
        distance_circel.lock_location = (False, False, True)
        enemy_propery.distance_circle = distance_circel
        enemy_propery.move_distance = enemy_propery.move_distance
       
        distance_circel.data.materials.append(CreateDistanceMaterial(self, context, (0,1,0,0.2)))
        list.append(distance_circel)

        for obj in list:
            addToCollection(self, context, "Enemy", obj)
        
        distance_circel.hide_set(True)
        distance_circel.hide_select = True
        bpy.context.view_layer.objects.active = enemy
        enemy.select_set(True)

        return {'FINISHED'}

class ENEMY_Distance_Button(bpy.types.Operator):
    bl_idname = "enemy.distance_toggle"
    bl_label = "Toggle Visibility of Distance Circle"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.object.enemy_property.distance_circle.hide_get():
            context.object.enemy_property.distance_circle.parent = None
            context.object.enemy_property.distance_circle.hide_set(False)
        else:
            context.object.enemy_property.distance_circle.parent = context.object
            context.object.enemy_property.distance_circle.hide_set(True)
        loc = context.object.location
        loc.z = context.object.enemy_property.distance_circle.location.z
        context.object.enemy_property.distance_circle.location = loc
        return {"FINISHED"} 

class MAP_add(bpy.types.Operator):
    "Add Map Collection to the Scene"
    bl_idname = "map.add"
    bl_label = "Add Map"
    
    tmp_name : bpy.props.StringProperty(name ="Enter Name", default= "map")
    def invoke(self, context, event):
                
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        bpy.ops.gpencil.annotation_add()
        gpd = context.annotation_data
        
        dm_prop = bpy.context.scene.dm_property
        collection = check_if_collection_exists(self.tmp_name)
        gpd.name = collection.name
        for coll in dm_prop.maps_coll.children:
            if(coll is collection):
                return {'CANCELLED'}
        dm_prop.maps_coll.children.link(collection)
        collection_pointer = dm_prop.maplist.add()
        collection_pointer.annotation = gpd
        collection_pointer.map = collection
        collection_pointer.name = collection.name
        
        return {'FINISHED'}
class MAP_update(bpy.types.Operator):
    "Add Map Collection to the Scene"
    bl_idname = "map.update"
    bl_label = "Update Maps"
    
    def execute(self, context):
        dm_property = context.scene.dm_property
        if(bpy.data.collections.get("Maps") is None):
            collection = bpy.data.collections.new("Maps")
            bpy.context.scene.collection.children.link(collection)
            dm_property.maps_coll = collection
        else:
            collection = bpy.data.collections.get("Maps")
            update_maps(self,context,collection)
        return {'FINISHED'}

class FLOOR_add(bpy.types.Operator):
    "Add Map Collection to the Scene"
    bl_idname = "floor.add"
    bl_label = "Add Map"
    
    tmp_name : bpy.props.StringProperty(name ="Enter Name", default= "floor")


    def invoke(self, context, event):
                
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        dm_property = bpy.context.scene.dm_property
        map = dm_property.maplist[dm_property.maplist_data_index]

        collection = check_if_collection_exists(self.tmp_name)

        for maps in dm_property.maplist:
            for coll in maps.map.children:
                if(coll is collection):
                    return {'CANCELLED'}
        dm_property.maplist[dm_property.maplist_data_index].map.children.link(collection)
        collection_pointer = map.floorlist.add()
        collection_pointer.floor = collection
        collection_pointer.name = collection.name

        bpy.ops.gpencil.layer_annotation_add()

        gpl = context.active_annotation_layer
        print("TEST",gpl)
        collection_pointer.annotation = gpl
        
        return {'FINISHED'}
class SCENE_Grid_Setup(bpy.types.Operator):
    """SetupGridScene"""
    bl_idname = "scene.grid_scale"
    bl_label = "Set Grid Scale"

    def execute(self, context):
        unitsinfo = GetCurrentUnits()
        scale = bu_to_unit(1.524, unitsinfo[1])
        
        AREA = 'VIEW_3D'

        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if not area.type == AREA:
                    continue

                for s in area.spaces:
                    if s.type == AREA:
                        s.overlay.grid_scale = scale
                        break
        return {'FINISHED'}

class SCENE_Setup(bpy.types.Operator):
    """SetupScene"""
    bl_idname = "scene.setup"
    bl_label = "Setup Scene"

    def execute(self, context):

        dm_property = context.scene.dm_property
        #bpy.ops.object.select_all(action='SELECT')
        #bpy.ops.object.delete(use_global=False)
        if(bpy.data.collections.get("Collection") is not None):
            collection = bpy.data.collections.get("Collection")
            bpy.context.scene.collection.children.unlink(collection)

        if(bpy.data.collections.get("Camera") is None):
            collection = bpy.data.collections.new("Camera")
            bpy.context.scene.collection.children.link(collection)

        if(bpy.data.collections.get("Maps") is None):
            collection = bpy.data.collections.new("Maps")
            bpy.context.scene.collection.children.link(collection)
            dm_property.maps_coll = collection
        else:
            collection = bpy.data.collections.get("Maps")
            update_maps(self,context,collection)


        bpy.context.scene.eevee.use_taa_reprojection = False
        bpy.context.scene.eevee.taa_samples = 1
        bpy.context.scene.eevee.sss_samples = 1

        bpy.context.scene.eevee.use_soft_shadows = False
        bpy.context.scene.eevee.shadow_cube_size = '1024'
        bpy.context.scene.eevee.shadow_cascade_size = '1024'
        bpy.context.scene.eevee.use_shadow_high_bitdepth = True
        bpy.context.scene.eevee.use_bloom = True

        bpy.context.space_data.shading.type = 'MATERIAL'


        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
        return {'FINISHED'}

class CAMERA_add(bpy.types.Operator):
    """Add Camera, a Darkness Plane and Light to the Scene"""
    bl_idname = "camera.dnd_add"
    bl_label = "Add Camera"
    
    def execute(self, context):
        dm_property = context.scene.dm_property
        bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=(0, 0, 10), rotation=(0, 0, 0), scale=(1, 1, 1))
        camera = bpy.context.object
        camera.name = "DnD Camera"
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = 35.0
        camera.lock_location = (False, False, True)
        camera.lock_rotation = (True, True, True)
        camera.data.passepartout_alpha = 1
        dm_property.camera = camera

        
        bpy.ops.mesh.primitive_plane_add(size=80, enter_editmode=False, align='WORLD', location=(0, 0, -9.5), scale=(1, 1, 1))
        planeDarkness = bpy.context.object
        planeDarkness.name = "Darkness Plane"
        planeDarkness.parent = camera
        
        planeDarkness.data.materials.append(CreateDarknessMaterial(self,context))
        planeDarkness.hide_select = True
        
        bpy.ops.object.light_add(type='SUN', align='WORLD', location=(0, 0, 10), scale=(1, 1, 1))
        sun = bpy.context.object
        sun.name = "DND SUN"
        sun.data.energy = 10
        sun.data.color = (0, 0, 1)
        sun.hide_select = True
        sun.parent = camera

        context.scene.dm_property.global_Sun = sun.data
        addToCollection(self, context, "Camera",camera)
        addToCollection(self, context, "Camera",planeDarkness)
        addToCollection(self, context, "Camera",sun)
        return {'FINISHED'}

class CAMERA_remove(bpy.types.Operator):
    """Add Camera, a Darkness Plane and Light to the Scene"""
    bl_idname = "camera.dnd_remove"
    bl_label = "Remove Camera"
    
    def execute(self, context):
        dm_property = context.scene.dm_property
        camera = dm_property.camera
        dm_property.camera = None
        delete_hierarchy(camera)
        return{'FINISHED'}
class CAMERA_zoom(bpy.types.Operator):
    """Toggle Camera Orthographic Scale between 80 and 35"""
    bl_idname = "camera.dnd_zoom"
    bl_label = "Toggle Camera Zoom"
    
    scale : bpy.props.FloatProperty(min=10, max = 1000)

    def execute(self, context):
        dm_property = context.scene.dm_property
        camera = dm_property.camera
        
        camera.data.ortho_scale = self.scale

        return {'FINISHED'}

class CAMERA_panning(bpy.types.Operator):
    """Add Camera, a Darkness Plane and Light to the Scene"""
    bl_idname = "camera.dnd_pan"
    bl_label = "Camera panning"

    def execute(self,context):
        dm_property = bpy.context.scene.dm_property
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        if dm_property.camera_pan_toggle is None:
                            dm_property.camera_pan_toggle = space.lock_camera
                        dm_property.camera_pan_toggle = not dm_property.camera_pan_toggle
                        space.lock_camera = dm_property.camera_pan_toggle
        return {'FINISHED'}

class MESH_Create_GeometryNode_Walls(bpy.types.Operator):
    """Create Walls with Geometry Nodes"""
    bl_idname = "mesh.wall_add"
    bl_label = "Add Walls"
    def execute(self,context):
        bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        wall = context.object
        wall.name = "Wall"
        mesh = wall.data
        # deselect all vertices
        bpy.ops.object.mode_set(mode='OBJECT')  # can change selection only in Object mode
        for face in mesh.polygons:  # you also have to deselect faces and edges
            face.select = False
        for edge in mesh.edges:
            edge.select = False
        for vert in mesh.vertices:
            vert.select = vert.co.x < 0  # select vertices that are below the threshold
            vert.co.x = 0
        # enter edit mode and delete vertices
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        CreateExtrudeGeoNode(self,context,wall)
        dm_property = context.scene.dm_property
        addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, 
            wall)
            
        bpy.context.view_layer.objects.active = wall
        wall.select_set(True)
        return{'FINISHED'}

class MESH_Create_GeometryNode_Pillars(bpy.types.Operator):
    """Create Walls with Geometry Nodes"""
    bl_idname = "mesh.pillar_add"
    bl_label = "Add Pillar"
    def execute(self,context):
        dm_property = context.scene.dm_property
        bpy.ops.mesh.primitive_circle_add(radius=1.524, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        pillar = context.object
        pillar.name = "Pillar"

        CreateExtrudeGeoNode(self,context,pillar)
        addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, 
            pillar)
        bpy.context.view_layer.objects.active = pillar
        pillar.select_set(True)
        return{'FINISHED'}

class MESH_Create_Cave(bpy.types.Operator):
    """Create Cave Roof for Light Shadow"""
    bl_idname = "mesh.cave_add"
    bl_label = "Add Cave"

    def execute(self,context):
        dm_property = context.scene.dm_property
        bpy.ops.mesh.primitive_plane_add(size=10, enter_editmode=False, align='WORLD', location=(0, 0, 10), scale=(1, 1, 1))
        cave = context.object
        cave.name = "Cave"
        cave.data.materials.append(CreateCaveMaterial(self, context))
        addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, cave)
        bpy.context.view_layer.objects.active = cave
        return{'FINISHED'}

class ImportMapImage(bpy.types.Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_mesh.map_image"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Map Image"

    # ImportHelper mixin class uses this
    filename_ext = ".png"

    filter_glob: bpy.props.StringProperty(
        default="*.png;*.jpg;*.gif;*.tif",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    # use_setting: bpy.props.BoolProperty(
    #     name="Example Boolean",
    #     description="Example Tooltip",
    #     default=True,
    # )

    # type: bpy.props.EnumProperty(
    #     name="Example Enum",
    #     description="Choose between two items",
    #     items=(
    #         ('OPT_A', "First Option", "Description one"),
    #         ('OPT_B', "Second Option", "Description two"),
    #     ),
    #     default='OPT_A',
    #)

    def execute(self, context):
        image = bpy.data.images.load(self.filepath)
        x = image.size[0]
        y = image.size[1]
        mean = (x + y) /2
        x= x / mean 
        y= y / mean
        bpy.ops.mesh.primitive_plane_add(size=10, enter_editmode=False, align='WORLD', location=(0, 0, -0.2), scale=(1, 1, 1))
        map = context.object
        map.dimensions = (x,y,0)
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
        map.name = "Cave"
        map.data.materials.append(CreateMapMaterial(self, context,image))
        dm_property = context.scene.dm_property
        addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, 
            map)
        bpy.context.view_layer.objects.active = map
        map.select_set(True)
        return{'FINISHED'}


def setTransparency(self, context,material, alpha):
    shaderMix_node = material.node_tree.nodes.get('Mix Shader')
    shaderMix_node.inputs[0].default_value = alpha

class MESH_Setup_Map(bpy.types.Operator):
    """Create Cave Roof for Light Shadow"""
    bl_idname = "mesh.map_scale"
    bl_label = "Setup Map"

    def update_scale(self,context):
        map = context.object
        map.scale[0] = self.scale
        map.scale[1] = self.scale

    def update_loc(self,context):
        map = context.object
        map.location[0] = self.xpos
        map.location[1] = self.ypos

    scale : bpy.props.FloatProperty(name="Scale",default=1,update=update_scale)
    xpos : bpy.props.FloatProperty(name="X Position",default=0,update=update_loc)
    ypos : bpy.props.FloatProperty(name="Y Position",default=0,update=update_loc)

    def execute(self,context):
        map = context.object
        material = map.material_slots[0].material
        setTransparency(self,context,material, 1.0)
        return{'FINISHED'}
    def invoke(self, context, event):
        map = context.object
        material = map.material_slots[0].material
        setTransparency(self,context,material, .1)
        return context.window_manager.invoke_props_dialog(self)

class LIGHT_Create_Torch(bpy.types.Operator):
    """Create Torch Light"""
    bl_idname = "light.torch_add"
    bl_label = "Add Torch"
    def execute(self, context):
        bpy.ops.object.light_add(type='POINT', align='WORLD', location=(0, 0, 5), rotation=(0, 0, 0), scale=(1, 1, 1))
        torch = bpy.context.object
        torch.name = "Torch"
        torch.data.energy = 10000
        torch.data.shadow_soft_size = 9.144
        torch.data.color = (0, 0, 1)
        torch.data.use_shadow = False
        torch.data.use_custom_distance = True
        torch.data.cutoff_distance = 12.192
        dm_property = context.scene.dm_property
        addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, torch)
        bpy.context.view_layer.objects.active = torch
        torch.select_set(True)
        return{'FINISHED'}

class Window_new(bpy.types.Operator):
    """Bla """
    bl_idname = "window.dnd_new"
    bl_label = "New Window"
    def execute(self, context):
        bpy.ops.wm.window_new()
        bpy.context.area.ui_type = 'VIEW_3D'
        bpy.context.space_data.shading.type = 'RENDERED'
        bpy.context.space_data.overlay.show_overlays = False
        bpy.context.space_data.show_gizmo = False
        bpy.ops.screen.screen_full_area(use_hide_panels=True)
        #Camera view
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        area.spaces[0].region_3d.view_perspective = 'CAMERA'
        return {'FINISHED'}


# Annotation properties
class VIEW3D_PT_grease_pencil(AnnotationDataPanel, bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DM Tools"

    # NOTE: this is just a wrapper around the generic GP Panel


class VIEW3D_PT_annotation_onion(AnnotationOnionSkin, bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DM Tools"
    bl_parent_id = 'VIEW3D_PT_grease_pencil'

    # NOTE: this is just a wrapper around the generic GP Panel


class TOPBAR_PT_annotation_layers(bpy.types.Panel, AnnotationDataPanel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_label = "Layers"
    bl_ui_units_x = 14





blender_classes = [
    PlayerProperties,    
    FloorPointerProperties,
    MapPointerProperties,
    PlayerPointerProperties,
    EnemyProperties,
    EnemyPointerProperties,
    DMProperties,
    MESH_Setup_Map,
    _PT_SceneSetupPanel,
    _PT_CameraSetupPanel,
    _PT_LightSetupPanel,
    _PT_PlayerListPanel,
    _UL_Playerlist_player,
    _PT_EnemyListPanel,
    _UL_Enemylist,
    _PT_WindowSetupPanel,
    _PT_AddSetupPanel,
    Map_List_Button,
    Floor_List_Button,
    _UL_Maplist,
    _UL_Floorlist,
    ImportMapImage,
    PLAYER_Distance_Button,
    PLAYER_List_Button,
    PLAYER_Torch_Button,
    PLAYER_add,
    PLAYER_update,
    ENEMY_add,
    MAP_add,
    MAP_update,
    FLOOR_add,
    ENEMY_Distance_Button,
    Enemy_List_Button,
    SCENE_Setup,
    SCENE_Grid_Setup,
    CAMERA_add,
    CAMERA_remove,
    CAMERA_zoom,
    CAMERA_panning,
    Window_new,
    MESH_Create_GeometryNode_Walls,
    MESH_Create_Cave,
    MESH_Create_GeometryNode_Pillars,
    LIGHT_Create_Torch,
    VIEW3D_PT_grease_pencil,
    VIEW3D_PT_annotation_onion,
    TOPBAR_PT_annotation_layers
]

# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access)
def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)

    

    bpy.types.Scene.dm_property = bpy.props.PointerProperty(type = DMProperties)    
    bpy.types.Object.player_property = bpy.props.PointerProperty(type = PlayerProperties)
    bpy.types.Object.enemy_property = bpy.props.PointerProperty(type = EnemyProperties)
    bpy.types.GreasePencil.map_property = bpy.props.PointerProperty(type = MapPointerProperties)
    bpy.types.GreasePencilLayers.floor_property = bpy.props.PointerProperty(type = FloorPointerProperties)

    #del bpy.context.scene["dm_property"]
    #bpy.context.scene.dm_property.master_coll = bpy.context.scene.collection

def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)    
        
    del bpy.types.Scene.dm_property
    del bpy.types.Object.player_property
    del bpy.types.Object.enemy_property


if __name__ == "__main__":
    register()

    