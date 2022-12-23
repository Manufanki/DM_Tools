import os
import re
import copy
import cmath
from textwrap import indent
from time import time
from traceback import print_tb
import pygame as pg
from pygame import _sdl2
from pygame._sdl2 import touch
from pygame import mixer
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

def set_touch_id( context,id,touch_pos, time):
    """Run this function on left mouse, execute the ray cast"""
    # get the context arguments
    touch_pos = Vector((touch_pos[0], touch_pos[1]))
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

            #context.scene.cursor.location = hit_world

            dm_property = context.scene.dm_property

            

            distance = 1000
            player_index = -1
            index = -1
            for char in dm_property.characterlist:
                index += 1
                if not char.obj.player_property.distance_sphere.hide_get():
                    for touch in dm_property.player_touchlist:
                        d = np.linalg.norm(hit_world-char.obj.location)
                        if d < char.obj.player_property.move_distance and touch.player_id == char.obj.player_property.player_id:  
                            touch.finger_id = id
                            touch.start_time = time
                            touch.touch_start[0] = int(touch_pos[0])
                            touch.touch_start[1] = int(touch_pos[1])        
                            touch.touch_pos[0] = int(touch_pos[0])
                            touch.touch_pos[1] = int(touch_pos[1])

                            char.obj.location = hit_world
                            char.obj.player_property.touch_pos[0] = int(touch_pos[0])
                            char.obj.player_property.touch_pos[1] = int(touch_pos[1])
                            bpy.context.view_layer.objects.active = char.obj
                            bpy.ops.player.distance_toggle()
                            char.obj.player_property.touch_id = id
                            return


                hit_world_XY = hit_world
                hit_world_XY[2] = 0
                char_loc_XY = copy.deepcopy(char.obj.location)
                char_loc_XY[2] = 0
                d = np.linalg.norm(hit_world_XY-char_loc_XY)
                if d < 2 and d < distance:# and char.obj.player_property.touch_id == -1:
                    distance = d
                    player_index = index
            if player_index != -1:
                char = dm_property.characterlist[player_index]
                char.obj.player_property.touch_id = id

                for touch in dm_property.player_touchlist:
                    if touch.player_id == char.obj.player_property.player_id:
                        if time -touch.start_time < .5:
                            bpy.context.view_layer.objects.active = char.obj
                            bpy.ops.player.distance_toggle()
                        
                        touch.finger_id = id
                        touch.start_time = time
                        touch.touch_start[0] = int(touch_pos[0])
                        touch.touch_start[1] = int(touch_pos[1])        
                        touch.touch_pos[0] = int(touch_pos[0])
                        touch.touch_pos[1] = int(touch_pos[1])
                        return
                add_touch_to_list(dm_property.player_touchlist,id, time,touch_pos, char.obj.player_property.player_id)
                return

    for touch in dm_property.touchlist:
        if touch.finger_id == id:
            return
    dm_property.zoom_value_backup = dm_property.camera_zoom
    dm_property.zoom_value = dm_property.camera_zoom
    add_touch_to_list(dm_property.touchlist,id, time,touch_pos)

    print("FIRST TOUCH NAV")


def add_touch_to_list(list, id, time, touch_pos, player_id = -1):
    touch_pointer = list.add()
    touch_pointer.player_id = player_id
    touch_pointer.finger_id = id
    touch_pointer.start_time = time
    touch_pointer.touch_start[0] = int(touch_pos[0])
    touch_pointer.touch_start[1] = int(touch_pos[1])        
    touch_pointer.touch_pos[0] = int(touch_pos[0])
    touch_pointer.touch_pos[1] = int(touch_pos[1])


