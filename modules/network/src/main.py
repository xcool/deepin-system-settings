#!/usr/bin/env python
#-*- coding:utf-8 -*-

#from proxy_config import ProxyConfig
from proxy_config import ProxyConfig
import sys
import os
sys.path.append("../")
from theme import app_theme
from dtk.ui.theme import ui_theme
from dtk.ui.new_treeview import TreeView
from dtk.ui.draw import draw_pixbuf, draw_line
from dtk.ui.utils import color_hex_to_cairo, get_parent_dir, is_dbus_name_exists
from dtk.ui.label import Label
from dtk.ui.new_slider import HSlider
from dtk.ui.scrolled_window import ScrolledWindow
from dtk.ui.threads import post_gui
import gtk
import traceback
import threading as td

from container import Contain
from lists import WiredItem, WirelessItem

from lan_config import WiredSetting
from wlan_config import WirelessSetting
from dsl_config import DSLSetting

#from nmlib.nmobject import dbus_loop
from nmlib.nmclient import nmclient
from nmlib.nm_remote_settings import nm_remote_settings
from nmlib.nmcache import cache

slider = HSlider()
PADDING = 32
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))
from module_frame import ModuleFrame 

        

class WiredDevice(object):
    def __init__(self, device, treeview, index):
        self.wired_device = device
        self.tree = treeview
        self.index = index
        device_ethernet = cache.get_spec_object(self.wired_device.object_path)
        self.wired_device.connect("device-active", self.device_activate)
        self.wired_device.connect("device-deactive", self.device_deactive)
        device_ethernet.connect("try-activate-begin", self.try_activate_begin)

    def device_activate(self, widget ,reason):
        if self.tree.visible_items != []:
            self.tree.visible_items[self.index].network_state = 2
            self.tree.queue_draw()

    def device_deactive(self, widget, reason):
        if not reason == 0:
            if self.tree.visible_items != []:
                self.tree.visible_items[self.index].network_state = 0
                self.tree.queue_draw()

    def try_activate_begin(self, widget):
        if self.tree.visible_items != []:
            self.tree.visible_items[self.index].network_state = 1
            self.tree.queue_draw()

