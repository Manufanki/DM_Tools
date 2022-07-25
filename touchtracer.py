'''
Touch Tracer Line Drawing Demonstration
=======================================

This demonstrates tracking each touch registered to a device. You should
see a basic background image. When you press and hold the mouse, you
should see cross-hairs with the coordinates written next to them. As
you drag, it leaves a trail. Additional information, like pressure,
will be shown if they are in your device's touch.profile.

.. note::

   A function `calculate_points` handling the points which will be drawn
   has by default implemented a delay of 5 steps. To get more precise visual
   results lower the value of the optional keyword argument `steps`.

This program specifies an icon, the file icon.png, in its App subclass.
It also uses the particle.png file as the source for drawing the trails which
are white on transparent. The file touchtracer.kv describes the application.

The file android.txt is used to package the application for use with the
Kivy Launcher Android application. For Android devices, you can
copy/paste this directory into /sdcard/kivy/touchtracer on your Android device.

'''
__version__ = '1.0'

from doctest import FAIL_FAST
from time import sleep
import bpy

import kivy
import numpy as np

kivy.require('1.0.6')
from kivy.config import Config

Config.set('graphics', 'maxfps', '30')
#Config.set('input', 'mouse', 'mouse,disable_on_activity')
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Point, GraphicException
from kivy.metrics import dp
from kivy.lang import Builder

from bpy_extras import view3d_utils
from mathutils import Vector

import win32gui
import win32con
import win32api
import winxpgui

from random import random
from math import dist, fabs, sqrt

import threading
import bpy
from random import randint
import queue



execution_queue = queue.Queue()


class TouchThread(threading.Thread):
    thread_is_alive = False
    touch_active = False
    def __init__(self,port):
         super(TouchThread, self).__init__()
         self.port=port
    
    def stop(self):
        print("stop")
        TouchtracerApp().stop()
 
    def run(self):
        self.thread_is_alive = True
        TouchtracerApp().run()
        self.join()
 
touchInput = TouchThread(8000)

def execute_queued_functions():
    window = bpy.context.window_manager.windows[0]
    ctx = {'window': window, 'screen': window.screen}  
    
    #print(threading.current_thread().name, "timer consuming queue")
    while not execution_queue.empty():
        function = execution_queue.get()        
        print(threading.current_thread().name, "function found name:", function)
        function(ctx)
    return 1.0


def calculate_points(x1, y1, x2, y2, steps=5):
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt(dx * dx + dy * dy)
    if dist < steps:
        return
    o = []
    m = dist / steps
    for i in range(1, int(m)):
        mi = i / m
        lastx = x1 + dx * mi
        lasty = y1 + dy * mi
        o.extend([lastx, lasty])
    return o

def adjust_windows():
    window = win32gui.FindWindow(None, "Touchtracer")
    alpha = 100
    if window == 0:
        return
    if bpy.context.scene.dm_property.adjust_windows == True:
        alpha = 2


    win32gui.SetWindowLong (window, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (window, win32con.GWL_EXSTYLE ) | win32con.WS_EX_LAYERED )
    winxpgui.SetLayeredWindowAttributes(window, win32api.RGB(0,0,0), alpha, win32con.LWA_ALPHA)

    return
    blender_window = win32gui.FindWindow(None, "Blender")
    if window == 0 or blender_window == 0:
        return 
    x,y,w,h = get_window_rect(window)
    a,b,c,d = get_window_rect(blender_window)

    if a != x or b != y or c != w or d != h:
        win32gui.SetWindowPos(blender_window,win32con.HWND_TOP, x, y, w, h, 0) 

