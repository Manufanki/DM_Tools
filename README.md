# DM_Tools Blender Addon
v1.0 <br/>
A Blender addon for tabletop games. DM_Tools allows the user to easily create maps, floors and environments.  
What makes DM_Tools unique is that each player has their own field of view. The DM simply opens doors or windows and Blender's real-time renderer calculates the view for each player

# Player
Automaticly generated field of view for each player.

![biggif_example](/doc/field_of_view.gif) 
<br/>


You can set the movement distance for each player. A green circle indicates the area in which the player can move in one turn.
![biggif_example](/doc/walk_distance.gif) 
<br/>


There is also an option to change the lighting of the playing field. In daylight, players can see as far as the screen allows, but at night, players are blind unless they have darkvision or use a torch.

![biggif_example](/doc/day_night.gif) 
<br/>

# Create Maps
The addon offers the possibility to add maps to your scene. Each map can consist of several floors. In this example, the map shows a house with two floors.
When a player goes to the upper floor, you can easily change the floor. 
![biggif_example](/doc/floors.gif) 
<br/>

If you want to mark certain points on your floor, such as traps or enemy positions, you can use the annotation tool. Each floor has its own annotation layer and is automatically activated with the floor.
![biggif_example](/doc/annotations.gif) 
<br/>

You can save all your maps in a blend file and when the game moves to another location, you just have to select another map.   
![biggif_example](/doc/maps.gif) 
<br/>

# Installation
1. Download this repo as zip
2. open blender got to Edit -> Preferences -> Add-ons and press Install
3. Navigate to the zip select it and install add on
4. Search for "DM_Tools" and enable the add on
