import bpy

from . utils import *
#region Properties


class ObjectPointerProperties(bpy.types.PropertyGroup):
    obj : bpy.props.PointerProperty(type=bpy.types.Object)
class FloatPointerProperties(bpy.types.PropertyGroup):
    value : bpy.props.FloatProperty()
class FloatVectorPointerProperties(bpy.types.PropertyGroup):
    value : bpy.props.FloatVectorProperty()

class FloorPointerProperties(bpy.types.PropertyGroup):
    floor : bpy.props.PointerProperty(type=bpy.types.Collection)
    name : bpy.props.StringProperty(update =lambda s, c: update_collection_name(s, c, s.floor))
    annotation : bpy.props.PointerProperty(type=bpy.types.GreasePencil)
    characterlist_data_index : bpy.props.IntProperty(
    )
    characterlist : bpy.props.CollectionProperty(type = ObjectPointerProperties)


class MapPointerProperties(bpy.types.PropertyGroup):
    map : bpy.props.PointerProperty(type=bpy.types.Collection)
    name : bpy.props.StringProperty(update =lambda s, c: update_collection_name(s, c, s.map))
    floorlist_data_index : bpy.props.IntProperty(
        update=selectFloor
    )
    floorlist : bpy.props.CollectionProperty(type = FloorPointerProperties)
    annotation : bpy.props.PointerProperty(type=bpy.types.GreasePencil)


class TouchPointerProperties(bpy.types.PropertyGroup):
    finger_id : bpy.props.IntProperty(default=-1)
    player_id : bpy.props.IntProperty(default=-1)
    zoom_value: bpy.props.FloatProperty()
    start_time: bpy.props.FloatProperty()
    touch_start: bpy.props.IntVectorProperty(
    size=2,
    default=(0, 0),
    )
    touch_pos: bpy.props.IntVectorProperty(
    size=2,
    default=(0, 0),
    )

class PlayerProperties(bpy.types.PropertyGroup):

    def update_touch_active(self, context):
        if self.touch_id != -1:
            self.selection_sphere.hide_set(False)
        else:
            self.selection_sphere.hide_set(True)


    def update_player_height(self, context):
        self.spot_day.location[2] = self.player_height
        self.point_day.location[2] = self.player_height
        self.spot_night.location[2] = self.player_height
        self.point_night.location[2] = self.player_height
    
    def update_player_color(self, context):
        self.distance_sphere.active_material.grease_pencil.color = (self.player_color[0], self.player_color[1], self.player_color[2], 1)
        self.distance_sphere.active_material.grease_pencil.fill_color = (self.player_color[0], self.player_color[1], self.player_color[2], .1)
        self.selection_sphere.active_material.grease_pencil.color = (self.player_color[0], self.player_color[1], self.player_color[2], 1)
        self.selection_sphere.active_material.grease_pencil.fill_color = (self.player_color[0], self.player_color[1], self.player_color[2], .1)
        if self.is_npc:
            rgb_node = self.player_material.node_tree.nodes.get('Principled BSDF')
            rgb_node.inputs[0].default_value = self.player_color
        else:
            rgb_node = self.player_material.node_tree.nodes.get('Emission')
            rgb_node.inputs[0].default_value = self.player_color
   
    def update_move_distance(self,context):
        unitinfo = GetCurrentUnits()
        unit_dist = self.move_distance*2
        distance = unit_to_bu(unit_dist,unitinfo[1])
        distance += 1.5
        self.distance_sphere.dimensions = (distance, distance, distance)

    def update_distance_toggle(self,context):

        if self.distance_toggle:
            self.distance_sphere.parent = None
        else:
            self.distance_sphere.parent = self.player

        self.distance_sphere.hide_set(not self.distance_toggle)
        loc = self.player.location
        self.distance_sphere.location = (loc.x, loc.y, loc.z + 1)

    def update_darkvision(self,context):
        unitinfo = GetCurrentUnits()
        unit_dist = self.darkvision
        distance = unit_to_bu(unit_dist,unitinfo[1])
        distance += 1.5
        self.spot_night.data.cutoff_distance = distance
        self.point_night.data.cutoff_distance = distance

    def update_init(self, context):
        bpy.ops.list.list_op(menu_active = 8)

    def update_torch(self, context):
         self.torch.hide_set(not self.torch_toggle)

    player_coll : bpy.props.PointerProperty(type= bpy.types.Collection)
    light_coll : bpy.props.PointerProperty(type= bpy.types.Collection)
    is_npc : bpy.props.BoolProperty()
    move_distance : bpy.props.FloatProperty(
        #name = "MOVE_DISTANCE",
        description = "Distance in Meter the Player can move in one Turn",
        default = 9,
        min = 1,
        max = 100,
        update=update_move_distance
    )
    distance_toggle : bpy.props.BoolProperty(
        update=update_distance_toggle
    )

    torch_toggle : bpy.props.BoolProperty(
        update=update_torch
    )
    player_id : bpy.props.IntProperty( default = -1)

    touch_id : bpy.props.IntProperty(
        default = -1,
        update=update_touch_active
    )

    touch_pos: bpy.props.IntVectorProperty(
        size=2,
        default=(0, 0),
    )
    active_sphere : bpy.props.PointerProperty(type=bpy.types.Object)
    selection_sphere : bpy.props.PointerProperty(type=bpy.types.Object)
    distance_sphere : bpy.props.PointerProperty(type=bpy.types.Object)
    torch : bpy.props.PointerProperty(type=bpy.types.Object)
    darkvision : bpy.props.FloatProperty(
        #name = "MOVE_DISTANCE",
        description = "Distance in Meter the Player can see in the dark",
        default = 0,
        min = 0,
        max = 100,
        update=update_darkvision
    )
    spot_day : bpy.props.PointerProperty(type=bpy.types.Object)
    point_day : bpy.props.PointerProperty(type=bpy.types.Object)
    spot_night : bpy.props.PointerProperty(type=bpy.types.Object)
    point_night : bpy.props.PointerProperty(type=bpy.types.Object)
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
    player_height : bpy.props.FloatProperty(
        name="player_height",
        description="Player height in meter",
        min=.5,
        max=5,
        default= 1.8,
        update=update_player_height
    )
    list_index : bpy.props.IntProperty(
    name="index",
    description="index",
    default= 0,
    update=update_init
    )

    notes : bpy.props.StringProperty(
    name="notes",
    description="notes",
    default= "",
    )

    health_points : bpy.props.IntProperty(
    name="health_points",
    description="HP",
    default= 20,
    min=0,
    )
    armor_class : bpy.props.IntProperty(
    name="armor_class",
    description="AC",
    default= 10,
    min=0,
    )
    
    positionlist : bpy.props.CollectionProperty(type = FloatVectorPointerProperties)
    rotationlist : bpy.props.CollectionProperty(type = FloatPointerProperties)
    player : bpy.props.PointerProperty(type=bpy.types.Object)

