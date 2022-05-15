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
            list_row_layout.template_list("DM_UL_Playerlist_player", "", dm_property, "playerlist", dm_property, "playerlist_data_index")
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

class DM_PT_EnemyListPanel(bpy.types.Panel):
    """Creates a Panel for all Player Settings"""
    bl_label = "Enemies"
    bl_idname = "PT_ui_Enemy_list"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DM Tools'
    
    def draw(self, context):
        layout = self.layout

        dm_property = context.scene.dm_property
        if dm_property.is_setup:
            list_row_layout = layout.row()
            list_row_layout.template_list("DM_UL_Enemylist", "", dm_property, "enemylist", dm_property, "enemylist_data_index")
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
                        
                    layout.prop(enemy_property,"health_points")
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

            if dm_property.maplist_data_index >= 0:
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
                    col.operator("import_mesh.map_image", icon="IMAGE_DATA")
                    col.operator("mesh.map_scale", icon="SETTINGS")    


                    col.label(text="Add Geometry")
                    col.operator("mesh.wall_add", icon="MOD_BUILD")
                    col.operator("mesh.cave_add") 
                    col.operator("mesh.pillar_add",icon="MESH_CYLINDER") 
                    col.label(text="Add Light")
                    col.operator("light.torch_add",icon="LIGHT_POINT")

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

#region lists

class DM_UL_Playerlist_player(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item.player.player_property
        ma = slot.name
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.3)

            if ma:
                split.prop(slot, "player_color", text ="")
                split.prop(slot, "name", text="", emboss=False, icon_value=icon)
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

class DM_UL_Enemylist(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item.enemy.enemy_property
        ma = slot.name
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.3)

            if ma:
                split.prop(slot, "enemy_color", text ="")
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
    DM_PT_AddSetupPanel,
    DM_PT_EnemyListPanel,
    DM_PT_WindowSetupPanel,
    DM_UL_Playerlist_player,
    DM_UL_Enemylist,
    DM_UL_Maplist,
    DM_UL_Floorlist,
    Map_List_Button,
    Floor_List_Button,
    PLAYER_List_Button,
    Enemy_List_Button,
    ChooseItemOperator,
]
    
def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)


def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class) 
    
