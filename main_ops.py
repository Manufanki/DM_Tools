
import bpy
import random
import colorsys
from bl_ui.properties_grease_pencil_common import (
    AnnotationDataPanel,
    AnnotationOnionSkin,
)

from bpy_extras.io_utils import ImportHelper
from ctypes import windll

from collections import namedtuple



try:
    from .touch import register
    print("Touch is inported")
    pygame_installed = True
except ModuleNotFoundError as e:
    print(e)
    pygame_installed = False
    #print("pygame is not installed")
from .properties import *
from .utils import *
from .ui import *
from .import_images import *


#endregion Methods     

#region Operatior
class PLAYER_Distance_Button(bpy.types.Operator):
    bl_idname = "player.distance_toggle"
    bl_label = "Toggle Visibility of Distance Circle"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        else:
            return True
    def execute(self, context):

        if context.object is None:
            return {"FINISHED"} 
        if context.object.player_property.distance_sphere.hide_get():
            context.object.player_property.distance_sphere.parent = None
            context.object.player_property.distance_sphere.hide_set(False)
        else:
            context.object.player_property.distance_sphere.parent = context.object
            context.object.player_property.distance_sphere.hide_set(True)
        loc = context.object.location
        context.object.player_property.distance_sphere.location = (loc.x, loc.y, loc.z + 1)
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
    bl_idname = "player.add"
    bl_label = "Add Player"
    

    tmp_is_npc : bpy.props.BoolProperty(name ="NPC", default= False)
    tmp_name : bpy.props.StringProperty(name ="Enter Name", default= "player")


    def invoke(self, context, event):
                
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        dm_prop = bpy.context.scene.dm_property
        

        location = get_rayhit_loc(self, context,context.region, (context.region.width /2, context.region.height /2))


        rgb = colorsys.hsv_to_rgb(random.random(),1,1)
        tmp_player_color = (rgb[0],rgb[1],rgb[2],1)

        player_height = 2
        if self.tmp_is_npc == True:
            player_height = 0.5
            rgb = colorsys.hsv_to_rgb(random.uniform(0, 1),1,.05)
            tmp_player_color = (rgb[0],rgb[1],rgb[2],1)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=player_height, enter_editmode=False, align='WORLD', location=location, scale=(1, 1, 1))
        player = bpy.context.object
        component_list = []
        light_list = []
        component_list.append(player)


        player.name = self.tmp_name
        player_property = player.player_property
        player_property.player_id = dm_prop.next_player_id
        dm_prop.next_player_id += 1
        player.data.vertices[0].co.y += 0.3
        player.data.vertices[1].co.y += 0.3
        player_property.player = player

        player_pointer = dm_prop.characterlist.add()
        player_pointer.character = player

        player_property.list_index = dm_prop.characterlist_data_index
        player_property.name = self.tmp_name
        player_property.is_npc = self.tmp_is_npc
        if self.tmp_is_npc == True:
            player_property.player_material = CreateNPCMaterial(self, context, tmp_player_color)
        else:
            player_property.player_material = CreatePlayerMaterial(self, context, tmp_player_color)
        player.data.materials.append(player_property.player_material)
        player.lock_location = (False, False, True)
        player.lock_rotation = (True, True, False)
        
        bpy.ops.mesh.primitive_circle_add(vertices=128, radius= .5, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.convert(target='GPENCIL')
        distance_sphere = context.object
        distance_sphere.data.pixel_factor = 0.1
        distance_sphere.active_material.grease_pencil.show_fill = True
        distance_sphere.active_material.grease_pencil.color = (tmp_player_color[0], tmp_player_color[1], tmp_player_color[2], 1)
        distance_sphere.active_material.grease_pencil.fill_color = (tmp_player_color[0], tmp_player_color[1], tmp_player_color[2], .1)
        distance_sphere.data.layers[0].use_lights = False

        distance_sphere.name = "Distance Sphere"
        distance_sphere.parent = player
        distance_sphere.lock_location = (False, False, True)

        bpy.ops.mesh.primitive_circle_add(vertices=32, radius= .05, enter_editmode=False, align='WORLD', location=(0, 0, 1), scale=(1, 1, 1))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.convert(target='GPENCIL')    
        selection_sphere = context.object
        selection_sphere.data.pixel_factor = 0.1
        selection_sphere.active_material.grease_pencil.show_fill = True
        selection_sphere.active_material.grease_pencil.color = (tmp_player_color[0], tmp_player_color[1], tmp_player_color[2], 1)
        selection_sphere.active_material.grease_pencil.fill_color = (tmp_player_color[0], tmp_player_color[1], tmp_player_color[2], .1)
        selection_sphere.data.layers[0].use_lights = False
        selection_sphere.data.layers[0].line_change = 60

        selection_sphere.parent = player
        selection_sphere.name = "Selection Sphere"
        selection_sphere.data.stroke_thickness_space = 'SCREENSPACE'





        player_property.selection_sphere = selection_sphere
        player_property.distance_sphere = distance_sphere
        player_property.move_distance = player_property.move_distance
        player_property.player_color = tmp_player_color
        # distance_sphere.data.materials.append(CreateDistanceMaterial(self, context, (0,1,0,0.2)))
        component_list.append(distance_sphere)
        component_list.append(selection_sphere)


        

        
        bpy.ops.object.light_add(type='SPOT', align='WORLD', location=(0, 0, player_property.player_height), rotation=(1.5708, 0, 0), scale=(1, 1, 1))
        spot = bpy.context.object
        spot.name = "Player Vision Day"
        spot.parent = player
        spot.data.spot_size = 1.74
        spot.data.shadow_soft_size = 100
        spot.data.energy = 500000
        spot.data.spot_blend = 1
        spot.data.color = (1, 1, 1)
        component_list.append(spot)
        light_list.append(spot)

        bpy.ops.object.light_add(type='POINT', align='WORLD', location=(0, 0,  player_property.player_height), rotation=(1.5708, 0, 0), scale=(1, 1, 1))
        point = bpy.context.object
        point.name = "Player Vision Day Point"
        point.parent = player
        point.data.shadow_soft_size = 2.5
        point.data.energy = 500
        point.data.color = (1, 1, 1)
        component_list.append(point)
        light_list.append(point)


        bpy.ops.object.light_add(type='SPOT', align='WORLD', location=(0, 0,  player_property.player_height), rotation=(1.5708, 0, 0), scale=(1, 1, 1))
        spotDark = bpy.context.object
        spotDark.name = "Player Vision Dark"
        spotDark.parent = player
        spotDark.data.spot_size = 1.74
        spotDark.data.shadow_soft_size = 100
        spotDark.data.energy = 500000
        spotDark.data.color = (1, 1, 1)
        spotDark.data.spot_blend = 1
        #spotDark.data.use_shadow = False
        spotDark.data.use_custom_distance = True
        spotDark.data.cutoff_distance = 0
        component_list.append(spotDark)
        light_list.append(spotDark)

        bpy.ops.object.light_add(type='POINT', align='WORLD', location=(0, 0,  player_property.player_height), rotation=(1.5708, 0, 0), scale=(1, 1, 1))
        pointDark = bpy.context.object
        pointDark.name = "Player Vision Dark Point"
        pointDark.parent = player
        pointDark.data.shadow_soft_size = 2
        pointDark.data.energy = 150
        pointDark.data.color = (1, 1, 1)
        pointDark.data.use_custom_distance = True
        pointDark.data.cutoff_distance = 0
        component_list.append(pointDark)
        light_list.append(pointDark)
        
        
        bpy.ops.object.light_add(type='POINT', align='WORLD', location=(0, 0, 1), rotation=(0, 0, 0), scale=(1, 1, 1))
        torch = bpy.context.object
        torch.name = "Torch"
        torch.parent = player
        torch.data.energy = 40000
        torch.data.shadow_soft_size = 9.144
        torch.data.color = (1, 1, 1)
        torch.data.use_shadow = True
        torch.data.use_custom_distance = True
        torch.data.cutoff_distance = 18.288
        player_property.torch = torch
        component_list.append(torch)

        for obj in component_list:
            player_property.player_coll = addToCollection(self, context, player.name, obj)

        for obj in light_list:
            player_property.light_coll = addToCollection(self, context, player.name + "_light", obj)
                
        if bpy.data.collections.get("Player") is None:
            collection = bpy.data.collections.new("Player")
            bpy.context.scene.collection.children.link(collection)
            collection.children.link(player_property.player_coll)

        else:
            collection = bpy.data.collections.get("Player")   
            collection.children.link(player_property.player_coll)

        player_property.player_coll.children.link( player_property.light_coll)
        if bpy.context.scene.collection.children.get(player_property.player_coll.name):
            bpy.context.scene.collection.children.unlink(player_property.player_coll)
            bpy.context.scene.collection.children.unlink(player_property.light_coll)

        player_property.light_coll.hide_viewport = player_property.is_npc
        
        torch.hide_set(True)
        torch.hide_select = True
        if player_property.is_npc == False:
            point.hide_select = True
            spot.hide_select = True
            spotDark.hide_select = True
            pointDark.hide_select = True
            point.hide_viewport = dm_prop.day_night
            spot.hide_viewport = dm_prop.day_night
            spotDark.hide_viewport = not dm_prop.day_night
            pointDark.hide_viewport = not dm_prop.day_night
            player_property.spot_day = spot
            player_property.point_day = point
            player_property.spot_night = spotDark
            player_property.point_night = pointDark
        distance_sphere.hide_select = True
        distance_sphere.hide_set(True)
        distance_sphere.hide_select = True
        selection_sphere.hide_set(True)
        bpy.context.view_layer.objects.active = player
        player.select_set(True)
        return {'FINISHED'}
class PLAYER_update(bpy.types.Operator):
    "Add Map Collection to the Scene"
    bl_idname = "player.update"
    bl_label = "Update players"
    
    def execute(self, context):
        dm_property = context.scene.dm_property
        if bpy.data.collections.get("Player") is None:
            collection = bpy.data.collections.new("Player")
            bpy.context.scene.collection.children.link(collection)
        else:
            collection = bpy.data.collections.get("Player")
            update_players(self,context,collection)

        bpy.ops.list.list_op(menu_active = 8)
        return {'FINISHED'}

class MAP_add(bpy.types.Operator):
    "Add Map Collection to the Scene"
    bl_idname = "map.add"
    bl_label = "Add Map"
    
    tmp_name : bpy.props.StringProperty(name ="Enter Name", default= "map")
    def invoke(self, context, event):
                
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        bpy.ops.gpencil.annotation_add()

        
        dm_prop = bpy.context.scene.dm_property
        collection = check_if_collection_exists(self.tmp_name)
        
        for coll in dm_prop.maps_coll.children:
            if coll is collection:
                return {'CANCELLED'}
        dm_prop.maps_coll.children.link(collection)

        #context.scene.grease_pencil.new(name = collection.name)
        gpd = context.annotation_data
        gpd.name = collection.name
        try:
            gpd.layers.remove(gpd.layers["Note"])
        except:
            print("no layer Note")
        collection_pointer = dm_prop.maplist.add()
        collection_pointer.annotation = gpd
        collection_pointer.map = collection
        collection_pointer.name = collection.name

        dm_prop.maplist_data_index = len(dm_prop.maplist)-1

        bpy.ops.floor.add()
        
        return {'FINISHED'}
class MAP_update(bpy.types.Operator):
    "Add Map Collection to the Scene"
    bl_idname = "map.update"
    bl_label = "Update Maps"
    
    def execute(self, context):
        dm_property = context.scene.dm_property
        if bpy.data.collections.get("Maps") is None:
            collection = bpy.data.collections.new("Maps")
            bpy.context.scene.collection.children.link(collection)
            dm_property.maps_coll = collection
        else:
            collection = bpy.data.collections.get("Maps")
            update_maps(self,context,collection)
        return {'FINISHED'}

class FLOOR_add(bpy.types.Operator):
    "Add a Floor to the current Map"
    bl_idname = "floor.add"
    bl_label = "Add Floor"
    
    tmp_name : bpy.props.StringProperty(name ="Enter Name", default= "floor")


    def invoke(self, context, event):
                
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        dm_property = bpy.context.scene.dm_property
        map = dm_property.maplist[dm_property.maplist_data_index]

        collection = check_if_collection_exists(self.tmp_name)

        for maps in dm_property.maplist:
            for coll in maps.map.children:
                if coll is collection:
                    return {'CANCELLED'}
        dm_property.maplist[dm_property.maplist_data_index].map.children.link(collection)
        collection_pointer = map.floorlist.add()
        collection_pointer.floor = collection
        collection_pointer.name = collection.name
        

        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = recurLayerCollection(layer_collection, collection_pointer.name)
        bpy.context.view_layer.active_layer_collection = layerColl


        gpl = map.annotation.layers.new(name = collection.name)
        gpl.color = (1,1,1)
        map.annotation.layers.active = gpl
        #collection_pointer.floor.annotation = gpl
        collection_pointer.annotation = map.annotation
        
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
    """Setup of Scenebackground, Eevee ettings, Collections and Camera"""
    bl_idname = "scene.setup"
    bl_label = "Setup the Scene"

    def execute(self, context):

        dm_property = context.scene.dm_property
        #bpy.ops.object.select_all(action='SELECT')
        #bpy.ops.object.delete(use_global=False)
        if bpy.data.collections.get("Collection") is not None:
            collection = bpy.data.collections.get("Collection")
            #objs = collection.all_objects
            # for obj in objs:
            #     bpy.data.objects.remove(obj, do_unlink=True)
            # if bpy.context.scene.collection.children.get("Collection"):
            #     bpy.context.scene.collection.children.unlink(collection)

        if bpy.data.collections.get("Camera") is None:
            collection = bpy.data.collections.new("Camera")
            bpy.context.scene.collection.children.link(collection)

        if bpy.data.collections.get("Maps") is None:
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
        bpy.context.scene.eevee.bloom_radius = 1.5

        bpy.context.space_data.shading.type = 'MATERIAL'
        
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
        dm_property.is_setup = True

        if dm_property.camera is None:
                bpy.ops.camera.add()
            
        bpy.ops.scene.grid_scale()

        return {'FINISHED'}

class CAMERA_add(bpy.types.Operator):
    """Add Camera, a Darkness Plane and Light to the Scene"""
    bl_idname = "camera.add"
    bl_label = "Add Camera"
    
    def execute(self, context):
        dm_property = context.scene.dm_property
        bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=(0, 0, 100), rotation=(0, 0, 0), scale=(1, 1, 1))
        camera = bpy.context.object
        camera.name = "MainCamera"
        camera.data.clip_end = 1000

        camera.data.type = 'PERSP'
        camera.data.lens = 50.0
        camera.lock_location = (False, False, True)
        camera.lock_rotation = (True, True, True)
        camera.data.passepartout_alpha = 1
        dm_property.camera = camera

        
        # bpy.ops.mesh.primitive_plane_add(size=1000, enter_editmode=False, align='WORLD', location=(0, 0, -9.5), scale=(1, 1, 1))
        # planeDarkness = bpy.context.object
        # planeDarkness.name = "Darkness Plane"
        # planeDarkness.parent = camera
        
        # planeDarkness.data.materials.append(CreateDarknessMaterial(self,context))
        # planeDarkness.hide_select = True
        
        # bpy.ops.object.light_add(type='SUN', align='WORLD', location=(0, 0, 10), scale=(1, 1, 1))
        # sun = bpy.context.object
        # sun.name = "DND SUN"
        # sun.data.energy = 10
        # sun.data.color = (0, 0, 1)
        # sun.hide_select = True
        # sun.parent = camera

        #context.scene.dm_property.global_Sun = sun.data
        addToCollection(self, context, "Camera",camera)
        #addToCollection(self, context, "Camera",planeDarkness)
        #addToCollection(self, context, "Camera",sun)
        return {'FINISHED'}

