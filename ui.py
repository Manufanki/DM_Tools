from distutils.log import debug
import bpy

from . utils import *


#region panels
class DM_PT_SceneSetupPanel(bpy.types.Panel):
    bl_label = "Scene"
    bl_idname = "_PT_SceneSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        
        col = layout.column()
        if not dm_property.is_setup:
            col.operator("scene.setup", icon ="WORLD")
        else:
            col.operator("scene.setup", icon ="WORLD")
            col.prop(context.scene.unit_settings, 'system')
            col.operator("scene.grid_scale", text="Set 5ft Grid")
            col.operator("add.grid", icon="MESH_GRID")
            #col.prop(context.scene.tool_settings, "use_snap")

class DM_PT_CameraSetupPanel(bpy.types.Panel):
    bl_label = "Camera"
    bl_idname = "_PT_CameraSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        if dm_property.is_setup:
            col = layout.column()

            if dm_property.camera is None:
                col.operator("camera.add", icon ='OUTLINER_DATA_CAMERA')
            else:
                if dm_property.camera_pan_toggle:
                    col.operator("camera.pan",text ="Panning active", icon="CANCEL")
                else:
                    col.operator("camera.pan",text ="Panning", icon="VIEW_PAN")
                col.operator("view3d.view_camera",icon='OUTLINER_DATA_CAMERA')

                col.prop(dm_property, "camera_zoom", text="Zoom")

                #pan_row.prop(dm_property,"camera_pan_toggle",text="Active")
                col.operator("camera.remove", icon ='PANEL_CLOSE')
     
class DM_PT_LightSetupPanel(bpy.types.Panel):
    bl_label = "Light"
    bl_idname = "_PT_LightSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        if dm_property.is_setup:
            col = layout.column()
            if not dm_property.day_night:
                col.operator('light.daynight',icon ="LIGHT_SUN",text = "Day")
            else:
                 col.operator('light.daynight',icon ="SHADING_SOLID",text = "Night")
            # if dm_property.global_Sun != None:
            #     col.prop(dm_property.global_Sun, 'diffuse_factor',text = "Sun Light")

class DM_PT_PlayerListPanel(bpy.types.Panel):
    """Creates a Panel for all Player Settings"""
    bl_label = "Player"
    bl_idname = "PT_ui_player_list"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        if dm_property.is_setup:
            
            list_row_layout = layout.row()

            list_row_layout.template_list("DM_UL_Playerlist_player", "", dm_property, "characterlist", dm_property, "characterlist_data_index")
            menu_sort_layout_column = list_row_layout.column()
            menu_sort_layout = menu_sort_layout_column.column(align=True)
            menu_sort_layout.operator("player.update", text="", icon="FILE_REFRESH")
            menu_sort_layout.operator("player.add", text="", icon="ADD")
            #menu_sort_layout.operator("list.list_o", text="", icon="ADD").menu_active = 6
            menu_sort_layout.operator("list.list_op", text="", icon="REMOVE").menu_active = 7
            menu_sort_layout2 = menu_sort_layout_column.column(align=True)
            menu_sort_layout.separator(factor=3.0)
            menu_sort_layout2.operator("list.list_op", text="", icon="TRIA_UP").menu_active = 4
            menu_sort_layout2.operator("list.list_op", text="", icon="TRIA_DOWN").menu_active = 5


            col = layout.column()
            row = layout.row()

            i = 0
            for char in dm_property.characterlist:
                if bpy.context.object == char.obj: 
                    player_property = char.obj.player_property
                    layout.prop(player_property, "name")
                    if player_property.is_npc == False:
                        layout.prop(player_property, "darkvision", text="Darkvision")
                    list_row = layout.row()
                    if player_property.distance_sphere.hide_get():
                        list_row.operator("player.distance_toggle", text="", icon="HIDE_ON")
                    else:
                        list_row.operator("player.distance_toggle",text ="",  icon="HIDE_OFF")
                    list_row.label(text="Distance Measure")
                    split = list_row.split(factor=0.9)
                    split.prop(player_property, "move_distance", text="")
                    split.label(text=GetCurrentUnits()[0])

                    list1_row = layout.row()
                    if player_property.torch.hide_get():
                        list1_row.operator("player.torch", text="", icon="HIDE_ON")
                        list1_row.label(text="Use Torch")
                    else:
                        list1_row.operator("player.torch", text="", icon="HIDE_OFF")
                        list1_row.label(text="Use Torch")
                        list1_row.prop(player_property.torch.data, "cutoff_distance", text="")

                    list2_col = layout.column()
                    list2_col.label(text="Player Stats")
                    list2_col.prop(player_property,"player_height")
                    list2_col.prop(player_property,"health_points")
                    list2_col.prop(player_property,"armor_class")
                    break
