#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.                                        
#               2012 ~ 2013 Zhai Xiang                                          
#                                                                               
# Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>                            
# Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>                            
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
from theme import app_theme
from dtk.ui.label import Label
from dtk.ui.combo import ComboBox
from dtk.ui.button import ToggleButton
from ConfigParser import ConfigParser

from media import MediaAutorun
from app import AppManager
import gtk
import style
from constants import STANDARD_LINE, TEXT_WINDOW_LEFT_PADDING 
from nls import _

CFG_FILE = os.path.expanduser("~/.config/deepin-system-settings/mount_media/mount_media.ini")

if not os.path.exists(CFG_FILE):
    os.makedirs(os.path.dirname(CFG_FILE))
    with open(CFG_FILE, "w") as cfg:
        parser = ConfigParser()
        parser.add_section("mount_media")
        parser.set("mount_media", "auto_mount", "none")
        parser.write(cfg)
        
def get_auto_mount():
    with open(CFG_FILE) as cfg:
        parser = ConfigParser()        
        parser.readfp(cfg)
        return parser.get("mount_media", "auto_mount")

def set_auto_mount(auto_mount_option):
    with open(CFG_FILE, "r+") as cfg:
        parser = ConfigParser()
        parser.readfp(cfg)
        cfg.seek(0)
        cfg.truncate()
        parser.set("mount_media", "auto_mount", auto_mount_option)
        parser.write(cfg)