class CAMERA_remove(bpy.types.Operator):
    """Add Camera, a Darkness Plane and Light to the Scene"""
    bl_idname = "camera.remove"
    bl_label = "Remove Camera"
    
    def execute(self, context):
        dm_property = context.scene.dm_property
        camera = dm_property.camera
        dm_property.camera = None
        delete_hierarchy(camera)
        return{'FINISHED'}
class CAMERA_zoom(bpy.types.Operator):
    """Toggle Camera Orthographic Scale between 80 and 35"""
    bl_idname = "camera.togglezoom"
    bl_label = "Toggle Camera Zoom"
    
    scale : bpy.props.FloatProperty(min=10, max = 1000)

    def execute(self, context):
        dm_property = context.scene.dm_property
        camera = dm_property.camera
        camera.data.lens = self.scale

        return {'FINISHED'}

class CAMERA_panning(bpy.types.Operator):
    """Add Camera, a Darkness Plane and Light to the Scene"""
    bl_idname = "camera.pan"
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
    bl_idname = "mesh.geowall_add"
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


        dm_property = context.scene.dm_property
        wall.data.materials.append(CreateBackfaceWallMaterial(self, context))
        wall.data.materials.append(CreateTransparentMaterial(self, context))

        CreateExtrudeGeoNode(self,context,wall)
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].use_rim_only = True
        bpy.context.object.modifiers["Solidify"].thickness = 0.3
        bpy.context.object.modifiers["Solidify"].material_offset_rim = 1

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
        pillar.data.materials.append(CreateBackfaceWallMaterial(self, context))
        pillar.data.materials.append(CreateTransparentMaterial(self, context))

        CreateExtrudeGeoNode(self,context,pillar)

        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].use_rim_only = True
        bpy.context.object.modifiers["Solidify"].thickness = 0.3
        bpy.context.object.modifiers["Solidify"].material_offset_rim = 1


        addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, 
            pillar)
        bpy.context.view_layer.objects.active = pillar
        pillar.select_set(True)
        return{'FINISHED'}

