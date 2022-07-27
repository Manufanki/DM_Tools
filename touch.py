import os
import pygame as pg
import numpy as np

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


def adjust_windows():

    # windows = []
    # win32gui.EnumWindows(lambda hwnd, resultList: resultList.append(hwnd), windows)


    # for win in windows:
    #     if win32gui.GetWindowText(win).startswith('Blender '):
    #         win32gui.SetForegroundWindow(win)

    window = win32gui.FindWindow(None, "Touch")
    alpha = 100
    
    if window == 0:
        return

    x,y,w,h = get_window_rect(window)

    win32gui.SetWindowLong (window, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (window, win32con.GWL_EXSTYLE ) | win32con.WS_EX_LAYERED )
    winxpgui.SetLayeredWindowAttributes(window, win32api.RGB(0,0,0), alpha, win32con.LWA_ALPHA)
    win32gui.SetWindowPos(window, win32con.HWND_TOP, x, y, w, h, win32con.SWP_NOACTIVATE) 

    




def get_window_rect(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    # print("Window %s:" % win32gui.GetWindowText(hwnd))
    # print("\tLocation: (%d, %d)" % (x, y))
    # print("\t    Size: (%d, %d)" % (w, h))
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
        result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, ray_origin_mouse, direction)
        
        if result is None:
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
            if d < 5 and d < distance and char.character.player_property.touch_id == -1:
                distance = d
                player_index = index
        if player_index != -1:
                dm_property.characterlist[player_index].character.player_property.touch_id = id

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
        result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, ray_origin_mouse, direction)
        
        
        if result is None or obj is None:
            return

        for char in dm_property.characterlist:
            if obj == char.character:
                return  
        for char in dm_property.characterlist:
            if char.character.player_property.touch_id == id:
                
                dir = location - char.character.location 
                forward = Vector((0,1,0))
                char.character.rotation_euler[2] = angle_between(forward, dir)
                char.character.location = location


class TOUCH_OT_move(bpy.types.Operator):
    "Add Map Collection to the Scene"
    bl_idname = "touch.move"
    bl_label = "move players"
    
    _timer = None
    circles = {}

    def modal(self, context, event):

        dm_property = bpy.context.scene.dm_property
        area =  dm_property.screen.areas[0]
        region = None
        for reg in area.regions:
            if reg.type == 'WINDOW':
                region = reg

        
        pg.init()

        # Different colors for different fingers.
        colors = [
            'red', 'green', 'blue', 'cyan', 'magenta',
            'yellow', 'black', 'orange', 'purple', 'violet'
        ]
        available_colors = colors[:] + colors[:] # two copies for people with 12 fingers.
        # keyed by finger_id, and having dict as a value like this:
        # {
        #     'x': 20,
        #     'y': 20,
        #     'color': 'red',
        # }
    
        width, height = (region.width, region.height)
        screen = pg.display.set_mode((width, height))
        #clock = pg.time.Clock()
        caption = 'Touch'
        pg.display.set_caption(caption)
        adjust_windows()
        # we hide the mouse cursor and keep it inside the window.
        
        #print("INOUT GRABBED: ",pg.event.get_grab())
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

        if event.type == 'TIMER':
            for e in pg.event.get():
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_s:
                        print("KEY s")
                # We look for finger down, finger motion, and then finger up.
                if e.type == pg.FINGERDOWN:

                    touch_pos = Vector((int(width * e.x), int(height-(height * e.y))))
                    set_touch_id(bpy.context,e.finger_id, touch_pos)
                    print(f" Touch Id: {e.finger_id} touched at pos {touch_pos}")
                    self.circles[e.finger_id] = {
                        'color': available_colors.pop(),
                        'x': int(width * e.x),  # x and y are 0.0 to 1.0 in touch space.
                        'y': int(height * e.y), #     we translate to the screen pixels.
                    }
                elif e.type == pg.FINGERMOTION:
                    touch_pos = Vector((int(width * e.x), int(height-(height * e.y))))
                    for char in bpy.context.scene.dm_property.characterlist:
                        if char.character.player_property.touch_id == e.finger_id:
                            update_player_pos(bpy.context,e.finger_id, touch_pos)
                            print(touch_pos)
                    print(f" Touch Id: {e.finger_id} touched at pos {touch_pos}")
                    self.circles[e.finger_id].update({
                        'x': int(width * e.x),  # x and y are 0.0 to 1.0 in touch space.
                        'y': int(height * e.y), #     we translate to the screen pixels.
                    })
                elif e.type == pg.FINGERUP:
                    for char in dm_property.characterlist:
                        if char.character.player_property.touch_id == e.finger_id:
                            char.character.player_property.touch_id = -1
                    available_colors.append(self.circles[e.finger_id]['color'])
                    del self.circles[e.finger_id]
            pg.display.flip()

        if event.type in {'ESC'}:
            pg.quit()
            self.cancel(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
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