class DMProperties(bpy.types.PropertyGroup):

    def update_active_char(self,context):
        for char in self.characterlist:
            if self.active_character == char.obj and self.use_round_order:
                char.obj.player_property.active_sphere.hide_set(False)
            else:
                char.obj.player_property.active_sphere.hide_set(True) 
  
    is_setup : bpy.props.BoolProperty(default=False)

    active_map_index :  bpy.props.IntProperty(default=-1)
    active_floor_index :  bpy.props.IntProperty(default=-1)

    characterlist_data_index : bpy.props.IntProperty(
        update=selectCharacter
    )
    characterlist : bpy.props.CollectionProperty(type = ObjectPointerProperties)
    active_character : bpy.props.PointerProperty(type=bpy.types.Object,
    update=update_active_char)
    round_index : bpy.props.IntProperty(
        default=0,
        )
    use_round_order :bpy.props.BoolProperty(
    update=update_active_char)

    groundlist : bpy.props.CollectionProperty(type = ObjectPointerProperties)

    maplist_data_index : bpy.props.IntProperty(
        update=selectMap
    )
    maplist : bpy.props.CollectionProperty(type = MapPointerProperties)
    grid :  bpy.props.PointerProperty(type=bpy.types.Object)
    camera :  bpy.props.PointerProperty(type=bpy.types.Object)
    camera_zoom : bpy.props.FloatProperty(
        default= 60,
        min = 10,
        max = 100,
        update=adjustCamera
    )
    camera_pan_toggle : bpy.props.BoolProperty()
    global_Sun : bpy.props.PointerProperty(type=bpy.types.SunLight)
    
    day_night :bpy.props.BoolProperty(
        update=toggleDayNight
    )

    next_player_id : bpy.props.IntProperty(default=0)

    cave_Mat : bpy.props.PointerProperty(type= bpy.types.Material)
    bf_wall_Mat : bpy.props.PointerProperty(type= bpy.types.Material)

    master_coll : bpy.props.PointerProperty(type= bpy.types.Collection)
    maps_coll : bpy.props.PointerProperty(type= bpy.types.Collection)

    screen : bpy.props.PointerProperty(type=bpy.types.Screen)
    hwnd_id : bpy.props.IntProperty(default=-1)

    touch_navigation : bpy.props.BoolProperty()
    touch_active : bpy.props.BoolProperty()
    touchlist : bpy.props.CollectionProperty(type = TouchPointerProperties)

    player_touchlist : bpy.props.CollectionProperty(type = TouchPointerProperties)

    touch_device_id : bpy.props.IntProperty(default=-1)
    hwnd_id : bpy.props.IntProperty(default=-1)
    zoom_value: bpy.props.FloatProperty()
    zoom_value_backup: bpy.props.FloatProperty()
    touch_update_rate : bpy.props.FloatProperty(default=60,
    min= 1,
    max= 144)


blender_classes = [
    ObjectPointerProperties,
    FloatPointerProperties,
    FloatVectorPointerProperties,
    PlayerProperties,    
    FloorPointerProperties,
    MapPointerProperties,
    TouchPointerProperties,
    DMProperties,
    ]
def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
    
    bpy.types.Scene.dm_property = bpy.props.PointerProperty(type = DMProperties)    
    bpy.types.Object.player_property = bpy.props.PointerProperty(type = PlayerProperties)
    bpy.types.GreasePencil.map_property = bpy.props.PointerProperty(type = MapPointerProperties)
    bpy.types.GreasePencilLayers.floor_property = bpy.props.PointerProperty(type = FloorPointerProperties)


def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class) 
    
    del bpy.types.Scene.dm_property
    del bpy.types.Object.player_property
    del bpy.types.GreasePencil.map_property
    del bpy.types.GreasePencilLayers.floor_property
#endregion Properties