class MESH_Create_GreasePencil(bpy.types.Operator):
    """Create Cave Roof for Light Shadow"""
    bl_idname = "mesh.gpencil_add"
    bl_label = "Add Grease Pencil"

    def execute(self,context):
        dm_property = context.scene.dm_property
        bpy.ops.object.gpencil_add(align='WORLD', location=(0,0,1), scale=(1, 1, 1), type='EMPTY')
        gpencil = context.object
        gpencil.name = "gpencil"
        addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, gpencil)
        bpy.context.view_layer.objects.active = gpencil
        bpy.ops.gpencil.paintmode_toggle()
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
    filename_ext = ".png;.jpg;.gif;.tif"

    filter_glob: bpy.props.StringProperty(
        default="*.png;*.jpg;*.gif;*.tif",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        image = bpy.data.images.load(self.filepath)
        x = image.size[0]
        y = image.size[1]
        mean = (x + y) /2
        x= x / mean 
        y= y / mean
        bpy.ops.mesh.primitive_plane_add(size=10, enter_editmode=False, align='WORLD', location=(0, 0, -0.2), )
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

class AddWhiteMapImage(bpy.types.Operator):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "add.white_map_image"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Add white Map"


    def execute(self, context):
        bpy.ops.mesh.primitive_plane_add(size=152.4, enter_editmode=False, align='WORLD', location=(0, 0, -0.2), )
        map = context.object
        map.name = "White_BG"
        #map.data.materials.append(CreatePlayerMaterial(self, context,(1,1,1,1)))
        dm_property = context.scene.dm_property
        addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, 
            map)
        map.hide_select =True

        return{'FINISHED'}

