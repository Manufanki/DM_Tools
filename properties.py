import bpy

from . utils import *
#region Properties
class FloorPointerProperties(bpy.types.PropertyGroup):
    floor : bpy.props.PointerProperty(type=bpy.types.Collection)
    name : bpy.props.StringProperty(update =lambda s, c: update_collection_name(s, c, s.floor))
    annotation : bpy.props.PointerProperty(type=bpy.types.GreasePencil)
class MapPointerProperties(bpy.types.PropertyGroup):
    map : bpy.props.PointerProperty(type=bpy.types.Collection)
    name : bpy.props.StringProperty(update =lambda s, c: update_collection_name(s, c, s.map))
    floorlist_data_index : bpy.props.IntProperty(
        update=selectFloor
    )
    floorlist : bpy.props.CollectionProperty(type = FloorPointerProperties)
    annotation : bpy.props.PointerProperty(type=bpy.types.GreasePencil)


class CharacterPointerProperties(bpy.types.PropertyGroup):
    character : bpy.props.PointerProperty(type=bpy.types.Object)

class PlayerProperties(bpy.types.PropertyGroup):

    def update_touch_active(self, context):
        if self.is_npc:
            emit_node = self.player_material.node_tree.nodes.get('Principled BSDF')
            if self.touch_id != -1:
                emit_node.inputs[20].default_value = 300
            else:
                emit_node.inputs[20].default_value = 0
        else:
            emit_node = self.player_material.node_tree.nodes.get('Emission')
            if self.touch_id != -1:
                emit_node.inputs[1].default_value = 300
            else:
                emit_node.inputs[1].default_value = 1
    def update_player_height(self, context):
        self.spot_day.location[2] = self.player.location[2]+ self.player_height
        self.point_day.location[2] = self.player.location[2]+ self.player_height
        self.spot_night.location[2] = self.player.location[2]+ self.player_height
        self.point_night.location[2] = self.player.location[2]+  self.player_height
    
    def update_player_color(self, context):
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

    def update_darkvision(self,context):
        unitinfo = GetCurrentUnits()
        unit_dist = self.darkvision
        distance = unit_to_bu(unit_dist,unitinfo[1])
        distance += 1.5
        self.spot_night.data.cutoff_distance = distance
        self.point_night.data.cutoff_distance = distance

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

    touch_id : bpy.props.IntProperty(
        default = -1,
        update=update_touch_active
    )

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
        min=0,
        max=2,
        default= 1,
        update=update_player_height
    )
    list_index : bpy.props.IntProperty(
    name="index",
    description="index",
    default= 0,
    min=0,
    )


    strength : bpy.props.IntProperty(
    name="STR",
    description="STR",
    default= 0,
    min=0,
    )
    dexterity : bpy.props.IntProperty(
    name="DEX",
    description="DEX",
    default= 0,
    min=0,
    )
    constitution : bpy.props.IntProperty(
    name="CON",
    description="constitution",
    default= 0,
    min=0,
    )
    intelligence : bpy.props.IntProperty(
    name="INT",
    description="intelligence",
    default= 0,
    min=0,
    )
    wisdom : bpy.props.IntProperty(
    name="WIS",
    description="wisdom",
    default= 0,
    min=0,
    )
    charisma : bpy.props.IntProperty(
    name="CHA",
    description="charisma",
    default= 0,
    min=0,
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
    attack_bonus : bpy.props.IntProperty(
    name="attak_bonus",
    description="Bonus",
    default= 0,
    min=0,
    )
    player : bpy.props.PointerProperty(type=bpy.types.Object)

class DMProperties(bpy.types.PropertyGroup):


    is_setup : bpy.props.BoolProperty(default=False)

    characterlist_data_index : bpy.props.IntProperty(
        update=selectCharacter
    )
    characterlist : bpy.props.CollectionProperty(type = CharacterPointerProperties)

    maplist_data_index : bpy.props.IntProperty(
        update=selectMap
    )
    maplist : bpy.props.CollectionProperty(type = MapPointerProperties)
   
    camera :  bpy.props.PointerProperty(type=bpy.types.Object)
    camera_zoom_in : bpy.props.FloatProperty(
        default= 35,
        update=adjustCamera
    )
    camera_zoom_out : bpy.props.FloatProperty(
        default= 80,
        update=adjustCamera
    )
    camera_zoom_toggle : bpy.props.BoolProperty()
    camera_pan_toggle : bpy.props.BoolProperty()
    global_Sun : bpy.props.PointerProperty(type=bpy.types.SunLight)
    
    day_night :bpy.props.BoolProperty(
        update=toggleDayNight
    )

    cave_Mat : bpy.props.PointerProperty(type= bpy.types.Material)
    bf_wall_Mat : bpy.props.PointerProperty(type= bpy.types.Material)

    master_coll : bpy.props.PointerProperty(type= bpy.types.Collection)
    maps_coll : bpy.props.PointerProperty(type= bpy.types.Collection)

    screen : bpy.props.PointerProperty(type=bpy.types.Screen)
    hwnd_id : bpy.props.IntProperty()
    touchwindow_active : bpy.props.BoolProperty()
    touch_active : bpy.props.BoolProperty()
    touch_update_rate : bpy.props.FloatProperty(default=60,
    min= 1,
    max= 144)


blender_classes = [
    PlayerProperties,    
    FloorPointerProperties,
    MapPointerProperties,
    CharacterPointerProperties,
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