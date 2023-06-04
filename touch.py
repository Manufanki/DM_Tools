import os
import copy
import cmath
from time import time
import pygame as pg
from pygame._sdl2 import touch
import numpy as np
import math

from bpy_extras import view3d_utils
from mathutils import Vector


import win32gui
import win32con
import win32api
import winxpgui

from random import random
from math import dist, fabs, sqrt

import bpy
from random import randint


# This makes the touchpad be usable as a multi touch device.
os.environ['SDL_MOUSE_TOUCH_EVENTS'] = '1'

def get_window_rect(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    return x,y,w,h


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    if np.linalg.norm(vector) == 0:
        return vector
    
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
    if np.dot(Vector((1,0,0)),v2_u) < 0:
        return angle
    else:
        return -angle


def ground_objects(context):
    """Loop over (object, matrix) pairs (mesh only)"""
    index = -1

    for ground in context.scene.dm_property.groundlist:
        index += 1
        if ground.obj is None or context.scene.objects.get(ground.obj.name) is None:
            context.scene.dm_property.groundlist.remove(index)
            continue
        if ground.obj.visible_get():
            yield (ground.obj, ground.obj.matrix_world.copy())


def obj_ray_cast(obj, matrix,ray_origin,ray_target):
    """Wrapper for ray casting that moves the ray into object space"""
    # get the ray relative to the object
    matrix_inv = matrix.inverted()
    ray_origin_obj = matrix_inv @ ray_origin
    ray_target_obj = matrix_inv @ ray_target
    ray_direction_obj = ray_target_obj - ray_origin_obj

    # cast the ray
    try:
        success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

        if success:
            return location, normal, face_index
        else:
            return None, None, None
    except:
        return None, None, None


def get_ray_target(context,touch_pos):
    dm_property = context.scene.dm_property
    area =  dm_property.screen.areas[0]
    region = None
    rv3d = None
    for reg in area.regions:
        if reg.type == 'WINDOW':
            region = reg
            rv3d = reg.data

    if region is None or rv3d is None:
        return
    coord = touch_pos

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    return ray_origin , view_vector

def raycast_screen_to_world(context, ray_origin,ray_target):
    best_length_squared = -1.0
    best_hit_world = None
    for obj, matrix in ground_objects(context):
        if obj.type == 'MESH':
            hit, normal, face_index = obj_ray_cast(obj, matrix,ray_origin, ray_target)
            if hit is None:
                continue
            hit_world = matrix @ hit
            length_squared = (hit_world - ray_origin).length_squared
            if best_hit_world is None or length_squared < best_length_squared:
                best_length_squared = length_squared
                best_hit_world = hit_world
    return best_hit_world

def set_touch_id( context,id,touch_pos, time):
    """On Touch Down, a touch id is given, the touch can belong to a character or navigation"""
    # get the context arguments

    
    touch_pos = Vector((touch_pos[0], touch_pos[1]))
    
    dm_property = context.scene.dm_property

    ray_origin , view_vector = get_ray_target(context, touch_pos)

    ray_target = ray_origin + view_vector
    hit_world = raycast_screen_to_world(context,ray_origin, ray_target)
    if hit_world is not None:
        distance = 1000
        player_index = -1
        index = -1

        #Find closest player
        for char in dm_property.characterlist:
            index += 1
            if char.obj.player_property.is_npc:
                continue

           
            hit_world_XY = hit_world
            hit_world_XY[2] = 0
            char_loc_XY = copy.deepcopy(char.obj.location)
            char_loc_XY[2] = 0

            # place character inside circle
            if not char.obj.player_property.distance_sphere.hide_get():
                for touch in dm_property.player_touchlist:
                    d = np.linalg.norm(hit_world-char.obj.player_property.distance_sphere.location)
                    if d <= char.obj.player_property.move_distance + 1 and touch.player_id == char.obj.player_property.player_id:  
                        touch.finger_id = id
                        touch.start_time = time
                        touch.touch_start[0] = int(touch_pos[0])
                        touch.touch_start[1] = int(touch_pos[1])        
                        touch.touch_pos[0] = int(touch_pos[0])
                        touch.touch_pos[1] = int(touch_pos[1])

                        char.obj.location = hit_world
                        char.obj.player_property.distance_toggle = not char.obj.player_property.distance_toggle
                        add_touch_to_list(dm_property.touchlist,id, time,touch_pos, char.obj.player_property.player_id)
                        char.obj.player_property.touch_id = id
                        return 


            d = np.linalg.norm(hit_world_XY-char_loc_XY)
            #print(char.obj.name,"DIST:",d)
            if d < 1 and d < distance:
                if char.obj.player_property.touch_id <= -1:
                    distance = d
                    player_index = index
        if player_index > -1:  #Player was found
            char = dm_property.characterlist[player_index]
            char.obj.player_property.touch_id = id
            
            #update player touch for this character
            for touch in dm_property.player_touchlist:
                if touch.player_id == char.obj.player_property.player_id:
                    if time -touch.start_time < .2:
                        # if dm_property.use_round_order:
                        #     bpy.ops.next.round()
                        # else:
                        char.obj.player_property.distance_toggle = not char.obj.player_property.distance_toggle

                    touch.finger_id = id
                    touch.start_time = time
                    touch.touch_start[0] = int(touch_pos[0])
                    touch.touch_start[1] = int(touch_pos[1])        
                    touch.touch_pos[0] = int(touch_pos[0])
                    touch.touch_pos[1] = int(touch_pos[1])
                    return True
            #if no touch is found add a new touch
            add_touch_to_list(dm_property.touchlist,id, time,touch_pos, char.obj.player_property.player_id)
            add_touch_to_list(dm_property.player_touchlist,id, time,touch_pos, char.obj.player_property.player_id)
            return
    #player was not found = navigational Touch

    dm_property.zoom_value_backup = dm_property.camera_zoom
    dm_property.zoom_value = dm_property.camera_zoom
    add_touch_to_list(dm_property.touchlist,id, time,touch_pos)
    add_touch_to_list(dm_property.nav_touchlist,id, time,touch_pos)
    

    
    


def add_touch_to_list(list, id, time, touch_pos, player_id = -1):
    touch_pointer = list.add()
    touch_pointer.player_id = player_id
    touch_pointer.finger_id = id
    touch_pointer.start_time = time
    touch_pointer.touch_start[0] = int(touch_pos[0])
    touch_pointer.touch_start[1] = int(touch_pos[1])        
    touch_pointer.touch_pos[0] = int(touch_pos[0])
    touch_pointer.touch_pos[1] = int(touch_pos[1])

def remove_touch_from_list(list,finger_id):
    index = 0
    for touch in list:
        if touch.finger_id == finger_id:
            list.remove(index)
            break
        index += 1


def get_touch_from_list(list, finger_id):
    for touch in list:
        if touch.finger_id == finger_id:
            return touch
def clear_touch_id(dm_property):
     for char in dm_property.characterlist:
                char.obj.player_property.touch_id = -1

def update_player_pos(self,context,id,touch_pos):

    dm_property = context.scene.dm_property

    # for touch in dm_property.player_touchlist:
    #     if touch.finger_id == id:
    #         if time - touch.start_time < 2:
    #             return  


    touch_pos = Vector((touch_pos[0], touch_pos[1]))
    area =  dm_property.screen.areas[0]
    region = None
    rv3d = None
    for reg in area.regions:
        if reg.type == 'WINDOW':
            region = reg
            rv3d = reg.data

    if region is None or rv3d is None:
        return
    coord = touch_pos

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + view_vector

    best_length_squared = -1.0
    best_hit_world = None

    for obj, matrix in ground_objects(context):
        if obj.type == 'MESH':
            hit, normal, face_index = obj_ray_cast(obj, matrix,ray_origin, ray_target)
            if hit is None:
                continue
            hit_world = matrix @ hit
            length_squared = (hit_world - ray_origin).length_squared
            if best_hit_world is None or length_squared < best_length_squared:
                best_length_squared = length_squared
                best_hit_world = hit_world
    if best_hit_world is None:
        return

    for char in dm_property.characterlist:
        if char.obj.player_property.touch_id == id:
            if char.obj.player_property.player_coll.hide_viewport:
                return
            if(dm_property.use_round_order and dm_property.active_character != char.obj):
                return

            loc_buffer_size = 1
            rot_buffer_size = 10

            last_touch_pos = char.obj.player_property.touch_pos
            last_touch_pos = Vector((last_touch_pos[0], last_touch_pos[1]))

            #Average Position           
            if len(char.obj.player_property.positionlist) > loc_buffer_size:
                char.obj.player_property.positionlist.remove(0)
    
            saved_pos = char.obj.player_property.positionlist.add()
            saved_pos.value = best_hit_world
            sum = Vector((0,0,0))
            for p in char.obj.player_property.positionlist:
                    sum[0] += p.value[0]
                    sum[1] += p.value[1] 
                    sum[2] += p.value[2]  
                    #print("POS: ", sum) 
            
            count = len(char.obj.player_property.positionlist)
            avrPos = Vector((sum[0] / count,sum[1] / count,sum[2] / count)) 

            #keep distance between players
            for charloc in dm_property.characterlist:
                p = charloc.obj.location
                if np.linalg.norm(best_hit_world-p) < 1.5 and char != charloc:
                    return
            #set Position
            char.obj.location = avrPos

            dir = best_hit_world - avrPos #char.obj.location 
            
            #calculate direction
            touch_distance = np.linalg.norm(dir)
            forward = Vector((0,1,0))
            if touch_distance > 0:
                rot = angle_between(forward, dir)
                #rot = round(rot / math.pi *4) *(math.pi /4)

                #Avarage Rotation
                if len(char.obj.player_property.rotationlist) > rot_buffer_size:
                    char.obj.player_property.rotationlist.remove(0)
      
                saved_rot = char.obj.player_property.rotationlist.add()
                saved_rot.value = float(rot)
                sum_x = 0
                sum_y = 0
                for r in char.obj.player_property.rotationlist:
                    x,y = math.cos(r.value), math.sin(r.value)
                    sum_x += x
                    sum_y += y 
                    #print("SIN: ",math.sin(r.value)) 

                mean_x = sum_x / len(char.obj.player_property.rotationlist)
                mean_y = sum_y / len(char.obj.player_property.rotationlist)

                mean = complex(mean_x, mean_y)
                mean = cmath.phase(mean)
                #print("RESULT: ",mean) 
                char.obj.rotation_euler[2] = mean
            char.obj.player_property.touch_pos[0] = int(touch_pos[0])
            char.obj.player_property.touch_pos[1] = int(touch_pos[1])
            return




def update_camera_pos(self,context,id,touch_pos):

        dm_property = context.scene.dm_property

        if dm_property.touch_navigation == False:
            return

        touchlist = dm_property.nav_touchlist

    
        if len(touchlist) < 2:
            return   

        if touchlist[0].finger_id == id:
            touchlist[0].touch_pos[0] = int(touch_pos[0])
            touchlist[0].touch_pos[1] = int(touch_pos[1])
            return
        
 
        if  touchlist[1].zoom_value == 0:
            touch0_start = touchlist[0].touch_start
            touch0_start = Vector((touch0_start[0], touch0_start[1]))

            touch1_start = touchlist[1].touch_start
            touch1_start = Vector((touch1_start[0], touch1_start[1]))

            touchlist[1].zoom_value = float(np.linalg.norm(touch1_start - touch0_start))

        touch0_pos = touchlist[0].touch_pos
        touch0_pos = Vector((touch0_pos[0], touch0_pos[1]))

        touch1_pos = touchlist[1].touch_pos
        touch1_pos = Vector((touch1_pos[0], touch1_pos[1]))

        zoomvalue = float(np.linalg.norm(touch1_pos - touch0_pos))

        new_zoom_value =  zoomvalue - touchlist[1].zoom_value
        touchlist[1].zoom_value = zoomvalue
        new_zoom_value = new_zoom_value *0.15

        dm_property.zoom_value += new_zoom_value

        threshold = 5
        if abs(dm_property.zoom_value_backup - dm_property.zoom_value) > threshold:
            if dm_property.zoom_value < dm_property.zoom_value_backup :
                threshold = -threshold
            dm_property.camera_zoom = dm_property.zoom_value - threshold
            for char in dm_property.characterlist:
                char.obj.player_property.touch_id = -1
        else:
            last_touch_pos = touchlist[1].touch_pos
            last_touch_pos = Vector((last_touch_pos[0], last_touch_pos[1]))
            #touch_distance = np.linalg.norm(touch_pos - last_touch_pos)

            x = dm_property.camera_zoom * .01
            a = 10
            speed =  (-a*pow(x,.025) + a+.1) *0.1
            print("Speed: ",speed)
            
            #result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph,ray_origin_mouse, direction)
            dm_property.camera.location[0] +=  (last_touch_pos[0] - touch_pos[0]) * speed
            dm_property.camera.location[1] +=  (last_touch_pos[1] - touch_pos[1]) * speed

   
            touchlist[1].touch_pos[0] = int(touch_pos[0])
            touchlist[1].touch_pos[1] = int(touch_pos[1])

def cancel_programm(dm_property):
    dm_property.touch_active = False 
    clear_touch_id(dm_property)
    dm_property.touch_device_id = -1


def update_touch_input(self,dm_property):
      #Searching the right touch device
        if dm_property.touch_device_id == -1:
            num_touch_dev = touch.get_num_devices()
            for index in range(0,num_touch_dev):     
                try:
                    touch_id = touch.get_device(index)
                    num_touch_ids = touch.get_num_fingers(touch_id)
                    for i in range(0,num_touch_ids):
                        e = touch.get_finger(touch_id,i)
                        if e is not None:
                            dm_property.touch_device_id = touch_id
                except Exception as e:
                    #continue
                    print(e)
        else:
            try:
                #Updating Player Posision when they do not move
                touch_id = dm_property.touch_device_id
                num_touch_ids = touch.get_num_fingers(touch_id)
                move_cam = False
                for i in range(0,num_touch_ids):
                    e = touch.get_finger(touch_id,i)    
                    if e is not None:
                        touch_pos = Vector((int(self.width * e['x']), int(self.height-(self.height * e['y']))))
                        # if  move_camera_at_boarderts(self,touch_pos, dm_property):
                        #     move_cam = True
                if not move_cam:
                    return

                for i in range(0,num_touch_ids):
                    e = touch.get_finger(touch_id,i)
                    
                    if e is not None:
                        touch_pos = Vector((int(self.width * e['x']), int(self.height-(self.height * e['y']))))
                        for char in bpy.context.scene.dm_property.characterlist:
                            if char.obj.player_property.touch_id == e['id']:
                                update_player_pos(self,bpy.context,e['id'], touch_pos)
                                break
                    
            except Exception as e:
                print(e)
                dm_property.touch_device_id = -1

            pg.display.flip()
    


class TOUCH_OT_move(bpy.types.Operator):
    "Creates a Update loop and checks for Touch input"
    bl_idname = "touch.move"
    bl_label = "move players"
    
    _timer = None
    width, height = 0,0
    hwnd_touch = 0
    time = 0

    #First Execution
    def execute(self, context):
        dm_property = context.scene.dm_property

        # len_touch = len(dm_property.touchlist)
        # for i in range(0,len_touch+1):
        dm_property.touchlist.clear()
        dm_property.player_touchlist.clear()
        dm_property.nav_touchlist.clear()
        # len_pl_touch = len(dm_property.player_touchlist)
        # for i in range(0,len_pl_touch+1):
        #    dm_property.player_touchlist.remove(i)
        
        dm_property.touch_active = not dm_property.touch_active
        wm = context.window_manager
        self._timer = wm.event_timer_add(1/context.scene.dm_property.touch_update_rate, window=context.window)
        wm.modal_handler_add(self)

        area =  dm_property.screen.areas[0]
        region = None
        for reg in area.regions:
            if reg.type == 'WINDOW':
                region = reg

        pg.init()    
        self.width, self.height = (region.width, region.height)
        screen = pg.display.set_mode((self.width, self.height),pg.NOFRAME)


        # a = mixer.Sound("D:\OneDrive\Musik\Weather System Sounds\Ambience\Ambience.mp3")
        # a.play(-1)
        # w = mixer.Sound("D:\OneDrive\Musik\Weather System Sounds\Wind\Stormy Wind 1.wav")
        # w.play(-1)
        caption = 'Touch'
        pg.display.set_caption(caption)
        
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

        self.hwnd_touch = pg.display.get_wm_info()["window"]

        return {'RUNNING_MODAL'}

    #Update
    def modal(self, context, event):
        
        dm_property = context.scene.dm_property

        if dm_property.touch_active == False:
            print("EXIT TOUCH BY Property")
            cancel_programm(dm_property)
            pg.quit()
            self.cancel(context)
            return {'CANCELLED'}

        self.time += 1/context.scene.dm_property.touch_update_rate

        hwnd_blender = dm_property.hwnd_id
      
        alpha = 1 # if pygame window is complete transparent it will not recieve touch input 
        
        try:
            x,y,w,h = get_window_rect(self.hwnd_touch)
            x1,y1,w1,h1 = get_window_rect(hwnd_blender)
        except Exception as e:
            cancel_programm(dm_property)
            print("EXIT TOUCH BY Window Closed")
            dm_property.hwnd_id = -1
            pg.quit()
            self.cancel(context)
            return {'CANCELLED'}
        
        y1 = y1-(h -h1) -7 

        x1 = x1 + 7
        try:
            win32gui.SetWindowLong (self.hwnd_touch, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (self.hwnd_touch, win32con.GWL_EXSTYLE ) | win32con.WS_EX_LAYERED )
            winxpgui.SetLayeredWindowAttributes(self.hwnd_touch, win32api.RGB(0,0,0), alpha, win32con.LWA_ALPHA)
            win32gui.SetWindowPos(self.hwnd_touch, win32con.HWND_TOP, x1, y1, w, h, win32con.SWP_NOACTIVATE) 
        except Exception as e:
            print(e)
        width, height = self.width, self.height


        #Pygame Touch Events
        for e in pg.event.get():
            # We look for finger down, finger motion, and then finger up.
            if e.type == pg.FINGERDOWN:
                print("FINGERDOWN: ",e.finger_id)
                touch_pos = Vector((int(width * e.x), int(height-(height * e.y))))
                set_touch_id(bpy.context,e.finger_id, touch_pos, self.time)

                
                #print(f" Touch Id: {e.finger_id} touched at pos {touch_pos}")
            elif e.type == pg.FINGERMOTION:
                touch_pos = Vector((int(width * e.x), int(height-(height * e.y))))
                
                if get_touch_from_list(dm_property.player_touchlist,e.finger_id):
                    update_player_pos(self,context,e.finger_id, touch_pos)
                else:
                     #set_touch_id(bpy.context,e.finger_id, touch_pos, self.time)
                     update_camera_pos(self, bpy.context,e.finger_id, touch_pos)
            elif e.type == pg.FINGERUP:
                print("__FINGER_UP: ",e.finger_id)
                for char in dm_property.characterlist:
                    if char.obj.player_property.touch_id == e.finger_id:
                        distance = 10000
                        for charloc in dm_property.characterlist:
                            if char == charloc:
                                continue
                            d = np.linalg.norm(char.obj.location - charloc.obj.location)
                            if d < distance:
                                distance = d
                            #print(char.obj.name,charloc.obj.name,"DIST:",distance)
                        if distance > 0:
                            char.obj.player_property.touch_id = -1
                            char.obj.player_property.rotationlist.clear()
                        else:
                            char.obj.player_property.touch_id = abs(char.obj.player_property.touch_id) *-1
                        break

                remove_touch_from_list(dm_property.touchlist,e.finger_id)
                #remove_touch_from_list(dm_property.player_touchlist,e.finger_id)
                remove_touch_from_list(dm_property.nav_touchlist,e.finger_id)

                
        if dm_property.touch_navigation:
            update_touch_input(self,dm_property)
        pg.display.flip()

        return {'PASS_THROUGH'}
    


    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)