class AddGrid(bpy.types.Operator):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "add.grid"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Add grid"


    def execute(self, context):

        dm_property = context.scene.dm_property

        if dm_property.grid is None or  context.scene.objects.get(dm_property.grid.name) is None:
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, size=152.4, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.delete(type='ONLY_FACE')
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.convert(target='GPENCIL')
            bpy.context.object.show_in_front = True
            grid = context.object
            grid.name = "Grid"

            
            xValDrive = grid.driver_add("location", 0)

            drvVar = xValDrive.driver.variables.new()
            drvVar.name = 'xvar'
            drvVar.type = 'TRANSFORMS'
            drvVar.targets[0].id = dm_property.camera
            drvVar.targets[0].transform_type = 'LOC_X'
            xValDrive.driver.expression = 'int(%s / 1.524) *1.524 ' % drvVar.name

            yValDrive = grid.driver_add("location", 1)

            yVar = yValDrive.driver.variables.new()
            yVar.name = 'yvar'
            yVar.type = 'TRANSFORMS'
            yVar.targets[0].id = dm_property.camera
            yVar.targets[0].transform_type = 'LOC_Y'
            yValDrive.driver.expression = 'int(%s / 1.524) *1.524 ' % yVar.name

            grid.data.layers["Grid_Lines"].line_change = -20
            grid.data.stroke_thickness_space = 'SCREENSPACE'

            dm_property = context.scene.dm_property

            # addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, 
            #     grid)
            addToCollection(self,context, "Camera", grid)
            #grid.hide_select = True
            grid.select_set(False)
            grid.hide_select = True
            dm_property.grid = grid
        else:
            dm_property.grid.hide_viewport = not dm_property.grid.hide_viewport
        return{'FINISHED'}

