import bpy

from . utils import *
#region Properties
class FloorPointerProperties(bpy.types.PropertyGroup):
    floor : bpy.props.PointerProperty(type=bpy.types.Collection)

class MapPointerProperties(bpy.types.PropertyGroup):
    map : bpy.props.PointerProperty(type=bpy.types.Collection)
    floorlist_data_index : bpy.props.IntProperty(
        update=selectFloor
    )
    floorlist : bpy.props.CollectionProperty(type = FloorPointerProperties)
    annotation : bpy.props.PointerProperty(type=bpy.types.GreasePencil)


class CharacterPointerProperties(bpy.types.PropertyGroup):
    character : bpy.props.PointerProperty(type=bpy.types.Object)

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
        distance += 1.5
        self.distance_circle.dimensions = (distance,distance,self.distance_circle.dimensions.z)

    def update_darkvision(self,context):
        unitinfo = GetCurrentUnits()
        unit_dist = self.darkvision
        distance = unit_to_bu(unit_dist,unitinfo[1])
        distance += 1.5
        self.spot_night.data.cutoff_distance = distance
        self.point_night.data.cutoff_distance = distance

    player_coll : bpy.props.PointerProperty(type= bpy.types.Collection)
    light_coll : bpy.props.PointerProperty(type= bpy.types.Collection)
    is_enemy : bpy.props.BoolProperty()
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
    )

    distance_circle : bpy.props.PointerProperty(type=bpy.types.Object)
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
    adjust_windows : bpy.props.BoolProperty()



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


def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class) 
#endregion Properties