def update_player_pos(context,id,touch_pos):

    touch_pos = Vector((touch_pos[0], touch_pos[1]))
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
            
            last_touch_pos = char.obj.player_property.touch_pos
            last_touch_pos = Vector((last_touch_pos[0], last_touch_pos[1]))

            #Pinch to zoom
            #last_touch_pos = Vector((char.obj.location[0], char.obj.location[1]))
            #touch_distance = np.linalg.norm(touch_pos - last_touch_pos)
            
            dir = best_hit_world - char.obj.location 
            #Slide to zoom
            touch_distance = np.linalg.norm(dir)
            
            forward = Vector((0,1,0))
            if touch_distance > 0:
                rot = angle_between(forward, dir)
                #rot = round(rot / math.pi *4) *(math.pi /4)

                buffer_size = 10
 
                if len(char.obj.player_property.rotationlist) > buffer_size:
                    char.obj.player_property.rotationlist.remove(0)
      
                saved_rot = char.obj.player_property.rotationlist.add()
                saved_rot.value = float(rot)
                



                sum_x = 0
                sum_y = 0
                for r in char.obj.player_property.rotationlist:
                    x,y = math.cos(r.value), math.sin(r.value)
                    sum_x += x
                    sum_y += y 
                    print("SIN: ",math.sin(r.value)) 

                mean_x = sum_x / buffer_size
                mean_y = sum_y / buffer_size

                mean = complex(mean_x, mean_y)
                mean = cmath.phase(mean)
                print("RESULT: ",mean) 
                char.obj.rotation_euler[2] = mean
            char.obj.location = best_hit_world
            char.obj.player_property.touch_pos[0] = int(touch_pos[0])
            char.obj.player_property.touch_pos[1] = int(touch_pos[1])



def update_camera_pos(self, context,id,touch_pos):

        dm_property = context.scene.dm_property

        touchlist = dm_property.touchlist
        index = 0

        if dm_property.touch_navigation == False:
            return

        if len(touchlist) < 2:
            return
        
        index = -1
        i =  -1
        for touch in touchlist:
            i +=1
            if touch.finger_id == id:
                index = i
                break
        
        if index == -1:
            return
        

        touch0_start = touchlist[0].touch_start
        touch0_start = Vector((touch0_start[0], touch0_start[1]))

        touch1_start = touchlist[1].touch_start
        touch1_start = Vector((touch1_start[0], touch1_start[1]))

        if  touchlist[1].zoom_value == 0:
            #touchlist[1].zoom_value = float(np.linalg.norm(touch1_start - touch0_start))
            touchlist[1].zoom_value = (touch0_start[1] + touch1_start[1]) /2

        
        if touch0_start[0] < (self.width/10) and touch1_start[0] < (self.width/10):

            touch0_pos = touchlist[0].touch_pos
            touch0_pos = Vector((touch0_pos[0], touch0_pos[1]))

            touch1_pos = touchlist[1].touch_pos
            touch1_pos = Vector((touch1_pos[0], touch1_pos[1]))



            #zoomvalue = float(np.linalg.norm(touch0_start - touch0_pos))
            zoomvalue = (touch0_pos[1] + touch1_pos[1]) /2
            new_zoom_value =  touchlist[1].zoom_value - zoomvalue  
           
            touchlist[1].zoom_value = zoomvalue
            new_zoom_value = new_zoom_value *0.075
            print(new_zoom_value)

            dm_property.zoom_value += new_zoom_value

            print( dm_property.zoom_value)


        threshold = 0
        if abs(dm_property.zoom_value_backup - dm_property.zoom_value) > threshold:
            if dm_property.zoom_value < dm_property.zoom_value_backup :
                threshold = -threshold
            dm_property.camera_zoom = dm_property.zoom_value - threshold
            for char in dm_property.characterlist:
                char.obj.player_property.touch_id = -1
        else:
            last_touch_pos = touchlist[index].touch_pos
            last_touch_pos = Vector((last_touch_pos[0], last_touch_pos[1]))
            #touch_distance = np.linalg.norm(touch_pos - last_touch_pos)

            x = dm_property.camera_zoom * .01
            a = 10
            speed =  (-a*pow(x,.025) + a+.1) *0.1
            print("Speed: ",speed)
            
            #result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph,ray_origin_mouse, direction)
            dm_property.camera.location[0] +=  (last_touch_pos[0] - touch_pos[0]) * speed
            dm_property.camera.location[1] +=  (last_touch_pos[1] - touch_pos[1]) * speed

            

        try:
            dm_property.touchlist[index].touch_pos[0] = int(touch_pos[0])
            dm_property.touchlist[index].touch_pos[1] = int(touch_pos[1])
        except Exception as e:
            print(e)



             