class DM_PT_AddSetupPanel(bpy.types.Panel):
    bl_label = "Map"
    bl_idname = "_PT_MapSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        if dm_property.is_setup:

            #row = layout.row()
            
            col = layout.column()
            gpd_owner = context.annotation_data_owner  
            gpd = context.annotation_data
            #col.template_ID(gpd_owner, "grease_pencil", new="gpencil.annotation_add", unlink="gpencil.data_unlink")

            list_row_layout = col.row()

            list_row_layout.operator('example.choose_item', text="", icon='PRESET')
            if len(dm_property.maplist) > 0:
                list_row_layout.prop(dm_property.maplist[dm_property.maplist_data_index],"name", text ="")
            else:
                list_row_layout.label(text= "No Map exists")
            list_row_layout.operator("map.add", text="", icon="ADD")
            if len(dm_property.maplist) > 0:
                list_row_layout.operator("list.map_op", text="", icon="REMOVE").menu_active = 7
            list_row_layout.operator("map.update", text="", icon="FILE_REFRESH")
            # list_row_layout.template_list("DM_UL_Maplist", "", dm_property, "maplist", dm_property, "maplist_data_index")
            # menu_sort_layout_column = list_row_layout.column()
            # menu_sort_layout = menu_sort_layout_column.column(align=True)
            
            # menu_sort_layout.operator("map.add", text="", icon="ADD")
            # #menu_sort_layout.operator("list.list_o", text="", icon="ADD").menu_active = 6
            # menu_sort_layout.operator("list.map_op", text="", icon="REMOVE").menu_active = 7
            # menu_sort_layout2 = menu_sort_layout_column.column(align=True)
            # menu_sort_layout.separator(factor=3.0)
            # menu_sort_layout2.operator("list.map_op", text="", icon="TRIA_UP").menu_active = 4
            # menu_sort_layout2.operator("list.map_op", text="", icon="TRIA_DOWN").menu_active = 5

            if len(dm_property.maplist) > 0:
                map = dm_property.maplist[dm_property.maplist_data_index]

                #col = row.column()
                list_row_layout = col.row()
                list_row_layout.template_list("DM_UL_Floorlist", "", map, "floorlist", map, "floorlist_data_index")
                menu_sort_layout_column = list_row_layout.column()
                menu_sort_layout = menu_sort_layout_column.column(align=True)
                menu_sort_layout.operator("floor.add", text="", icon="ADD")
                #menu_sort_layout.operator("list.list_o", text="", icon="ADD").menu_active = 6
                menu_sort_layout.operator("list.floor_op", text="", icon="REMOVE").menu_active = 7
                menu_sort_layout2 = menu_sort_layout_column.column(align=True)
                menu_sort_layout.separator(factor=3.0)
                menu_sort_layout2.operator("list.floor_op", text="", icon="TRIA_UP").menu_active = 4
                menu_sort_layout2.operator("list.floor_op", text="", icon="TRIA_DOWN").menu_active = 5