class ConvertGPencilToWall(bpy.types.Operator):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "add.gpencil_to_wall"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Convert GPencil to Wall"

    @classmethod
    def poll(cls, context):
        # Checks to see if there's any active mesh object (selected or in edit mode)
        active_object = context.active_object
        return active_object is not None and active_object.type == 'GPENCIL'

    def execute(self, context):
               
        bpy.ops.gpencil.convert(type='POLY', timing_mode='LINEAR', use_timing_data=False)
        bpy.context.active_object.select_set(False)
        for obj in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target='MESH')
        wall = context.object
        wall.name = "Wall"
        mesh = wall.data
        wall.data.materials.append(CreateBackfaceWallMaterial(self, context))
        CreateExtrudeGeoNode(self,context,wall)
        dm_property = context.scene.dm_property
        addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, 
            wall)
                
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

    reveal : bpy.props.BoolProperty(name="reveal")
    def execute(self, context):
        bpy.ops.object.light_add(type='POINT', align='WORLD', location=(0, 0, 0.5), rotation=(0, 0, 0), scale=(1, 1, 1))
        torch = bpy.context.object
        torch.name = "Torch"
        if self.reveal:
            torch.data.energy = 35000
            torch.data.shadow_soft_size = 30
            torch.data.color = (1,1,1)
        torch.data.use_shadow = True
        if not self.reveal:
            torch.data.color = (0,0,1)
            torch.data.energy = 10000
            torch.data.shadow_soft_size = 9.144
            torch.data.use_custom_distance = True
            torch.data.cutoff_distance = 12.192
        dm_property = context.scene.dm_property
        addToCollection(self,context, dm_property.maplist[dm_property.maplist_data_index].floorlist[dm_property.maplist[dm_property.maplist_data_index].floorlist_data_index].floor.name, torch)
        bpy.context.view_layer.objects.active = torch
        torch.select_set(True)
        return{'FINISHED'}

