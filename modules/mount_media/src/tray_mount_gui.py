#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Deepin, Inc.
#               2013 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
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

from dtk.ui.line import HSeparator
from vtk.draw  import draw_text, draw_pixbuf
from vtk.utils import get_text_size
from nls import _
import os
import sys
import gtk
import gio
import glib
import gobject


image_path = os.path.dirname(sys.argv[0])
ICON_SIZE = 16

#class Device(gtk.Button):
class Device(gtk.HBox):
    def __init__(self):
        #gtk.Button.__init__(self)
        gtk.HBox.__init__(self)
        self.icon_image  = gtk.Image()
        self.open_btn  = gtk.Button()
        self.close_btn = gtk.Button()
        #self.icon_btn.connect("expose-event", self.icon_btn_expose_event)
        self.open_btn.connect("expose-event", self.open_btn_expose_event)
        self.close_btn.connect("expose-event", self.close_btn_expose_event)
        self.pack_start(self.icon_image, False, False, 5)
        self.pack_start(self.open_btn, True, True, 5)
        self.pack_start(self.close_btn, False, False)
        self.__init_values()

    def __init_values(self):
        self.eject_check = False
        self.icon_pixbuf = None
        self.off_pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(image_path, "image/offbutton/off.png"))
        self.on_pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(image_path, "image/offbutton/on.png"))
        close_w = self.on_pixbuf.get_width()
        close_h = self.on_pixbuf.get_height()
        self.close_btn.set_size_request(close_w, close_h)
        self.show_all()

    def icon_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        #
        if self.icon_pixbuf:
            print self.icon_pixbuf
            
            '''
            draw_pixbuf(cr,
                        pixbuf,
                        rect.x,
                        rect.y)
            '''
        '''
        cr.rectangle(rect.x, rect.y, 16, 16)
        cr.fill()
        '''
        #
        return True


    def open_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation
        text = widget.get_label().decode("utf-8")
        text_width = get_text_size("ABCDEFABCDEFH", text_size=9)[0]
        ch_width = get_text_size("a", text_size=9)[0]
        dec_width = get_text_size(text, text_size=9)[0] - text_width
        if dec_width > 0:
            index = dec_width/ch_width
            text = text[0:len(text)-index] + "..."
        if self.eject_check:
            text_color_value = "#000000"
        else:
            text_color_value = "#9d9d9d"
        draw_text(cr, 
                  text, 
                  rect.x, 
                  rect.y + rect.height/2 - get_text_size(text)[1]/2, 
                  text_color=text_color_value,
                  text_size=9)
        return True

    def close_btn_expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.allocation

        if self.eject_check:
            simple_pixbuf = self.on_pixbuf
        else:
            simple_pixbuf = self.off_pixbuf

        draw_pixbuf(cr, 
                    simple_pixbuf, 
                    rect.x,
                    rect.y + rect.height/2 - simple_pixbuf.get_height()/2)
        return True

    def set_eject_check(self, check):
        self.eject_check = check
        self.queue_draw()