class DM_PT_AddGroundPanel(bpy.types.Panel):
    """Creates a Panel for all Player Settings"""
    bl_label = "Add Background"
    bl_idname = "PT_ui_add_ground"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    bl_parent_id = '_PT_MapSetupPanel'

    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
       
        if len(dm_property.maplist) > 0:
            map = dm_property.maplist[dm_property.maplist_data_index]
            if len(map.floorlist) > 0:
                    col = layout.column()
                    col.label(text="Add Map")
                    col.operator("import_mesh.image_plane", icon="IMAGE_DATA")
                    col.operator("add.white_map_image", icon="MESH_GRID")
                    col.operator("mesh.gpencil_add", icon = "GREASEPENCIL")
                    col.operator("add.gpencil_to_wall", icon="OUTLINER_OB_GREASEPENCIL")
                    #col.operator("mesh.map_scale", icon="SETTINGS")    
class DM_PT_AddWallsPanel(bpy.types.Panel):
    """Creates a Panel for all Player Settings"""
    bl_label = "Add Geometry and Light"
    bl_idname = "PT_ui_addwalls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    bl_parent_id = '_PT_MapSetupPanel'

    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        if len(dm_property.maplist):
            map = dm_property.maplist[dm_property.maplist_data_index]
            if len(map.floorlist) > 0:
                    col = layout.column()
                    col.operator("mesh.geowall_add", icon="MOD_BUILD")
                    col.operator("mesh.pillar_add",icon="MESH_CYLINDER") 
                    #col.operator("light.torch_add",icon="LIGHT_POINT").reveal = False   

class DM_PT_WindowSetupPanel(bpy.types.Panel):
    bl_label = "Window and Touch"
    bl_idname = "_PT_WindowSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        if dm_property.is_setup:
            col = layout.column()

            col.operator("window.new", icon ='WINDOW')
            col.operator("wm.window_fullscreen_toggle",icon ="FULLSCREEN_ENTER")

            if dm_property.touch_active:
                col.operator("touch.use_touch",icon ="CANCEL", text="Close Touch")
            else:
                col.prop(dm_property, "touch_update_rate", text="Touch FPS:")
                col.operator("touch.use_touch",icon ="PROP_OFF")
            col.label(text="Touch setting")
            if obj_in_objectlist(context.active_object, dm_property.groundlist):
                col.operator("add.ground",icon ="REMOVE", text="Remove Ground")
            else:
                col.operator("add.ground",icon ="ADD", text="Add Ground")
            
            


#region lists

class DM_UL_Playerlist_player(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item.obj.player_property
        ma = slot.name
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.3)
            row = layout.row(align=True)
            if ma:
                split.prop(slot, "player_color", text ="")
                split.prop(slot, "name", text="", emboss=False, icon_value=icon)
                row.prop(slot, "list_index", text="Init")
                row.prop(slot,"health_points",text ="HP")
                row.prop(slot.light_coll, "hide_viewport", text="", icon="HIDE_OFF")
                row.prop(slot.player_coll, "hide_viewport", text="", emboss=False, icon_value=icon)
            else:
                split.label(text="", translate=False, icon_value=icon)

        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class DM_UL_Maplist(bpy.types.UIList):

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

class DM_UL_Floorlist(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item
        ma = slot.name


        dm_property = context.scene.dm_property
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.2)
            if ma:
                map = dm_property.maplist[dm_property.maplist_data_index]
                try:
                    layer = map.annotation.layers[ma]
                    split.prop(layer, "color", text ="")
                except:
                    split.label(text ="no layer assigned")
                split.prop(slot, "name", text="", emboss=False, icon_value=icon)
            else:
                split.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

#region operator 