class WiredSection(gtk.VBox):
    def __init__(self, send_to_crumb_cb):
        gtk.VBox.__init__(self)
        self.wired_devices = nmclient.get_wired_devices()
        if self.wired_devices:
            self.wire = Contain(app_theme.get_pixbuf("/Network/wired.png"), "有线网络", self.toggle_cb)
            self.send_to_crumb_cb = send_to_crumb_cb
            self.pack_start(self.wire, False, False, 0)
            self.settings = None
            self.tree = TreeView([])
            self.tree.set_no_show_all(True)
            self.tree.hide()
            self.align = gtk.Alignment()
            self.align.show()
            self.align.set(0,0,1,1)
            self.align.set_padding(0,0,PADDING,11*2)
            self.align.add(self.tree)
            self.pack_start(self.align, False, False, 0)
            
         
    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            item_list = self.retrieve_list()
            self.tree.add_items(item_list, 0, True)
            self.tree.visible_items[-1].is_last = True
            self.tree.set_no_show_all(False)
            self.tree.set_size_request(-1,len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
            for index, wired_device in enumerate(self.wired_devices):
                WiredDevice(wired_device,self.tree, index )

            self.try_active()
            self.show_all()
        else:
            self.tree.add_items([],0,True)
            self.tree.hide()
            for wired_device in self.wired_devices:
                wired_device.nm_device_disconnect()

    def retrieve_list(self):
        """
        retrieve network lists, will use thread
        """
        wired_items = []
        for wired_device in self.wired_devices:
                #self.device_ethernet.auto_connect()
                #self.device_ethernet.emit("try-activate-begin")
            wired_items.append(WiredItem(wired_device,
                                         self.settings, 
                                         lambda : slider.slide_to_page(self.settings, "right"),
                                         self.send_to_crumb_cb))
        return wired_items

    #def get_active(self):
        #for index, device in enumerate(self.wired_devices):
            #if device.is_active:
                #return index
        #return False

    def try_active(self):
        for index, device in enumerate(self.wired_devices):
            if not device.is_active():
                device_ethernet = cache.get_spec_object(device.object_path)
                device_ethernet.auto_connect()
                device_ethernet.emit("try-activate-begin")
            else:
                self.tree.visible_items[index].network_state = 2

    def add_setting_page(self, setting_page):
        self.settings = setting_page
        if self.wired_devices:
            for device in self.wired_devices:
                if device.is_active():
                    self.wire.set_active(True)
                else:
                    self.wire.set_active(False)

class WirelessDevice(object):
    def __init__(self, device, treeview, ap_list):
        self.wireless_device = device
        self.ap_list = ap_list
        self.tree = treeview
        self.device_wifi = cache.get_spec_object(self.wireless_device.object_path)
        self.wireless_device.connect("device-active", self.device_is_active)
        self.wireless_device.connect("device-deactive", self.device_is_deactive)
        self.device_wifi.connect("try-ssid-begin", self.try_to_connect)

    def try_to_connect(self, widget, ap_object):
        index = self.ap_list.index(ap_object)
        self.tree.visible_items[index].network_state = 1
        self.tree.queue_draw()
    
    def device_is_active(self, widget, reason):
        active = self.wireless_device.get_active_connection()
        # FIXME little wierd
        if widget.is_active():
            index = [ap.object_path for ap in self.ap_list].index(active.get_specific_object())
            self.index = index
            self.tree.visible_items[index].network_state = 2
            self.tree.queue_draw()
    
    def device_is_deactive(self, widget, reason):
        if not reason == 0:
            if self.tree.visible_items != []:
                self.tree.visible_items[self.index].network_state = 0
                self.tree.queue_draw()
    #def try_to_connect_end(self, widget, ap_object):
        #pass
        #print ap_object.get_ssid(),"end"
        #index = self.ap_list.index(ap_object)
        #self.tree.visible_items[index].network_state = 0
        #self.tree.queue_draw()

class WirelessSection(gtk.VBox):
    def __init__(self, send_to_crumb_cb):
        gtk.VBox.__init__(self)
        self.wireless_devices = nmclient.get_wireless_devices()
        if self.wireless_devices:
            # FIXME will support multi devices
            nmclient.wireless_set_enabled(True)

            self.wireless = Contain(app_theme.get_pixbuf("/Network/wireless.png"), "无线网络", self.toggle_cb)
            self.send_to_crumb_cb = send_to_crumb_cb

            self.pack_start(self.wireless, False, False)
            self.tree = TreeView([], enable_multiple_select = False)
            self.settings = None
            self.wifi = WifiSection()

            self.vbox = gtk.VBox()
            self.vbox.pack_start(self.tree)
            self.vbox.pack_start(self.wifi)
            self.vbox.set_no_show_all(True)
            self.vbox.hide()
            self.align = gtk.Alignment()
            self.align.show()
            self.align.set(0,0,1,1)
            self.align.set_padding(0,0,PADDING,11 + 11)
            self.align.add(self.vbox)

            self.pack_start(self.align, False, False, 0)
    
    def add_setting_page(self, page):
        self.settings = page
        if self.wireless_devices:
            for wireless_device in self.wireless_devices:
                if wireless_device.is_active():
                    self.wireless.set_active(True)
                else:
                    self.wireless.set_active(False)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active: 
            item_list = self.retrieve_list()
            self.tree.add_items(item_list,0,True)
            self.tree.visible_items[-1].is_last = True
            self.vbox.set_no_show_all(False)
            self.tree.set_size_request(-1,len(self.tree.visible_items) * self.tree.visible_items[0].get_height())
            self.queue_draw()
            self.show_all()

            for wireless_device in self.wireless_devices:
                WirelessDevice(wireless_device, self.tree, self.ap_list)

            index = self.get_actives(self.ap_list)
            if index:
                for i in index:
                    self.tree.visible_items[i].network_state = 2
            else:
                for wireless_device in self.wireless_devices:
                    device_wifi = cache.get_spec_object(wireless_device.object_path)
                    device_wifi.auto_connect()
            self.index = index
        else:
            self.tree.add_items([],0,True)
            self.vbox.hide()
            for wireless_device in self.wireless_devices:
                wireless_device.nm_device_disconnect()

    def retrieve_list(self):
        """
        retrieve network lists, will use thread
        """
        self.ap_list = []
        for wireless_device in self.wireless_devices:
            device_wifi = cache.get_spec_object(wireless_device.object_path)
            self.ap_list += device_wifi.order_ap_list()

        items = [WirelessItem(i,
                              self.settings,
                              lambda : slider.slide_to_page(self.settings, "right"),
                              self.send_to_crumb_cb) for i in self.ap_list]
        return items

    def get_actives(self, ap_list):
        index = []
        for wireless_device in self.wireless_devices:
            active_connection = wireless_device.get_active_connection()
            if active_connection:
                index.append([ap.object_path for ap in ap_list].index(active_connection.get_specific_object()))

        return index
                


class WifiSection(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self, 0)
        cont = Contain(app_theme.get_pixbuf("/Network/wifi.png"), "个人热点", self.toggle_cb)
        self.pack_start(cont, False, False)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0, 0.0, 1, 1)
            self.align.set_padding(0, 0, PADDING,0)
            self.align.show()
            self.h = gtk.HBox()
            self.h.show()
            label = gtk.Label("热点密码 ")
            label.show()
            entry = gtk.Entry()
            entry.show()
            self.align.add(self.h)
            self.h.pack_start(label, False, False, 0)
            self.h.pack_start(entry, False, True, 0)
            self.pack_start(self.align, False, True, 0)
        else:
            self.h.destroy()