class EjecterApp(gobject.GObject):
    __gsignals__ = {
    "update-usb" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    "remove-usb" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    "empty-usb" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    def __init__(self):
        gobject.GObject.__init__(self)
        self.__init_values()
        self.__load_monitor()
        self.__init_monitor_events()

    def __init_values(self):
        hseparator_color = [(0,   ("#777777", 0.0)),
                            (0.5, ("#000000", 0.3)),
                            (1,   ("#777777", 0.0))
                           ]
        self.hbox = gtk.HBox()
        self.title_image = gtk.image_new_from_file(os.path.join(image_path, "image/usb/usb_label.png"))
        self.title_label = gtk.Label(_("USB Device"))
        #self.title_label.connect("expose-event", self.title_label_expose_event)
        self.title_label_ali = gtk.Alignment(0, 0, 0, 0)
        self.title_label_ali.set_padding(0, 0, 0, 0)
        self.title_label_ali.add(self.title_label)

        self.hbox.pack_start(self.title_image, False, False)
        self.hbox.pack_start(self.title_label_ali, True, True)

        self.h_separator_top = HSeparator(hseparator_color, 0, 0)
        self.h_separator_ali = gtk.Alignment(1, 1, 1, 1)
        self.h_separator_ali.set_padding(5, 10, 0, 0)
        self.h_separator_ali.add(self.h_separator_top)

        self.monitor_vbox = gtk.VBox()
        self.vbox = gtk.VBox()
        self.vbox.pack_start(self.hbox, False, False)
        self.vbox.pack_start(self.h_separator_ali, True, True)
        self.vbox.pack_start(self.monitor_vbox, False, False)

        self.monitor = gio.VolumeMonitor()

    def __load_monitor(self):
        # 移除挂载上的控件.
        for widget in self.monitor_vbox.get_children():
            self.monitor_vbox.remove(widget)
        self.network_mounts_list = []
        self.network_volumes_list = []
        drives = self.monitor.get_connected_drives()
        volumes = self.monitor.get_volumes()
        #print "drives:", drives
        # 获取大硬盘下的东西.
        for drive in drives:
            volumes = drive.get_volumes() 
            #print "volumes:", volumes
            if volumes:
                for volume in volumes:
                    id = volume.get_identifier("unix-device")
                    #print "id:", id
                    if id.startswith("network"):
                        print "network..."  
                        self.network_volumes_list.append(volume)
                        continue
                    mount = volume.get_mount()
                    if mount: # moutn != None
                        #print "mount信息:"
                        icon = mount.get_icon() 
                        root  = mount.get_root()
                        mount_uri = root.get_uri()
                        tooltip   = root.get_parse_name()
                        name = mount.get_name()
                        #
                        self.__add_place(
                                name, icon, mount_uri,
                                drive, volume, mount)
                    else:
                        print "moutn 为None, volume信息;"
                        icon = volume.get_icon() 
                        name = volume.get_name()
                        self.__add_place(
                                name, icon, None, 
                                drive, volume, None)
            else: # volumes.
                if (drive.is_media_removable() and 
                    not drive.is_media_check_automatic()):
                    print "drive:==="
                    icon = drive.get_icon()
                    name = drive.get_name()
                    self.__add_place(
                            name, icon, None,
                            drive, None, None)

        #print "======================\n\n\n"
        for volume in volumes:
            drive = volume.get_drive()
            if drive:
                #print "drive:", drive
                continue
            id = volume.get_identifier("unix-device")
            #print "id:", id

            mount = volume.get_mount()
            if mount:
                #print "mount:"
                icon = mount.get_icon()
                root = mount.get_root()
                mount_uri  = root.get_uri()
                tooltip   = root.get_parse_name()
                #print "icon:", icon
                #print "uri:", uri
                self.__add_place(
                        name, icon, mount_uri,
                        None, volume, mount)
            else:
                icon = volume.get_icon()
                name = volume.get_name()
                #print "icon:", icon
                #print "name:", name
                self.__add_place(
                        name, icon, None,
                        None, volume, None)
        print "========================\n\n\n"
        mounts = self.monitor.get_mounts() 
        #print "mounts:", mounts
        for mount in mounts:
            if mount.is_shadowed():
                print
                continue
            volume = mount.get_volume()
            if volume:
                #print "volume:===>>>"
                continue
            root = mount.get_root()
            if not root.is_native():
                #print "network....===>>>"
                # 保存到网络列表中.
                self.network_mounts_list.insert(0, mount)
                continue;

            #print "mount:====>>>"
            icon = mount.get_icon()
            mount_uri = root.get_uri()
            tooltip   = root.get_parse_name()
            name = mount.get_name()
            '''
            print "icon:", icon
            print "mount_uri:", mount_uri
            print "name:", name
            '''
            self.__add_place(
                    name, icon, mount_uri,
                    None, None, mount)

        # mounts  网络列表过滤.
        for mount in self.network_mounts_list:
            root = mount.get_root()
            icon = mount.get_icon()
            mount_uri = root.get_uri()
            tooltip   = root.get_parse_name()
            name = mount.get_name()
            '''
            print "mounts....====>>>"
            print "root:", root
            print "icon:", icon
            print "name:", name
            print "uri:", mount_uri
            '''
            self.__add_place(
                    name, icon, mount_uri, 
                    None, None, mount)

    def __add_place(self, 
                    name, icon, uri, 
                    drive, volume, mount):
        print "__add_place..."
        print "name:", name
        print "icon:", icon
        print "uri:", uri
        print self.__set_mount_and_eject_bit(drive, volume, mount)
        device_btn = Device()
        #
        device_btn.icon_image.set_from_gicon(icon, 16)
        #device_btn.icon_pixbuf = icon
        device_btn.open_btn.set_label(name)
        device_btn.open_btn.connect("clicked", self.device_btn_open_btn_clicked, uri)
        device_btn.close_btn.connect("clicked", self.device_btn_close_btn_clicked)
        self.monitor_vbox.pack_start(device_btn)
        self.monitor_vbox.show_all()

    def device_btn_open_btn_clicked(self, widget, uri):
        print "device_btn_open_btn_clicked....", uri

    def device_btn_close_btn_clicked(self, widget):
        print "device_btn_close_btn_clicked..."

    def __set_mount_and_eject_bit(self, drive, volume, mount):
        show_unmount = False # 是否存在.
        show_eject   = False # 是否挂载上去了.
        if drive:
            show_eject = drive.can_eject()
        if volume:
            show_eject = volume.can_eject()
        if mount:
            show_eject = mount.can_eject()
            show_unmount = (mount.can_unmount() and (not show_eject))
        return show_unmount, show_eject

    def __init_monitor_events(self):
        # mount events.
        self.monitor.connect("mount-added", self.mount_added_callback)
        self.monitor.connect("mount-removed", self.mount_removed_callback)
        self.monitor.connect("mount-changed", self.mount_changed_callback)
        # volume events.
        self.monitor.connect("volume-added", self.volume_added_callback)
        self.monitor.connect("volume-removed", self.volume_removed_callback)
        self.monitor.connect("volume-changed", self.volume_changed_callback)
        # drive events.
        self.monitor.connect("drive-disconnected", self.drive_disconnected_callback)
        self.monitor.connect("drive-connected", self.drive_connected_callback)
        self.monitor.connect("drive-changed", self.drive_changed_callback)

    def mount_added_callback(self, volume_monitor, mount):
        print "mount_added_callback..."
        print "update_places"
        self.__load_monitor()

    def mount_removed_callback(self, volume_monitor, mount):
        print "mount_removed_callback..."
        print "update_places"
        self.__load_monitor()

    def mount_changed_callback(self, volume_monitor, mount):
        print "mount_changed_callback..."
        print "update_places"
        self.__load_monitor()

    def volume_added_callback(self, volume_monitor, volume):
        print "volume_added_callback..."
        print "update_places"
        self.__load_monitor()

    def volume_removed_callback(self, volume_monitor, volume):
        print "volume_removed_callback...."
        print "update_places"
        self.__load_monitor()

    def volume_changed_callback(self, volume_monitor, volume):
        print "volume_changed_callback..."
        print "update_places"
        self.__load_monitor()

    def drive_disconnected_callback(self, volume_monitor, drive):
        print "drive_disconnected_callback..."
        print "update_places"
        self.__load_monitor()

    def drive_connected_callback(self, volume_monitor, drive):
        print "drive_connected_callback..."
        print "update_places"
        self.__load_monitor()

    def drive_changed_callback(self, volume_monitor, drive):
        print "drive_changed_callback......"
        print "update_places"
        self.__load_monitor()

if __name__ == "__main__":
    import gtk
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    
    eject = EjecterApp()
    win.add(eject.vbox)
    win.show_all()
    
    gtk.main()