def get_window_rect(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    print("Window %s:" % win32gui.GetWindowText(hwnd))
    print("\tLocation: (%d, %d)" % (x, y))
    print("\t    Size: (%d, %d)" % (w, h))
    return x,y,w,h

class Touchtracer(FloatLayout):

    def normalize_pressure(self, pressure):
        #print(pressure)
        # this might mean we are on a device whose pressure value is
        # incorrectly reported by SDL2, like recent iOS devices.
        if pressure == 0.0:
            return 1
        return dp(pressure * 10)

    def on_touch_down(self, touch):

        #bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(touch.x, touch.y, 0), scale=(1, 1, 1))

        win = self.get_parent_window()
        ud = touch.ud
        ud['group'] = g = str(touch.uid)
        pointsize = 5
    
        if isinstance(touch.id, int):
            touch_pos = Vector((int(touch.x), int(touch.y)))
            set_touch_id(self, bpy.context,touch.id, touch_pos)


        if 'pressure' in touch.profile:
            ud['pressure'] = touch.pressure
            pointsize = self.normalize_pressure(touch.pressure)
        ud['color'] = random()

        with self.canvas:
            Color(ud['color'], 1, 1, mode='hsv', group=g)
            ud['lines'] = [
                Rectangle(pos=(touch.x, 0), size=(1, win.height), group=g),
                Rectangle(pos=(0, touch.y), size=(win.width, 1), group=g),
                Point(points=(touch.x, touch.y), source='particle.png',
                      pointsize=pointsize, group=g)]

        ud['label'] = Label(size_hint=(None, None))
        self.update_touch_label(ud['label'], touch)
        self.add_widget(ud['label'])
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        ud = touch.ud
        ud['lines'][0].pos = touch.x, 0
        ud['lines'][1].pos = 0, touch.y

        if isinstance(touch.id, int):
            for char in bpy.context.scene.dm_property.characterlist:
                if char.character.player_property.touch_id == touch.id:
                    touch_pos = Vector((int(touch.x), int(touch.y)))
                    update_player_pos(self, bpy.context,touch.id, touch_pos)



        index = -1

        while True:
            try:
                points = ud['lines'][index].points
                oldx, oldy = points[-2], points[-1]
                break
            except IndexError:
                index -= 1

        points = calculate_points(oldx, oldy, touch.x, touch.y)

        # if pressure changed create a new point instruction
        if 'pressure' in ud:
            old_pressure = ud['pressure']
            if (
                not old_pressure
                or not .99 < (touch.pressure / old_pressure) < 1.01
            ):
                g = ud['group']
                pointsize = self.normalize_pressure(touch.pressure)
                with self.canvas:
                    Color(ud['color'], 1, 1, mode='hsv', group=g)
                    ud['lines'].append(
                        Point(points=(), source='particle.png',
                              pointsize=pointsize, group=g))

        if points:
            try:
                lp = ud['lines'][-1].add_point
                for idx in range(0, len(points), 2):
                    lp(points[idx], points[idx + 1])
            except GraphicException:
                pass

        ud['label'].pos = touch.pos
        import time
        t = int(time.time())
        if t not in ud:
            ud[t] = 1
        else:
            ud[t] += 1
        self.update_touch_label(ud['label'], touch)

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)   
            
        ud = touch.ud
        self.canvas.remove_group(ud['group'])
        self.remove_widget(ud['label'])

    def update_touch_label(self, label, touch):
        label.text = 'ID: %s\nPos: (%d, %d)\nClass: %s' % (
            touch.id, touch.x, touch.y, touch.__class__.__name__)
        label.texture_update()
        label.pos = touch.pos
        label.size = label.texture_size[0] + 20, label.texture_size[1] + 20

class TouchtracerApp(App):
    title = 'Touchtracer'
    icon = 'icon.png'

    def on_start(self):
        window = win32gui.FindWindow(None, "Touchtracer")
        blender_window = win32gui.FindWindow(None, "Blender")
        x,y,w,h = get_window_rect(blender_window)
        win32gui.SetWindowLong (window, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (window, win32con.GWL_EXSTYLE ) | win32con.WS_EX_LAYERED )
        winxpgui.SetLayeredWindowAttributes(window, win32api.RGB(0,0,0), 100, win32con.LWA_ALPHA)
        win32gui.SetWindowPos(window, win32con.HWND_TOPMOST, x, y, w, h, 0) 

       
    def build(self):
        Clock.schedule_interval(lambda dt: print("running"), 1)
        Clock.schedule_interval(lambda dt: adjust_windows(), 1)
        return Touchtracer()

    def on_pause(self):
        return True


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    if np.dot(Vector((1,0,0)),v2_u) < 0:
        return angle
    else:
        return -angle

def set_touch_id(self, context,id,touch_pos):
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
            if d < 5 and d < distance:
                distance = d
                player_index = index
        if player_index != -1:
                dm_property.characterlist[player_index].character.player_property.touch_id = id

def update_player_pos(self, context,id,touch_pos):

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
    
    def execute(self, context):
        if not touchInput.isDaemon:
            touchInput.setDaemon(True)
        
        if touchInput.is_alive() == False:
            touchInput.touch_active = True
            touchInput.start()

            
        else:
            if touchInput.is_alive(): 
                touchInput.touch_active = True
        




       
        return {'FINISHED'}



#classes = (TOUCH_OT_move)


def register():
    bpy.app.timers.register(execute_queued_functions)
    bpy.utils.register_class(TOUCH_OT_move)
    # for c in classes:
    #     bpy.utils.register_class(c)


def unregister():
    bpy.app.timers.unregister(execute_queued_functions)
    bpy.utils.unregister_class(TOUCH_OT_move)
    # for c in reversed(classes):
    #     bpy.utils.unregister_class(c)

