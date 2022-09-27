import os
import re
from time import time
from traceback import print_tb
import pygame as pg
from pygame import _sdl2
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

def set_touch_id( context,id,touch_pos):
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
        view_vector_mouse = view3d_utils.region_2d_to_vector_3d(region, rv3d,touch_pos)# self.touch_pos)
        ray_origin_mouse = view3d_utils.region_2d_to_origin_3d(region, rv3d,touch_pos)# self.touch_pos)
        direction = ray_origin_mouse + (view_vector_mouse * 1000)
        direction =  direction - ray_origin_mouse

        for char in dm_property.characterlist:
            char.character.player_property.distance_sphere.hide_viewport = True 


        result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, ray_origin_mouse, direction)
        
        for char in dm_property.characterlist:
            char.character.player_property.distance_sphere.hide_viewport = False


        if result is None:
            dm_property.touch_pos[0] = int(touch_pos[0])
            dm_property.touch_pos[1] = int(touch_pos[1])
            print("FIRST TOUCH NAV")
            return
        dm_property = context.scene.dm_property


        distance = 1000
        player_index = -1
        index = -1
        for char in dm_property.characterlist:
            index += 1
            if obj == char.character:
                char.character.player_property.touch_id = id
                return
            d = np.linalg.norm(location-char.character.location)
            if d < 2 and d < distance and char.character.player_property.touch_id == -1:
                distance = d
                player_index = index
        if player_index != -1:
                dm_property.characterlist[player_index].character.player_property.touch_id = id
                return



        for touch in dm_property.touchlist:
            if touch.finger_id == id:
                return
        touch_pointer = dm_property.touchlist.add()
        touch_pointer.finger_id = id
        touch_pointer.touch_start[0] = int(touch_pos[0])
        touch_pointer.touch_start[1] = int(touch_pos[1])        
        touch_pointer.touch_pos[0] = int(touch_pos[0])
        touch_pointer.touch_pos[1] = int(touch_pos[1])
        print("FIRST TOUCH NAV")

def update_player_pos(context,id,touch_pos):

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

        view_vector_mouse = view3d_utils.region_2d_to_vector_3d(region, rv3d,touch_pos)# self.touch_pos)
        ray_origin_mouse = view3d_utils.region_2d_to_origin_3d(region, rv3d,touch_pos)# self.touch_pos)
        direction = ray_origin_mouse + (view_vector_mouse * 1000)
        direction =  direction - ray_origin_mouse
        
        for char in dm_property.characterlist:
            char.character.hide_viewport = True
            char.character.player_property.distance_sphere.hide_viewport = True 
        
        result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph,ray_origin_mouse, direction)
        
        for char in dm_property.characterlist:
            char.character.hide_viewport = False
            char.character.player_property.distance_sphere.hide_viewport = False
        
        if result is None or obj is None:
            return

        for char in dm_property.characterlist:
            if char.character.player_property.touch_id == id:

                last_touch_pos = char.character.player_property.touch_pos
                last_touch_pos = Vector((last_touch_pos[0], last_touch_pos[1]))

                touch_distance = np.linalg.norm(touch_pos - last_touch_pos)
                dir = location - char.character.location 
                forward = Vector((0,1,0))
                if touch_distance > 3:
                    rot = angle_between(forward, dir)
                    #rot = round(rot / math.pi *4) *(math.pi /4)
                    char.character.rotation_euler[2] = rot
                char.character.location = location
                char.character.player_property.touch_pos[0] = int(touch_pos[0])
                char.character.player_property.touch_pos[1] = int(touch_pos[1])



def update_camera_pos(context,id,touch_pos):

        dm_property = context.scene.dm_property

        touchlist = dm_property.touchlist
        index = 0

        if len(touchlist) == 0:
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


        if index == 0:
            last_touch_pos = touchlist[index].touch_pos
            last_touch_pos = Vector((last_touch_pos[0], last_touch_pos[1]))


            touch_distance = np.linalg.norm(touch_pos - last_touch_pos)

            speed = 0.025
            
            #result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph,ray_origin_mouse, direction)
            dm_property.camera.location[0] +=  (last_touch_pos[0] - touch_pos[0]) * speed
            dm_property.camera.location[1] +=  (last_touch_pos[1] - touch_pos[1]) * speed


        elif index == 1:


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
            new_zoom_value = new_zoom_value *0.05
            print(new_zoom_value)
            if dm_property.camera_zoom_toggle:
                dm_property.camera_zoom_in += new_zoom_value
            else:
                dm_property.camera_zoom_out += new_zoom_value

            for char in dm_property.characterlist:
                char.character.player_property.touch_id = -1

            

        try:
            dm_property.touchlist[index].touch_pos[0] = int(touch_pos[0])
            dm_property.touchlist[index].touch_pos[1] = int(touch_pos[1])
        except:
            print("")



             