class Window_new(bpy.types.Operator):
    """Bla """
    bl_idname = "window.new"
    bl_label = "New Window"

    touch_window : bpy.props.BoolProperty()

    def execute(self, context):
        bpy.ops.wm.window_new()
        #if self.touch_window:
        context.scene.dm_property.hwnd_id = windll.user32.GetForegroundWindow()
        context.scene.dm_property.screen = bpy.context.screen
        #context.scene.touch_manager.rv3d = bpy.context.region_data
        bpy.context.area.ui_type = 'VIEW_3D'
        bpy.context.space_data.shading.type = 'RENDERED'
        bpy.context.space_data.overlay.show_overlays = False
        bpy.context.space_data.show_gizmo = False
        bpy.context.space_data.show_region_header = False

        #bpy.ops.screen.screen_full_area(use_hide_panels=True)
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


class TOUCH_OT_use_touch_operator(bpy.types.Operator):
    bl_idname = "touch.use_touch"
    bl_label = "Use Touchscreen"
    bl_description = "This operator uses starts the pygame modal operator."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(self, context):
        if pygame_installed and context.scene.dm_property.hwnd_id is not -1:
            return True
        else:
            return False 

    def execute(self, context):
        # if not context.scene.dm_property.touch_active:
        #     bpy.ops.window.new(touch_window = True)
        bpy.ops.touch.move('INVOKE_DEFAULT')
        return {"FINISHED"}

blender_classes = [
    MESH_Setup_Map,
    ImportMapImage,
    PLAYER_Distance_Button,
    PLAYER_Torch_Button,
    PLAYER_add,
    PLAYER_update,
    MAP_add,
    MAP_update,
    FLOOR_add,
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
    MESH_Create_GreasePencil,
    ConvertGPencilToWall,
    AddWhiteMapImage,
    AddGrid,
    LIGHT_Create_Torch,
    TOPBAR_PT_annotation_layers,
    TOUCH_OT_use_touch_operator,
    VIEW3D_PT_grease_pencil,
    VIEW3D_PT_annotation_onion,
]

# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access)
def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)


def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)    
        