class MediaView(gtk.VBox):
    ENTRY_WIDTH = 200
    LEFT_WIDTH = STANDARD_LINE - TEXT_WINDOW_LEFT_PADDING

    def __init__(self):
        gtk.VBox.__init__(self)
        self.all_app_default_value = {}
        style.draw_background_color(self)
        self.media_handle = MediaAutorun()
        self.app_manager = AppManager()
        self.init_table()
        
    def __get_index_from_value(self, value, _list):
        for tup in _list:
            if tup[1] == value:
                return _list.index(tup)

    def init_table(self):

        table = gtk.Table(8, 3, False)

        #info_label = Label(_("You can choose the operation after plugining media or device"))

        cd_label = Label(_("CD"))
        dvd_label = Label(_("DVD"))
        player_label = Label(_("Audio Player"))
        photo_label = Label(_("Camera"))
        software_label = Label(_("Applications"))
        auto_mount_label = Label(_("Automatically Mount"))

        self.all_label_list = [cd_label, dvd_label, player_label,
                               photo_label, software_label]

        default_list = [(_("Other applications"), "other_app"),
                        (_("Ask"), "ask"),
                        (_("Do nothing"), "do_nothing"),
                        (_("Open folder"),"open_folder")]
        auto_mount_list = [(_("Do nothing"), "do_nothing"), 
                           (_("Ask"), "ask"),
                           (_("Mount"), "mount"),
                           (_("Mount and open folder"), "mount_and_open")]
        #self.auto_mount_box = gtk.HBox(spacing = WIDGET_SPACING)
        #self.auto_mount_label = Label(_("apply auto open for all media and devices"))
        self.auto_mount_label = Label(_("AutoPlay"))
        self.auto_mount_toggle = ToggleButton(app_theme.get_pixbuf("toggle_button/inactive_normal.png"), 
            app_theme.get_pixbuf("toggle_button/active_normal.png"))
        #self.auto_mount_box.pack_start(self.auto_mount_label, False, False)
        #self.auto_mount_box.pack_start(self.auto_mount_toggle, False, False)

        self.cd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.dvd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.player= ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.photo = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.software = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.auto_mount = ComboBox(auto_mount_list, fixed_width=self.ENTRY_WIDTH)
        self.auto_mount.set_select_index(self.__get_index_from_value(get_auto_mount(), auto_mount_list))
        #self.more_option = Button(_("more option"))

        ###below content type displayed as more option is clicked"
        self.audio_dvd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.blank_bd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.blank_cd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.blank_hddvd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.video_bluray = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.ebook_reader = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.video_hddvd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.image_picturecd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.video_svcd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)
        self.video_vcd = ComboBox(default_list, fixed_width=self.ENTRY_WIDTH)

        #table.attach(style.wrap_with_align(info_label, width=self.LEFT_WIDTH), 0, 3, 0, 1)
        table.attach(style.wrap_with_align(cd_label, width=self.LEFT_WIDTH), 0, 1, 4, 5)
        table.attach(style.wrap_with_align(dvd_label, width=self.LEFT_WIDTH), 0, 1, 5, 6)
        table.attach(style.wrap_with_align(player_label, width=self.LEFT_WIDTH), 0, 1, 6, 7)
        table.attach(style.wrap_with_align(photo_label, width=self.LEFT_WIDTH), 0, 1, 7, 8)
        table.attach(style.wrap_with_align(software_label, width=self.LEFT_WIDTH), 0, 1, 8, 9)
        table.attach(style.wrap_with_align(auto_mount_label, width=self.LEFT_WIDTH), 0, 1, 9, 10)

        #table.attach(style.wrap_with_align(self.auto_mount_box, align = "left", left = 180), 0, 3, 1, 2)
        table.attach(style.wrap_with_align(self.auto_mount_label, width=self.LEFT_WIDTH), 0, 1, 1, 2)
        table.attach(style.wrap_with_align(self.auto_mount_toggle), 1, 3, 1, 2)

        table.attach(style.wrap_with_align(self.cd), 1, 3, 4, 5)
        table.attach(style.wrap_with_align(self.dvd), 1, 3, 5, 6)
        table.attach(style.wrap_with_align(self.player), 1, 3, 6, 7)
        table.attach(style.wrap_with_align(self.photo), 1, 3, 7, 8)
        table.attach(style.wrap_with_align(self.software), 1, 3, 8, 9)
        table.attach(style.wrap_with_align(self.auto_mount), 1, 3, 9, 10)

        # UI style
        table_align = style.set_box_with_align(table, "text")
        style.set_table(table)

        self.pack_start(table_align, False, False)

        combo_list = [self.cd, self.dvd, self.player, self.photo, self.software]
        for combo in combo_list:
            combo.set_size_request(self.ENTRY_WIDTH, 22)

        self.refresh_app_list(default_list)

        self.media_handle.auto_mount = True
        if self.media_handle.automount_open:
            for combo in self.all_app_dict:
                combo.set_sensitive(True)
            for l in self.all_label_list:
                l.set_sensitive(True)
        else:
            for combo in self.all_app_dict:
                combo.set_sensitive(False)
            for l in self.all_label_list:
                l.set_sensitive(False)
    
        self.auto_mount_toggle.set_active(self.media_handle.automount_open)

        self.connect_signal_to_combos()

    def refresh_app_list(self, default_list):
        self.default_list = default_list
        self.all_app_dict = {self.cd: self.media_handle.cd_content_type,
                             self.dvd: self.media_handle.dvd_content_type,
                             self.player: self.media_handle.player_content_type,
                             self.photo: self.media_handle.photo_content_type,
                             self.software: self.media_handle.software_content_type,
                             }

        for key, value in self.all_app_dict.iteritems():
            app_info_list = []
            app_info_list.extend(self.app_manager.get_all_for_type(value))
            
            state = self.get_state(value)
            if state == "set_default":
                default_value = 0
            else:
                default_value = len(app_info_list) + ["ask", "do_nothing","open_folder"].index(state) + 1

            key.add_items(map(lambda info:(info.get_name(), info), app_info_list) + default_list, select_index=default_value)

        self.all_app_default_value = {self.cd: self.cd.get_select_index(), 
                                      self.dvd: self.dvd.get_select_index(), 
                                      self.player: self.player.get_select_index(), 
                                      self.photo: self.photo.get_select_index(), 
                                      self.software: self.software.get_select_index(),
                                     }

    def connect_signal_to_combos(self):
        for combo in self.all_app_dict:
            combo.connect("item-selected", self.change_autorun_callback)
        self.auto_mount.connect("item-selected", self.auto_mount_combo_changed)
        self.auto_mount_toggle.connect("toggled", self.automount_open_toggle_cb)
        
    def auto_mount_combo_changed(self, widget, content, value, index):
        set_auto_mount(value)

    def change_autorun_callback(self, widget, content, value, index):
        if value != "other_app":
            self.all_app_default_value[widget] = index
        if type(value) is not str:
            self.set_media_handler_preference(self.all_app_dict[widget], widget, "set_default")
            self.app_manager.set_default_for_type(value, self.all_app_dict[widget])
        else:
            self.set_media_handler_preference(self.all_app_dict[widget], widget, value)

    def automount_open_toggle_cb(self, widget):
        self.media_handle.automount_open = widget.get_active()
        
        if widget.get_active():
            for combo in self.all_app_dict:
                combo.set_sensitive(True)
            for l in self.all_label_list:
                l.set_sensitive(True)
        else:
            for combo in self.all_app_dict:
                combo.set_sensitive(False)
            for l in self.all_label_list:
                l.set_sensitive(False)

    def set_media_handler_preference(self, x_content, widget, action_name=None):
        if action_name == "ask":
            self.media_handle.remove_x_content_start_app(x_content)
            self.media_handle.remove_x_content_ignore(x_content)
            self.media_handle.remove_x_content_open_folder(x_content)
            print action_name, ">>>",self.get_state(x_content)

        elif action_name == "do_nothing":
            self.media_handle.remove_x_content_start_app(x_content)
            self.media_handle.add_x_content_ignore(x_content)
            self.media_handle.remove_x_content_open_folder(x_content)
            print action_name, ">>>",self.get_state(x_content)

        elif action_name == "open_folder":
            self.media_handle.remove_x_content_start_app(x_content)
            self.media_handle.remove_x_content_ignore(x_content)
            self.media_handle.add_x_content_open_folder(x_content)
            print action_name, ">>>",self.get_state(x_content)

        elif action_name == "set_default":
            self.media_handle.add_x_content_start_app(x_content)
            self.media_handle.remove_x_content_ignore(x_content)
            self.media_handle.remove_x_content_open_folder(x_content)
            print action_name, ">>>",self.get_state(x_content)
        else:
            from dtk.ui.dialog import OpenFileDialog
            OpenFileDialog(
                _("Other applications"), 
                self.get_toplevel(), 
                lambda name: self.add_app_info(name, x_content), 
                self.__cancel_other_application(widget))

    def __cancel_other_application(self, widget):
        widget.set_select_index(self.all_app_default_value[widget])

    def add_app_info(self, app_name, x_content):
        import os
        app_name = os.path.basename(app_name)
        app_info = self.app_manager.get_app_info(app_name + " %u", app_name)
        self.set_media_handler_preference(x_content, "set_default")
        self.app_manager.set_default_for_type(app_info, x_content)
        self.app_manager.get_all_for_type(x_content)
        self.refresh_app_list(self.default_list)

    def get_state(self, x_content):
        start_up = self.media_handle.autorun_x_content_start_app
        ignore = self.media_handle.autorun_x_content_ignore
        open_folder = self.media_handle.autorun_x_content_open_folder

        start_up_flag = x_content in start_up
        ignore_flag = x_content in ignore
        open_folder_flag = x_content in open_folder

        if start_up_flag:
            return "set_default"
        elif ignore_flag:
            return "do_nothing"
        elif open_folder_flag:
            return "open_folder"
        else:
            return "ask"
