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


import sys
import os
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from dtk.ui.new_slider import HSlider
from ui.detail_page import DetailPage
from ui.delete_page import DeletePage
from ui.theme_page import ThemePage
from ui.add_page import AddPage
from module_frame import ModuleFrame
from constant import PAGE_WIDTH, PAGE_HEIGHT
from helper import event_manager
from nls import _

class DeepinIndividuation(object):
    
    config_file = os.path.join(get_parent_dir(__file__, 2), "config.ini")
    
    def __init__(self):
        
        # Init theme datas.
        self.__init_data()
        
        self.module_frame = ModuleFrame(self.config_file)
        
        # Init slider.
        self.slider = HSlider()
    
        # Init theme setting view.
        self.detail_page = DetailPage()

        self.delete_page = DeletePage()
        
        # Init theme view.
        self.theme_page = ThemePage()
        
        # Init add page.
        self.add_page = AddPage()
    
        # Add widgets in slider.
        self.slider.append_page(self.theme_page)
        self.slider.append_page(self.detail_page)
        self.slider.append_page(self.add_page)
        self.theme_page.set_size_request(PAGE_WIDTH, PAGE_HEIGHT)
        self.detail_page.set_size_request(PAGE_WIDTH, PAGE_HEIGHT)
        self.add_page.set_size_request(PAGE_WIDTH, PAGE_HEIGHT)
        
        # Connect events.
        event_manager.add_callback("theme-detail", self.switch_detail_page)
        event_manager.add_callback("switch-to-deletepage", self.switch_delete_page)
        event_manager.add_callback("back-to-detailpage", self.back_to_detailpage)
        event_manager.add_callback("switch-to-addpage", self.switch_add_page)
        event_manager.add_callback("add-wallpapers", self.back_to_addpage)
        
        # Connect widgets.
        self.module_frame.add(self.slider)
        self.module_frame.connect("realize", lambda w: self.slider.set_to_page(self.theme_page))
        self.module_frame.module_message_handler = self.message_handler        
        self.module_frame.run()        

    def __init_data(self):
        from theme_manager import theme_manager
        theme_manager.load()
    
    def message_handler(self, *message):
        (message_type, message_content) = message
        if message_type == "click_crumb":
            (crumb_index, crumb_label) = message_content
            if crumb_index == 1:
                self.slider.slide_to_page(self.theme_page, "left")
            elif crumb_index == 2:    
                self.slider.slide_to_page(self.detail_page, "left")
                
        elif message_type == "show_again":
            self.slider.set_to_page(self.theme_page)
            self.module_frame.send_module_info()

    def switch_delete_page(self, name, obj, theme):
        self.slider.slide_to_page(self.delete_page, "right")
        self.delete_page.set_theme(theme)
        self.module_frame.send_submodule_crumb(3, _("Delete Wallpaper"))
            
    def back_to_addpage(self, name, obj, data):        
        self.module_frame.send_message("back", 2)
        self.slider.slide_to_page(self.detail_page, "left")        
    
    def back_to_detailpage(self, name, obj, theme):
        self.module_frame.send_message("back", 2)
        self.slider.slide_to_page(self.detail_page, "left")
        self.detail_page.set_theme(theme)
    
    def switch_detail_page(self, name, obj, theme):
        self.slider.slide_to_page(self.detail_page, "right")
        self.detail_page.set_theme(theme)
        self.module_frame.send_submodule_crumb(2, _("%s Theme Setting") % theme.get_name())
        
    def switch_add_page(self, name, obj, theme):    
        self.slider.slide_to_page(self.add_page, "right")
        self.add_page.set_theme(theme)
        self.module_frame.send_submodule_crumb(3, _("Add Wallpaper"))

if __name__ == "__main__":
    DeepinIndividuation()