class DSL(gtk.VBox):

    def __init__(self, slide_to_setting_cb):
        gtk.VBox.__init__(self)
        self.slide_to_setting = slide_to_setting_cb
        self.setting_page = None
        dsl = Contain(app_theme.get_pixbuf("/Network/wired.png"), "宽带拨号", self.toggle_cb)
        self.pack_start(dsl, False, False)
        pppoe_connections =  nm_remote_settings.get_pppoe_connections()

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11)
            label = Label("DSL setting", ui_theme.get_color("link_text"))
            label.connect("button-release-event", self.slide_to_event)

            self.align.add(label)
            self.align.connect("expose-event", self.expose_event)
            self.add(self.align)
            self.show_all()
        else:
            self.align.destroy()

    def add_setting_page(self, setting_page):
        self.setting_page = setting_page

    def slide_to_event(self, widget, event):
        self.setting_page.init()
        self.slide_to_setting()
        slider.slide_to_page(self.setting_page, "right")

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.child.allocation
        cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("link_text").get_color()))
        draw_line(cr, rect.x, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height)

class VpnSection(gtk.VBox):
    def __init__(self):

        gtk.VBox.__init__(self)
        vpn = Contain(app_theme.get_pixbuf("/Network/misc.png"), "VPN网络", self.toggle_cb)
        self.add(vpn)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11)
            label = Label("添加vpn网络", ui_theme.get_color("link_text"))
            label.connect("button-release-event", self.slide_to_event)

            self.align.add(label)
            self.align.connect("expose-event", self.expose_event)
            self.add(self.align)
            self.show_all()
        else:
            self.align.destroy()

    def slide_to_event(self, widget, event):
        print "clicked this label"

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.child.allocation
        cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("link_text").get_color()))
        draw_line(cr, rect.x, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height)


class ThreeG(gtk.VBox):
    def __init__(self):

        gtk.VBox.__init__(self)
        mobile = Contain(app_theme.get_pixbuf("/Network/3g.png"), "移动网络", self.toggle_cb)
        self.add(mobile)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11)
            label = Label("设置3G网络", ui_theme.get_color("link_text"))
            label.connect("button-release-event", self.slide_to_event)

            self.align.add(label)
            self.align.connect("expose-event", self.expose_event)
            self.add(self.align)
            self.show_all()
        else:
            self.align.destroy()

    def slide_to_event(self, widget, event):
        print "clicked 3G"

    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.child.allocation
        cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("link_text").get_color()))
        draw_line(cr, rect.x, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height)