def register():
    bpy.utils.register_class(TOUCH_OT_move)
    # for c in classes:
    #     bpy.utils.register_class(c)


def unregister():
    bpy.utils.unregister_class(TOUCH_OT_move)
    # for c in reversed(classes):
    #     bpy.utils.unregister_class(c)




#Deprecated

def two_finger_slide_zoom(self,context,id,touch_pos):

        dm_property = context.scene.dm_property

        nav_touchlist = dm_property.touchlist
        index = 0

        if len(nav_touchlist) == 0:
            return
        
        index = -1
        i =  -1
        for touch in nav_touchlist:
            i +=1
            if touch.finger_id == id:
                index = i
                break
        
        if index == -1:
            return


        if index == 0:
            last_touch_pos = nav_touchlist[index].touch_pos
            last_touch_pos = Vector((last_touch_pos[0], last_touch_pos[1]))


            touch_distance = np.linalg.norm(touch_pos - last_touch_pos)

            speed = 0.025
            
            #result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph,ray_origin_mouse, direction)
            dm_property.camera.location[0] +=  (last_touch_pos[0] - touch_pos[0]) * speed
            dm_property.camera.location[1] +=  (last_touch_pos[1] - touch_pos[1]) * speed


        elif index == 1:


            if  nav_touchlist[1].zoom_value == 0:
                touch0_start = nav_touchlist[0].touch_start
                touch0_start = Vector((touch0_start[0], touch0_start[1]))

                touch1_start = nav_touchlist[1].touch_start
                touch1_start = Vector((touch1_start[0], touch1_start[1]))

                nav_touchlist[1].zoom_value = float(np.linalg.norm(touch1_start - touch0_start))

            touch0_pos = nav_touchlist[0].touch_pos
            touch0_pos = Vector((touch0_pos[0], touch0_pos[1]))

            touch1_pos = nav_touchlist[1].touch_pos
            touch1_pos = Vector((touch1_pos[0], touch1_pos[1]))

            zoomvalue = float(np.linalg.norm(touch1_pos - touch0_pos))

            new_zoom_value =  zoomvalue - nav_touchlist[1].zoom_value
            nav_touchlist[1].zoom_value = zoomvalue
            new_zoom_value = new_zoom_value *0.05
            print(new_zoom_value)


            dm_property.camera_zoom += new_zoom_value


            for char in dm_property.characterlist:
                char.obj.player_property.touch_id = -1

            

        try:
            dm_property.touchlist[index].touch_pos[0] = int(touch_pos[0])
            dm_property.touchlist[index].touch_pos[1] = int(touch_pos[1])
        except:
            print("")

def move_camera_at_boarderts(self, touch_pos, dm_property):

        x = dm_property.camera_zoom * .01
        a = 10
        speed =  (-a*pow(x,.025) + a+.1) * (1/dm_property.touch_update_rate *120)

        boarder_size = 20

        on_boarder = False
        if touch_pos[0] < (self.width/boarder_size):
            dm_property.camera.location[0] -=  speed
            on_boarder = True
        if touch_pos[0] > (self.width - self.width/boarder_size):
            dm_property.camera.location[0] +=  speed
            on_boarder = True
        if touch_pos[1] < (self.height/boarder_size):
            dm_property.camera.location[1] -=  speed
            on_boarder = True
        if touch_pos[1] > (self.height - self.height/boarder_size):
            dm_property.camera.location[1] +=  speed 
            on_boarder = True
        return on_boarder