class PLAYER_List_Button(bpy.types.Operator):
    """List Operations"""
    bl_idname = "list.list_op"
    bl_label = "Player List Operator"
    bl_description = "List Operations"
    bl_options = {"REGISTER", "UNDO"}

    menu_active: bpy.props.IntProperty(name="Button Index")



    def execute(self, context):
        dm_property = context.scene.dm_property

        char_list = dm_property.characterlist
        index = dm_property.characterlist_data_index

        if self.menu_active == 1:
            print("Select")
            pass
			
        if self.menu_active == 2:
            anim_entry = char_list[index]
            #anim_entry = dm_property.characterlist
            anim_entry.width = anim_entry.width + 1

        if self.menu_active == 3:
            char_list.clear()

		# Move entry up
        if self.menu_active == 4:
            if index > 0:
                char_list.move(index, index-1)
                index -= 1

		# Move entry down
        if self.menu_active == 5:
            if index < len(char_list)-1:
                char_list.move(index, index+1)
                index += 1
        
        # Add entry
        if self.menu_active == 6:
            item = index.add()
            if len(bpy.data.actions) > 0:
                item.action = bpy.data.actions[0]
            if index < len(char_list)-1:
                char_list.move(len(char_list)-1, index+1)
                index += 1


		# Remove Item
        if self.menu_active == 7:
            if index >= 0 and index < len(char_list):
                player = char_list[index].obj
                player.player_property.distance_sphere.parent = player
                try:
                    player.player_property.player_coll.children.unlink(player.player_property.light_coll)
                    bpy.data.collections.get("Player").children.unlink(player.player_property.player_coll)
                except:
                    print("no collection to unlink")
                delete_hierarchy(player)
                char_list.remove(index)
                index = min(index, len(char_list)-1)


        # Sort
        if self.menu_active == 8:
            initiative_list = {}
            for i in range(len(char_list)):
                initiative_list[i]  =  char_list[i].obj.player_property.list_index


            initiative_list = dict(sorted(initiative_list.items(), key=lambda item: item[1],reverse=True))
            
            print("sorted : ",initiative_list)

            print(list(initiative_list.keys()).index(i))

            for i in range(len(char_list)):
                dif = i - list(initiative_list.keys()).index(i) 
                print("before:" ,i, " : " , dif)
                k = i
                
                if dif > 0:
                    for j in range(abs(dif)):
                        char_list.move(k, k-1)
                        k = k-1
                        print("move up ", j)
                if dif < 0:
                    for j in range(abs(dif)-1):
                        char_list.move(k, k+1)
                        k = k+1
                        print("move down " , j)
                dif = k - list(initiative_list.keys()).index(i) 
                print("after:" ,i, " : " , dif)
                print()
                print()
            
  
        return {"FINISHED"}      

class Map_List_Button(bpy.types.Operator):
    """List Operations"""
    bl_idname = "list.map_op"
    bl_label = "Map List Operator"
    bl_description = "List Operations"
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
            #anim_entry = dm_property.characterlist
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
            item = list.add()
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
    """List Operations"""
    bl_idname = "list.floor_op"
    bl_label = "Floor List Operator"
    bl_description = "List Operations"
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
            #anim_entry = dm_property.characterlist
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
                map = dm_property.maplist[dm_property.maplist_data_index]
                map.map.children.unlink(collection)
                map.annotation.layers.remove( map.annotation.layers[list[index].floor.name])
                list.remove(index)
                index = min(index, len(list)-1)
        return {"FINISHED"}      

class ChooseItemOperator(bpy.types.Operator):
    """Select an existing Map from the List"""
    bl_idname = "example.choose_item"
    bl_label = "Choose Map"
    bl_options = {'INTERNAL'}
    bl_property = "enum"

    def get_enum_options(self, context):
        enum = []
        dm_property = context.scene.dm_property
        test = dm_property.maplist
        for i in range(len(test)):
            item = (str(i),str(test[i].name),"","PRESET", i)
            enum.append(item)
        print(self.enum)
        return enum

    enum: bpy.props.EnumProperty(items=get_enum_options, name="Items")


    def execute(self, context):
        dm_property = context.scene.dm_property
        i = int(self.enum)
        map = dm_property.maplist[i]
        dm_property.maplist_data_index = i
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"FINISHED"}


blender_classes = [
    DM_PT_SceneSetupPanel,
    DM_PT_CameraSetupPanel,
    DM_PT_LightSetupPanel,
    DM_PT_PlayerListPanel,
    DM_PT_AddSetupPanel,
    DM_PT_AddGroundPanel,
    DM_PT_AddWallsPanel,
    DM_PT_WindowSetupPanel,
    DM_UL_Playerlist_player,
    DM_UL_Maplist,
    DM_UL_Floorlist,
    Map_List_Button,
    Floor_List_Button,
    PLAYER_List_Button,
    ChooseItemOperator,
]
    
def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)


def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class) 
    
