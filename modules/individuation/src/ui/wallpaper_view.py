#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Hou Shaohui
# 
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou Shaohui <houshao55@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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

from dtk.ui.menu import Menu
from dtk.ui.iconview import IconView
from dtk.ui.scrolled_window import ScrolledWindow
from helper import event_manager
from ui.wallpaper_item import AddItem, WallpaperItem
from theme_manager import background_gsettings
from nls import _

class WallpaperView(IconView):
    
    def __init__(self, padding_x=8, padding_y=10):
        IconView.__init__(self, padding_x=padding_x, padding_y=padding_y)
        
        self.add_item = AddItem()
        self.add_items([self.add_item])

        self.connect("right-click-item", self.__on_right_click_item)
        
        event_manager.add_callback("add-wallpapers", self.on_add_wallpapers)
        event_manager.add_callback("add-download-wallpapers", self.on_add_wallpapers)
        event_manager.add_callback("wallpapers-deleted", self.on_wallpapers_deleted)
        event_manager.add_callback("select-wallpaper", self.on_wallpaper_select)
        event_manager.add_callback("apply-wallpaper", self.on_wallpaper_apply)
        event_manager.add_callback("apply-download-wallpaper", self.on_download_wallpaper_apply)
        event_manager.add_callback("delete-wallpaper-link", self.__on_delete_wallpaper_link)
        self.theme = None

    def __on_delete_wallpaper_link(self, name, obj, data):
        items = filter(lambda item: item.image_path == data, self.items) 
        if items:                                                               
            self.delete_items(items) 

    def __on_right_click_item(self, widget, item, x, y):                        
        menu_items = [(None, _("Apply Wallpaper"), lambda : item.do_apply_wallpaper())]
        Menu(menu_items, True).show((int(x), int(y)))

    def set_theme(self, theme):    
        self.theme = theme
        self.clear()
        self.add_item.set_theme(self.theme)
        
        self.add_items([self.add_item])
        
        self.add_system_wallpapers(self.theme.get_system_wallpapers())        
        self.add_user_wallpapers(self.theme.get_user_wallpapers())

    def is_editable(self):
        if self.theme.is_system_theme:
            if len(self.theme.get_user_wallpapers()) == 0:
                return False

        return True

    def is_exists(self, image):    
        if self.theme == None:
            return False

        if image in self.theme.get_user_wallpapers():
            return True
        return False
    
    def add_user_wallpapers(self, image_paths, save=False):
        self.add_images(image_paths, readonly=False)
        if save:
            if self.theme == None:
                return
            
            self.theme.add_user_wallpapers(image_paths)        
    
    def add_system_wallpapers(self, image_paths):
        self.add_images(image_paths, readonly=True)

    def add_images(self, images, readonly=False):
        images = list(set(images))
        items = map(lambda image: WallpaperItem(image, readonly, self.theme, background_gsettings), images)
        self.add_items(items, insert_pos=-1)
        
    def on_wallpaper_select(self, name, obj, select_item):    
        image_uris = [ "file://%s" % item.image_path for item in self.items if item.is_tick]
        self.apply_wallpapers(image_uris)

    def is_deletable(self):
        for item in self.items:
            if not item.is_tick:
                return True

        return False

    def delete_wallpaper(self):
        for item in self.items:
            if not item.is_tick:
                self.theme.remove_option("user_wallpaper", item.image_path)

        self.theme.save()
        self.set_theme(self.theme, True)

    def is_randomable(self):
        i = 0

        for item in self.items:
            if item.is_tick:
                i += 1
        if i < 2:
            return False

        return True

    def is_select_all(self):
        for item in self.items:
            if item.__class__.__name__ == "AddItem":
                continue

            if not item.is_tick:
                return False

        return True

    def select_all(self):
        is_select_all = self.is_select_all()

        for item in self.items:
            if is_select_all:
                item.untick()
            else:
                item.tick()
        
        image_uris = [ "file://%s" % item.image_path for item in self.items if item.is_tick]
        self.apply_wallpapers(image_uris)

    def on_download_wallpaper_apply(self, name, obj, image_path):
        image_uris = ["file://%s" % image_path]
        self.apply_wallpapers(image_uris)
        if self.is_randomable():
            self.items[-2].tick()
    
    def on_wallpaper_apply(self, name, obj, apply_item):
        [ item.untick() for item in self.items if item != apply_item]
        image_uris = ["file://%s" % apply_item.image_path]
        self.apply_wallpapers(image_uris)
        
    def apply_wallpapers(self, image_paths):
        image_path_string = ";".join(image_paths)
        background_gsettings.set_string("picture-uris", image_path_string)        
        if self.theme:
            self.theme.save()        
                
    def on_add_wallpapers(self, name, obj, image_paths):    
        filter_images = filter(lambda image: not self.is_exists(image), image_paths)        
        if filter_images:
            self.add_user_wallpapers(filter_images, save=True)
        event_manager.emit("update-theme", self.theme)
            
    def on_wallpapers_deleted(self, name, obj, image_paths):        
        items = filter(lambda item: item.image_path in image_paths, self.items)
        if items:        
            self.delete_items(items)
        
    def get_scrolled_window(self):    
        scrolled_window = ScrolledWindow()
        scrolled_window.add_child(self)
        return scrolled_window
    
    def draw_mask(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill()
