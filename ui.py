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
       
        col.operator("scene.setup", icon ="WORLD")
        col.prop(context.scene.unit_settings, 'system')
        col.operator("scene.grid_scale")
        col.prop(context.scene.tool_settings, "use_snap")

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
                col.operator("camera.dnd_add", icon ='OUTLINER_DATA_CAMERA')
            else:
                col.operator("camera.dnd_remove", icon ='PANEL_CLOSE')
                if dm_property.camera_zoom_toggle:
                    col.operator("camera.dnd_zoom", icon ='ZOOM_OUT').scale = dm_property.camera_zoom_out
                    col.prop(dm_property, "camera_zoom_in")
                else:
                    col.operator("camera.dnd_zoom", icon ='ZOOM_IN').scale = dm_property.camera_zoom_in
                    col.prop(dm_property, "camera_zoom_out")
                pan_row = col.row()
                pan_row.operator("camera.dnd_pan", icon="VIEW_PAN",text ="Panning")
                if dm_property.camera_pan_toggle:
                    pan_row.label(text="Active")
                else:
                    pan_row.label(text="Not Active")
                col.operator("view3d.view_camera",icon='OUTLINER_DATA_CAMERA')
     
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
            col.prop(dm_property, 'day_night',text = "Day Night")
            if dm_property.global_Sun != None:
                col.prop(dm_property.global_Sun, 'diffuse_factor',text = "Sun Light")

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
            for char in dm_property.characterlist:
                if bpy.context.object == char.character: 
                    player_property = char.character.player_property
                    layout.prop(player_property, "name")
                    if player_property.is_enemy == False:
                        layout.prop(player_property, "darkvision", text="Darkvision")
                    list_row = layout.row()
                    if player_property.distance_circle.hide_get():
                        list_row.operator("player.distance_toggle", text="", icon="HIDE_ON")
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
                    break

class DM_PT_PlayerStatsPanel(bpy.types.Panel):
    """Creates a Panel for all Player Settings"""
    bl_label = "Player Stats"
    bl_idname = "PT_ui_player_stats"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    bl_parent_id = 'PT_ui_player_list'

    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        col = layout.column()
        row = layout.row()

        i = 0
        for char in dm_property.characterlist:
            if bpy.context.object == char.character: 
                player_property = char.character.player_property
                list2_col = layout.column()
                list2_col.prop(player_property,"health_points")
                list2_col.prop(player_property,"armor_class")
                list2_col.prop(player_property,"attack_bonus")
                list2_row = layout.row()
                col1 = list2_row.column()
                col1.label(text="STR")
                col1.prop(player_property,"strength", text= "")
                col2 = list2_row.column()
                col2.label(text="DEX")
                col2.prop(player_property,"dexterity", text= "")
                col3 = list2_row.column()
                col3.label(text="CON")
                col3.prop(player_property,"constitution", text= "")
                col4 = list2_row.column()
                col4.label(text="INT")
                col4.prop(player_property,"intelligence", text= "")
                col5 = list2_row.column()
                col5.label(text="WIS")
                col5.prop(player_property,"wisdom", text= "")
                col6 = list2_row.column()
                col6.label(text="CHA")
                col6.prop(player_property,"charisma", text= "")
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


                if len(map.floorlist) > 0:
                    col = layout.column()
                    col.label(text="Add Map")
                    col.operator("import_mesh.image_plane", icon="IMAGE_DATA")
                    col.operator("add.white_map_image", icon="MESH_GRID")
                    col.operator("add.grid", icon="MESH_GRID")

                    col.operator("mesh.gpencil_add", icon = "GREASEPENCIL")
                    col.operator("add.gpencil_to_wall", icon="OUTLINER_OB_GREASEPENCIL")
                    #col.operator("mesh.map_scale", icon="SETTINGS")    


                    col.label(text="Add Geometry")
                    col.operator("mesh.geowall_add", icon="MOD_BUILD")
                    col.operator("mesh.cave_add") 
                    col.operator("mesh.pillar_add",icon="MESH_CYLINDER") 
                    col.label(text="Add Light")
                    col.operator("light.torch_add",icon="LIGHT_POINT").reveal = False
                    col.operator("light.torch_add",text = "Reveal map",icon="LIGHT_POINT").reveal = True

class DM_PT_WindowSetupPanel(bpy.types.Panel):
    bl_label = "Window"
    bl_idname = "_PT_WindowSetupPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout
        dm_property = context.scene.dm_property
        if dm_property.is_setup:
            col = layout.column()

            col.operator("window.dnd_new", icon ='WINDOW')
            col.operator("wm.window_fullscreen_toggle",icon ="FULLSCREEN_ENTER")

            col.operator("touch.use_touch")
            col.prop(dm_property, "adjust_touchwindow", text="Adjust touchwindow")
            col.prop(dm_property, "hide_touchwindow", text="Hide touchwindow")

#region lists

class DM_UL_Playerlist_player(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item.character.player_property
        ma = slot.name
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.1)
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
            split = layout.split(factor=0.1)
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
    bl_idname = "list.list_op"
    bl_label = "Action List Operator"
    bl_description = ""
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
                player = char_list[index].character
                player.player_property.distance_circle.parent = player
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
                initiative_list[i]  =  char_list[i].character.player_property.list_index


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
    bl_idname = "example.choose_item"
    bl_label = "Choose item"
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
    DM_PT_PlayerStatsPanel,
    DM_PT_AddSetupPanel,
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
    
