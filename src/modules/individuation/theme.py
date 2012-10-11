#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import math
from dtk.ui.config import Config
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.iconview import IconView
from dtk.ui.label import Label
from dtk.ui.constant import COLOR_NAME_DICT
from dtk.ui.theme import ui_theme
from dtk.ui.draw import draw_window_frame, draw_pixbuf
from dtk.ui.utils import alpha_color_hex_to_cairo, get_optimum_pixbuf_from_file, cairo_disable_antialias, color_hex_to_cairo, cairo_state
import cairo
import gobject
import gtk

THEME_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "theme")
BACKGROUND_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "background")

class Theme(object):
    '''
    class docs
    '''
	
    def __init__(self, theme_file):
        '''
        init docs
        '''
        self.theme_file = theme_file
        self.config = Config(os.path.join(THEME_DIR, self.theme_file))
        self.config.load()
        self.name = self.config.get("theme", "name")
        self.color = self.config.get("window", "color")
        self.enable_gaussian = self.config.get("window", "enable_gaussian")
        self.enable_advanced_menu = self.config.get("window", "enable_advanced_menu")
        self.title = self.config.get("name", "zh_CN")
        self.system_wallpapers = map(lambda (k, v): k, self.config.config_parser.items("system_wallpaper"))
        self.user_wallpapers = map(lambda (k, v): k, self.config.config_parser.items("user_wallpaper"))

