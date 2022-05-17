# DM_Tools Blender Addon
v1.0 <br/>
A Blender Addon for Tabletop Games. DM_Tools allows the user to create maps, floors and environment in a simple way.  
What makes DM_Tools unique is the every player has their own field of view. The DM just opens doors or windows and Blenders realtime renderer calculates the view for each player.

# Player field of view
![biggif_example](/doc/field_of_view.gif) 
<br/>


You can set up the move distance for each player. A green circle shows the area where the player can move in one turn.
![biggif_example](/doc/walk_distance.gif) 
<br/>


There is also the possibility to change the light of the scnene. On daylight the players can see as far as the screen allows, but on night players are blind if they dont have nightvision or using a torch.

![biggif_example](/doc/day_night.gif) 
<br/>

# Create Maps
The addon gives the oportunity to add maps to your scene. Each map can consits of multiple floors. In this example the map shows a house with two floors.
If one player goes upstairs you can easyíly switch the floor. 
![biggif_example](/doc/floors.gif) 
<br/>

If you want to mark specific points on your floor, like traps or enemy locations you can use the annotation tool each floor has their own annotation layer and is automaticly activated with the floor.  
![biggif_example](/doc/annotations.gif) 
<br/>

You can store all your maps in one blend file and when the games switches to another locatiom you just have to select another map.   
![biggif_example](/doc/maps.gif) 
<br/>

# Installation
1. Download this repo as zip
2. open blender got to Edit -> Preferences -> Add-ons and press Install
3. Navigate to the zip select it and install add on
4. Search for "DM_Tools" and enable the add on