class Proxy(gtk.VBox):
    def __init__(self, slide_to_setting_cb):
        gtk.VBox.__init__(self)
        self.slide_to_setting = slide_to_setting_cb
        proxy = Contain(app_theme.get_pixbuf("/Network/misc.png"), "网络代理", self.toggle_cb)
        self.settings = None
        self.add(proxy)

    def toggle_cb(self, widget):
        active = widget.get_active()
        if active:
            self.align = gtk.Alignment(0,0,0,0)
            self.align.set_padding(0,0,PADDING,11)
            label = Label("设置网络代理", ui_theme.get_color("link_text"))
            label.connect("button-release-event", self.slide_to_event)

            self.align.add(label)
            self.align.connect("expose-event", self.expose_event)
            self.add(self.align)
            self.show_all()
        else:
            self.align.destroy()

    def slide_to_event(self, widget, event):
        self.settings.init()
        self.slide_to_setting()
        slider.slide_to_page(self.settings, "right")


    def expose_event(self, widget, event):
        cr = widget.window.cairo_create()
        rect = widget.child.allocation
        cr.set_source_rgb(*color_hex_to_cairo(ui_theme.get_color("link_text").get_color()))
        draw_line(cr, rect.x, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height)

    def add_setting_page(self, setting_page):
        self.settings = setting_page
        #if self.wired_devices:
            #for device in self.wired_devices:
                #if device.is_active():
                    #self.wire.set_active(True)
                #else:
                    #self.wire.set_active(False)

if __name__ == '__main__':
    if is_dbus_name_exists("org.freedesktop.NetworkManager", False):
        module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))
        wireless = WirelessSection(lambda : module_frame.send_submodule_crumb(2, "无线设置"))
        wireless_setting_page = WirelessSetting(None, 
                                                lambda :slider.slide_to_page(main_align, "left"),
                                                lambda : module_frame.send_message("change_crumb", 1))
        wireless.add_setting_page(wireless_setting_page)

        wired = WiredSection(lambda : module_frame.send_submodule_crumb(2, "有线设置"))
        wifi = WifiSection()
        dsl = DSL(lambda : module_frame.send_submodule_crumb(2, "DSL"))
        vpn = VpnSection()
        mobile = ThreeG()
        proxy = Proxy(lambda : module_frame.send_submodule_crumb(2, "Proxy"))

        vbox = gtk.VBox(False, 17)
        vbox.pack_start(wired, False, True,5)
        vbox.pack_start(wireless, False, True, 0)
        vbox.pack_start(dsl, False, True, 0)
        vbox.pack_start(mobile, False, True, 0)
        vbox.pack_start(vpn, False, True, 0)
        vbox.pack_start(proxy, False, True, 0)
        
        scroll_win = ScrolledWindow()
        scroll_win.set_size_request(825, 425)

        scroll_win.add_with_viewport(vbox)
        main_align = gtk.Alignment(0,0,0,0)
        main_align.set_padding(11,11,11,11)
        main_align.add(scroll_win)
        
        wired_setting_page = WiredSetting(lambda  :slider.slide_to_page(main_align, "left"),
                                          lambda  : module_frame.send_message("change_crumb", 1))
        wired.add_setting_page(wired_setting_page)

        dsl_setting_page = DSLSetting( lambda  :slider.slide_to_page(main_align, "left"),
                                          lambda  : module_frame.send_message("change_crumb", 1))
        dsl.add_setting_page(dsl_setting_page)

        proxy_setting_page = ProxyConfig( lambda  :slider.slide_to_page(main_align, "left"),
                                          lambda  : module_frame.send_message("change_crumb", 1))
        proxy.add_setting_page(proxy_setting_page)

        slider.append_page(main_align)
        slider.append_page(wired_setting_page)
        slider.append_page(dsl_setting_page)
        slider.append_page(wireless_setting_page)
        slider.append_page(proxy_setting_page)

        module_frame.add(slider)
        
        def message_handler(*message):
            (message_type, message_content) = message
            if message_type == "show_again":
                slider.set_to_page(main_align)
                module_frame.send_module_info()
            elif message_type == "click_crumb":
                (crumb_index, crumb_label) = message_content
                if crumb_index == 1:
                    slider.slide_to_page(main_align, "left")

        module_frame.module_message_handler = message_handler
        
        module_frame.run()