class TOUCH_OT_move(bpy.types.Operator):
    "Creates a Update loop and checks for Touch input"
    bl_idname = "touch.move"
    bl_label = "move players"
    
    _timer = None

    def modal(self, context, event):
        
        dm_property = bpy.context.scene.dm_property

        if context.scene.dm_property.touch_active == False:
            print("EXIT TOUCH BY Property")
            pg.quit()
            self.cancel(context)
            return {'CANCELLED'}

        area =  dm_property.screen.areas[0]
        region = None
        for reg in area.regions:
            if reg.type == 'WINDOW':
                region = reg

        pg.init()    
        width, height = (region.width, region.height)
        screen = pg.display.set_mode((width, height),pg.NOFRAME)

        hwnd_touch = pg.display.get_wm_info()["window"]
        hwnd_blender = dm_property.hwnd_id
      
        alpha = 1 # if pygame window is complete transparent it will not recieve touch input 

        
        try:
            x,y,w,h = get_window_rect(hwnd_touch)
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
            win32gui.SetWindowLong (hwnd_touch, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (hwnd_touch, win32con.GWL_EXSTYLE ) | win32con.WS_EX_LAYERED )
            winxpgui.SetLayeredWindowAttributes(hwnd_touch, win32api.RGB(0,0,0), alpha, win32con.LWA_ALPHA)
            win32gui.SetWindowPos(hwnd_touch, win32con.HWND_TOP, x1, y1, w, h, win32con.SWP_NOACTIVATE) 
        except Exception as e:
            print(e)
        caption = 'Touch'
        pg.display.set_caption(caption)
        
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

        if event.type == 'TIMER':
            for e in pg.event.get():
                # We look for finger down, finger motion, and then finger up.
                if e.type == pg.FINGERDOWN:
                    touch_pos = Vector((int(width * e.x), int(height-(height * e.y))))
                    set_touch_id(bpy.context,e.finger_id, touch_pos)
                   
                    #print(f" Touch Id: {e.finger_id} touched at pos {touch_pos}")
                elif e.type == pg.FINGERMOTION:
                    touch_pos = Vector((int(width * e.x), int(height-(height * e.y))))
                    navigation_touch = True
                    for char in bpy.context.scene.dm_property.characterlist:
                        if char.character.player_property.touch_id == e.finger_id:
                            #update_player_pos(bpy.context,e.finger_id, touch_pos)
                            navigation_touch = False
                            break
                    if navigation_touch:
                        update_camera_pos(bpy.context,e.finger_id, touch_pos)
                elif e.type == pg.FINGERUP:
                    for char in dm_property.characterlist:
                        if char.character.player_property.touch_id == e.finger_id:
                            char.character.player_property.touch_id = -1

                    index = 0
                    for touch in dm_property.touchlist:
                        if touch.finger_id == e.finger_id:
                            break
                        index += 1
                    dm_property.touchlist.remove(index)
            

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
                        continue
                        #print(e)
            else:
                try:
                    touch_id = dm_property.touch_device_id
                    num_touch_ids = pg._sdl2.touch.get_num_fingers(touch_id)
                    for i in range(0,num_touch_ids):
                        e = pg._sdl2.touch.get_finger(touch_id,i)
                        
                        if e is not None:

                           #navigation_touch = True
                            touch_pos = Vector((int(width * e['x']), int(height-(height * e['y']))))
                            for char in bpy.context.scene.dm_property.characterlist:
                                if char.character.player_property.touch_id == e['id']:
                                    update_player_pos(bpy.context,e['id'], touch_pos)
                                    #navigation_touch = False
                                    break
                            # if navigation_touch:
                            #     update_camera_pos(bpy.context,e['id'], touch_pos)
                except Exception as e:
                    print(e)
                    #dm_property.touch_device_id = -1

            pg.display.flip()
    
        return {'PASS_THROUGH'}

    def execute(self, context):

        len_touch = len(context.scene.dm_property.touchlist)
        for i in range(0,len_touch+1):
           context.scene.dm_property.touchlist.remove(i)

        context.scene.dm_property.touch_active = not context.scene.dm_property.touch_active
        wm = context.window_manager
        self._timer = wm.event_timer_add(1/context.scene.dm_property.touch_update_rate, window=context.window)
        wm.modal_handler_add(self)
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



