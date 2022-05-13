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


    is_setup : bpy.props.BoolProperty(default=False)

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

blender_classes = [
    PlayerProperties,    
    FloorPointerProperties,
    MapPointerProperties,
    PlayerPointerProperties,
    EnemyProperties,
    EnemyPointerProperties,
    DMProperties
    ]
def register():
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)


def unregister():
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class) 
#endregion Properties