class ThemeView(ScrolledWindow):
    '''
    class docs
    '''
	
    def __init__(self, switch_setting_view):
        '''
        init docs
        '''
        ScrolledWindow.__init__(self, 0, 0)
        self.switch_setting_view = switch_setting_view
        self.themes = map(lambda theme_file: Theme(theme_file), 
                          filter(lambda theme_file: os.path.isfile(os.path.join(THEME_DIR, theme_file)) and theme_file.endswith("ini"), os.listdir(THEME_DIR)))
        self.label_padding_x = 10
        self.label_padding_y = 10
        
        self.theme_box = gtk.VBox()
        self.user_theme_label = Label("我的主题")
        self.user_theme_align = gtk.Alignment()
        self.user_theme_align.set(0.0, 0.5, 0, 0)
        self.user_theme_align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        self.user_theme_view = IconView()
        self.user_theme_view.draw_mask = self.draw_mask
        self.user_theme_scrolledwindow = ScrolledWindow()
        self.system_theme_label = Label("系统主题")
        self.system_theme_align = gtk.Alignment()
        self.system_theme_align.set(0.0, 0.5, 0, 0)
        self.system_theme_align.set_padding(self.label_padding_y, self.label_padding_y, self.label_padding_x, 0)
        self.system_theme_view = IconView()
        self.system_theme_view.draw_mask = self.draw_mask
        self.system_theme_scrolledwindow = ScrolledWindow()
        
        self.user_theme_align.add(self.user_theme_label)
        self.theme_box.pack_start(self.user_theme_align, False, False)
        self.user_theme_scrolledwindow.add_child(self.user_theme_view)
        self.theme_box.pack_start(self.user_theme_scrolledwindow, False, False)
        self.system_theme_align.add(self.system_theme_label)
        self.theme_box.pack_start(self.system_theme_align, False, False)
        self.system_theme_scrolledwindow.add_child(self.system_theme_view)
        self.theme_box.pack_start(self.system_theme_scrolledwindow, True, True)
        self.add_child(self.theme_box)
        
        self.user_theme_align.connect("expose-event", self.expose_label_align)
        self.system_theme_align.connect("expose-event", self.expose_label_align)
        
        self.init_theme_view()
        
    def init_theme_view(self):
        user_theme_items = map(lambda theme: ThemeItem(theme, self.switch_setting_view), self.themes)
        system_theme_items = map(lambda theme: ThemeItem(theme, self.switch_setting_view), self.themes)
        
        self.user_theme_view.add_items(user_theme_items)
        self.system_theme_view.add_items(system_theme_items)
        
    def expose_label_align(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        
        self.draw_mask(cr, rect.x, rect.y, rect.width, rect.height)
                
    def draw_mask(self, cr, x, y, w, h):
        '''
        Draw mask interface.
        
        @param cr: Cairo context.
        @param x: X coordiante of draw area.
        @param y: Y coordiante of draw area.
        @param w: Width of draw area.
        @param h: Height of draw area.
        '''
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
        
gobject.type_register(ThemeView)        

class ThemeItem(gobject.GObject):
    '''
    Icon item.
    '''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    ITEM_WIDTH = 220
    ITEM_HEIGHT = 180
    
    def __init__(self, theme, switch_setting_view):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)
        self.theme = theme
        self.switch_setting_view = switch_setting_view
        self.hover_flag = False
        self.highlight_flag = False
        self.pixbufs = []
        self.wallpaper_offset_x = 60
        self.wallpaper_offset_y = 20
        self.wallpaper_width = 120
        self.wallpaper_height = 75
        self.wallpaper_render_offset = 15
        self.wallpaper_frame_size = 4
        self.window_frame_padding_x = 40
        self.window_frame_padding_y = 120
        self.window_frame_width = 48
        self.window_frame_height = 48
        
    def emit_redraw_request(self):
        '''
        Emit `redraw-request` signal.
        
        This is IconView interface, you should implement it.
        '''
        self.emit("redraw-request")
        
    def get_width(self):
        '''
        Get item width.
        
        This is IconView interface, you should implement it.
        '''
        return self.ITEM_WIDTH
        
    def get_height(self):
        '''
        Get item height.
        
        This is IconView interface, you should implement it.
        '''
        return self.ITEM_HEIGHT
    
    def render(self, cr, rect):
        '''
        Render item.
        
        This is IconView interface, you should implement it.
        '''
        # Draw wallpapers.
        wallpaper_x = rect.x + self.wallpaper_offset_x
        wallpaper_y = rect.y + self.wallpaper_offset_y
        
        if self.pixbufs == []:
            user_wallpaper_files = map(lambda wallpaper_file: os.path.join(BACKGROUND_DIR, wallpaper_file), self.theme.user_wallpapers)
            system_wallpaper_files = map(lambda wallpaper_file: os.path.join(BACKGROUND_DIR, wallpaper_file), self.theme.system_wallpapers)
            
            for wallpaper_file in user_wallpaper_files + system_wallpaper_files[:3]:
                self.pixbufs.append(get_optimum_pixbuf_from_file(wallpaper_file, self.wallpaper_width, self.wallpaper_height))
                
        reflection_height = 23
        reflection_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.wallpaper_width + self.wallpaper_frame_size * 2 + 2, reflection_height)        
        reflection_surface_cr = gtk.gdk.CairoContext(cairo.Context(reflection_surface))
                
        with cairo_state(cr):
            if len(self.pixbufs) == 1:
                draw_pixbuf(cr, self.pixbufs[0], wallpaper_x, wallpaper_y)
            elif len(self.pixbufs) > 1:
                for (index, pixbuf) in enumerate(self.pixbufs):
                    wallpaper_draw_x = wallpaper_x - index * self.wallpaper_render_offset
                    wallpaper_draw_y = wallpaper_y + 3 * self.wallpaper_render_offset - (len(self.pixbufs) - index) * self.wallpaper_render_offset
                    
                    self.render_wallpaper(cr, pixbuf, wallpaper_draw_x, wallpaper_draw_y)
                    
                    if index == len(self.pixbufs) - 1:
                        self.render_wallpaper(reflection_surface_cr, 
                                              pixbuf, 
                                              self.wallpaper_frame_size + 1, 
                                              self.wallpaper_frame_size + 1,
                                              True)
                        
                        i = 0
                        while (i <= reflection_height):
                            with cairo_state(cr):
                                cr.rectangle(
                                    wallpaper_draw_x - self.wallpaper_frame_size - 1, 
                                    wallpaper_draw_y + self.wallpaper_height + self.wallpaper_frame_size + i,
                                    self.wallpaper_width + self.wallpaper_frame_size * 2 + 2,
                                    1)
                                cr.clip()
                                cr.set_source_surface(
                                    reflection_surface, 
                                    wallpaper_draw_x - self.wallpaper_frame_size - 1, 
                                    wallpaper_draw_y + self.wallpaper_frame_size + self.wallpaper_height
                                    )
                                cr.paint_with_alpha(1.0 - (math.sin(i * math.pi / 2 / reflection_height)))
                            i += 1    
        
        # Draw window frame.
        window_frame_x = rect.x + self.window_frame_padding_x
        window_frame_y = rect.y + self.window_frame_padding_y
        
        cr.set_source_rgba(*alpha_color_hex_to_cairo((COLOR_NAME_DICT[self.theme.color], 0.5)))
        cr.rectangle(window_frame_x + 1, window_frame_y, self.window_frame_width - 2, 1)
        cr.rectangle(window_frame_x, window_frame_y + 1, self.window_frame_width, self.window_frame_height - 2)
        cr.rectangle(window_frame_x + 1, window_frame_y + self.window_frame_height - 1, self.window_frame_width - 2, 1) 
        cr.fill()
        
        draw_window_frame(cr, window_frame_x, window_frame_y, self.window_frame_width, self.window_frame_height,
                          ui_theme.get_alpha_color("window_frame_outside_1"),
                          ui_theme.get_alpha_color("window_frame_outside_2"),
                          ui_theme.get_alpha_color("window_frame_outside_3"),
                          ui_theme.get_alpha_color("window_frame_inside_1"),
                          ui_theme.get_alpha_color("window_frame_inside_2"),
                          )
        
    def render_wallpaper(self, cr, pixbuf, wallpaper_draw_x, wallpaper_draw_y, reflection=False):    
        cr.set_source_rgba(1, 1, 1, 1)
        cr.rectangle(wallpaper_draw_x - self.wallpaper_frame_size,
                     wallpaper_draw_y - self.wallpaper_frame_size,
                     self.wallpaper_width + self.wallpaper_frame_size * 2,
                     self.wallpaper_height + self.wallpaper_frame_size * 2)
        cr.fill()
        
        with cairo_disable_antialias(cr):
            cr.set_line_width(1)
            cr.set_source_rgb(*color_hex_to_cairo("#A4A7A7"))
            
            cr.rectangle(wallpaper_draw_x - self.wallpaper_frame_size,
                         wallpaper_draw_y - self.wallpaper_frame_size,
                         self.wallpaper_width + self.wallpaper_frame_size * 2 + 1,
                         self.wallpaper_height + self.wallpaper_frame_size * 2 + 1)
            cr.stroke()

            cr.rectangle(wallpaper_draw_x,
                         wallpaper_draw_y,
                         self.wallpaper_width + 1,
                         self.wallpaper_height + 1)
            cr.stroke()
        
        if reflection:
            cr.translate(wallpaper_draw_x - self.wallpaper_frame_size - 1,
                         wallpaper_draw_y + self.wallpaper_height + self.wallpaper_frame_size + 1)
            cr.scale(1, -1)
        
        draw_pixbuf(cr, pixbuf, wallpaper_draw_x, wallpaper_draw_y)
        
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        self.hover_flag = True
        
        self.emit_redraw_request()
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        self.hover_flag = False
        
        self.emit_redraw_request()
        
    def icon_item_highlight(self):
        '''
        Highlight item.
        
        This is IconView interface, you should implement it.
        '''
        self.highlight_flag = True

        self.emit_redraw_request()
        
    def icon_item_normal(self):
        '''
        Set item with normal status.
        
        This is IconView interface, you should implement it.
        '''
        self.highlight_flag = False
        
        self.emit_redraw_request()
    
    def icon_item_button_press(self, x, y):
        '''
        Handle button-press event.
        
        This is IconView interface, you should implement it.
        '''
        pass        
    
    def icon_item_button_release(self, x, y):
        '''
        Handle button-release event.
        
        This is IconView interface, you should implement it.
        '''
        pass
    
    def icon_item_single_click(self, x, y):
        '''
        Handle single click event.
        
        This is IconView interface, you should implement it.
        '''
        pass

    def icon_item_double_click(self, x, y):
        '''
        Handle double click event.
        
        This is IconView interface, you should implement it.
        '''
        self.switch_setting_view(self.theme)
    
    def icon_item_release_resource(self):
        '''
        Release item resource.

        If you have pixbuf in item, you should release memory resource like below code:

        >>> del self.pixbuf
        >>> self.pixbuf = None

        This is IconView interface, you should implement it.
        
        @return: Return True if do release work, otherwise return False.
        
        When this function return True, IconView will call function gc.collect() to release object to release memory.
        '''
        for pixbuf in self.pixbufs:
            del pixbuf
        self.pixbufs = []    
        
        # Return True to tell IconView call gc.collect() to release memory resource.
        return True
        
gobject.type_register(ThemeItem)