class TOUCH_OT_move(bpy.types.Operator):
    "Creates a Update loop and checks for Touch input"
    bl_idname = "touch.move"
    bl_label = "move players"
    
    _timer = None
    width, height = 0,0
    hwnd_touch = 0
    time = 0
    def modal(self, context, event):
        
        dm_property = bpy.context.scene.dm_property

        if context.scene.dm_property.touch_active == False:
            print("EXIT TOUCH BY Property")
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
            context.scene.dm_property.touch_active = False
            dm_property.hwnd_id = -1
            print("EXIT TOUCH BY Window Closed")
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

        for e in pg.event.get():
            # We look for finger down, finger motion, and then finger up.
            if e.type == pg.FINGERDOWN:
                touch_pos = Vector((int(width * e.x), int(height-(height * e.y))))
                set_touch_id(bpy.context,e.finger_id, touch_pos, self.time)

                
                #print(f" Touch Id: {e.finger_id} touched at pos {touch_pos}")
            elif e.type == pg.FINGERMOTION:
                touch_pos = Vector((int(width * e.x), int(height-(height * e.y))))
                navigation_touch = True
                for char in bpy.context.scene.dm_property.characterlist:
                    if char.obj.player_property.touch_id == e.finger_id:
                        #update_player_pos(bpy.context,e.finger_id, touch_pos)
                        navigation_touch = False
                        break
                if navigation_touch:
                    update_camera_pos(self, bpy.context,e.finger_id, touch_pos)
            elif e.type == pg.FINGERUP:
                for char in dm_property.characterlist:
                    if char.obj.player_property.touch_id == e.finger_id:
                        char.obj.player_property.touch_id = -1
                        char.obj.player_property.rotationlist.clear()

                index = 0
                for touch in dm_property.touchlist:
                    if touch.finger_id == e.finger_id:
                        break
                    index += 1
                dm_property.touchlist.remove(index)
        
        #Searching the right touch device
        if dm_property.touch_device_id == -1:
            num_touch_dev = pg._sdl2.touch.get_num_devices()
            for index in range(0,num_touch_dev):     
                try:
                    touch_id = pg._sdl2.touch.get_device(index)
                    num_touch_ids = pg._sdl2.touch.get_num_fingers(touch_id)
                    for i in range(0,num_touch_ids):
                        e = pg._sdl2.touch.get_finger(touch_id,i)
                        if e is not None:
                            dm_property.touch_device_id = touch_id
                except Exception as e:
                    #continue
                    print(e)
        else:
            try:
                #Updating Player Posision when they do not move
                touch_id = dm_property.touch_device_id
                num_touch_ids = pg._sdl2.touch.get_num_fingers(touch_id)
                for i in range(0,num_touch_ids):
                    e = pg._sdl2.touch.get_finger(touch_id,i)
                    
                    if e is not None:

                        #navigation_touch = True
                        touch_pos = Vector((int(width * e['x']), int(height-(height * e['y']))))
                        for char in bpy.context.scene.dm_property.characterlist:
                            if char.obj.player_property.touch_id == e['id']:
                                update_player_pos(bpy.context,e['id'], touch_pos)
                                #navigation_touch = False
                                break
                        # if navigation_touch:
                        #     update_camera_pos(bpy.context,e['id'], touch_pos)
            except Exception as e:
                print(e)
                dm_property.touch_device_id = -1

            pg.display.flip()
    
        return {'PASS_THROUGH'}

    def execute(self, context):
        dm_property = context.scene.dm_property

        len_touch = len(dm_property.touchlist)
        for i in range(0,len_touch+1):
           dm_property.touchlist.remove(i)

        len_touch = len(dm_property.player_touchlist)
        for i in range(0,len_touch+1):
           dm_property.player_touchlist.remove(i)
        
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



