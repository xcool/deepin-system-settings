#!/usr/bin/env python
#-*- coding:utf-8 -*-
# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Zeng Zhi
# 
# Author:     Zeng Zhi <zengzhilg@gmail.com>
# Maintainer: Zeng Zhi <zengzhilg@gmail.com>
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


from dtk.ui.label import Label
from dtk.ui.entry import InputEntry
from dtk.ui.net import IPV4Entry
from nmlib.nm_utils import TypeConvert
import gtk

import style
from constants import CONTENT_FONT_SIZE, WIDGET_HEIGHT
from nls import _
from elements import DefaultToggle, Title
from helper import Dispatcher
from dss_log import log

class IPV4Conf(gtk.VBox):
    ENTRY_WIDTH = 222
    def __init__(self, connection=None, set_button_callback=None, dns_only=False, settings_obj=None, link_local=False):
        
        gtk.VBox.__init__(self)
        self.tab_name = _("IPv4 settings")
        self.connection = connection 
        self.set_button = set_button_callback
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj

        self.dns_only = dns_only

        # Ip configuration
         
        self.link_section = Title(_("Link-Local Only"), toggle_callback = self.link_local_callback, label_right=True)
        self.ip_table = gtk.Table(3, 2, False)
        self.ip_section = DefaultToggle(_("Automatic IP address"))
        self.ip_section.toggle_on = self.ip_toggle_off
        self.ip_section.toggle_off = self.ip_toggle_on

        self.addr_row = self.__set_row(_("IP Address:"), 0)
        self.mask_row = self.__set_row(_("Subnet Mask:"), 1)
        self.gate_row = self.__set_row(_("Gateway:"), 2)
        self.__table_attach(self.ip_table, self.addr_row, 0)
        self.__table_attach(self.ip_table, self.mask_row, 1)
        self.__table_attach(self.ip_table, self.gate_row, 2)
        self.ip_section.load([self.ip_table])
        
        #DNS configuration
        self.dns_table = gtk.Table(2, 2, False)
        self.dns_section = DefaultToggle(_("Automatic DNS server address"))
        self.dns_section.toggle_on = self.dns_toggle_off
        self.dns_section.toggle_off = self.dns_toggle_on

        self.master_row = self.__set_row(_("Primary DNS server address:"), 0, "dns")
        self.slave_row = self.__set_row(_("Slave DNS server address:"), 1, "dns")

        self.__table_attach(self.dns_table, self.master_row, 0)
        self.__table_attach(self.dns_table, self.slave_row, 1)
        self.dns_section.load([self.dns_table])
        
        # TODO UI change
        style.draw_background_color(self)
        style.set_table(self.ip_table)
        style.set_table(self.dns_table)

        # Init Settings
        self.ip = ["","",""]
        self.dns = ["",""]
        names = ["ip4", "netmask", "gw"]
        for n in names:
            setattr(self, n + "_flag", False)
        self.pack_start(self.ip_section, False, False)
        self.pack_start(self.dns_section, False, False)
        if link_local:
            self.pack_start(self.link_section, False, False)
        self.reset(connection)
        self.show_all()


    def __set_row(self, name, arg, types="ip"):
        label = Label(name, text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)

        label.set_can_focus(False)
        entry = IPV4Entry()
        if types == "ip":
            entry.connect("changed", self.set_ip_address, arg)
        else:
            entry.connect("changed", self.set_dns_address, arg)

        return (label, entry)

    def __table_attach(self, table, row_item, row):
        for i, item in enumerate(row_item):
            if i >=1:
                align = style.wrap_with_align(item, align="left")
                align.set_padding(0, 0, 1, 0)
            else:
                align = style.wrap_with_align(item)
                align.set_size_request(210, -1)
            table.attach(align, i, i +1, row, row + 1)
    
    def link_local_callback(self, widget):
        self._ip_group_sensitive(not widget.get_active())
        if widget.get_active():
            self.setting.method = 'link-local'
        else:
            self.setting.method = 'auto'
        self.settings_obj.set_button('save', True)

    def _ip_group_sensitive(self, state):
        self.ip_section.set_sensitive(state)
        self.dns_section.set_sensitive(state)
             
    def reset(self, connection):
        self.setting = connection.get_setting("ipv4")       
        if "ipv4" not in connection.settings_dict.iterkeys():
            log.debug("ipv4 not in settings dict, will create one")
            self.setting.method = "auto"
            connection.settings_dict["ipv4"] = self.setting.prop_dict

        if self.setting.method == 'link-local':
            self.link_section.switch.set_active(True)
        else:
            if self.setting.method == "auto":
                self.ip_section.set_active(True)
                    
            else:
                log.debug("get addresses", self.setting.addresses)
                self.ip_section.set_active(False)
                #self.set_group_sensitive("ip", True)
                if not self.setting.addresses == []:
                    #print self.setting.addresses[0][0]
                    addr, mask, gate = self.setting.addresses[0]
                    #self.ip_section.set_active(True)
                    self.addr_row[1].set_address(addr)
                    self.mask_row[1].set_address(mask)
                    self.gate_row[1].set_address(gate)
                    self.ip = self.setting.addresses[0]

        if self.setting.dns == []:
            self.dns_section.set_active(True)
        else:
            self.dns_section.set_active(False)
            if len(self.setting.dns) == 1:
                self.dns = self.setting.dns + [""]
            else:
                self.dns = self.setting.dns

            self.master_row[1].set_address(self.dns[0])
            
            if self.dns[1]:
                self.slave_row[1].set_address(self.dns[1])

        self.reset_table()

    def reset_table(self):
        pass
        self.queue_draw()

    def set_group_sensitive(self, group_name, sensitive):
        pass

    def set_ip_address(self, widget, content, index):
        # if you really want no gateway, just put a 0.0.0.0
        names = ["ip4", "netmask", "gw"]
        verbose_name = [_("IPv4"), _("Subnet Mask"), _("Gateway")]
        self.ip[index] = content

        if self.check_valid(names[index]):
            setattr(self, names[index] + "_flag", True)
            Dispatcher.set_tip(_("Valid %s address.")%verbose_name[index])
        else:
            setattr(self, names[index] + "_flag", False)
            Dispatcher.set_tip(_("Invalid %s address.")%verbose_name[index])

        ############
        # 检查ip、子网掩码、网关是否正确
        log.debug(widget, content, index)
        is_valid = True
        for n in names:
            if not getattr(self, "%s_flag"%n):
                is_valid = False
                break
        if is_valid:
            if self.setting.addresses:
                self.setting.clear_addresses()
            self.setting.add_address(self.ip)
        
        if self.settings_obj:
            self.settings_obj.ipv4_ip_is_valid = is_valid
            self.settings_obj.set_button("save", is_valid)

    def set_dns_address(self, widget, content, index):
        self.dns[index] = content
        names = ["master", "slaver"]
        dns = self.check_complete_dns()
        #print "set dns address:", dns, content
        if dns:
            is_valid = True
            self.setting.clear_dns()
            for d in dns:
                self.setting.add_dns(d)
        else:
            is_valid = False
            self.setting.clear_dns()

        if TypeConvert.is_valid_ip4(content):
            setattr(self, names[index] + "_flag", True)
        else:
            setattr(self, names[index] + "_flag", False)

        ############
        # 检查dns
        if self.settings_obj:
            self.settings_obj.ipv4_dns_is_valid = is_valid
            self.settings_obj.set_button("save", is_valid)

    def check_complete_dns(self):
        dns = []
        for address in self.dns:
            if TypeConvert.is_valid_ip4(address):
                dns.append(address)
            else:
                return dns
        return dns

    def check_valid(self, name):
        if name == "ip4":
            return TypeConvert.is_valid_ip4(self.ip[0])
        elif name == "netmask":
            return TypeConvert.is_valid_netmask(self.ip[1])
        elif name == "gw":
            return TypeConvert.is_valid_gw(self.ip[0], self.ip[1], self.ip[2])
    
    def dns_toggle_on(self):
        self.setting.clear_dns()
        self.set_group_sensitive("dns", False)
        ###########
        if self.settings_obj:
            self.settings_obj.ipv4_dns_is_valid = True
            self.settings_obj.set_button("save", True)

    def dns_toggle_off(self):
        self.set_group_sensitive("dns", True)
        master, slave = self.dns
        if master:
            self.master_row[1].emit('changed', master)
        if slave:
            self.slave_row[1].emit('changed', slave)
        # 统一调用shared_methods.Settings的set_button
        #if self.connection.check_setting_finish():
            #dns_is_valid = True
        #else:
            #dns_is_valid = False
        #if self.settings_obj:
            #self.settings_obj.ipv4_dns_is_valid = dns_is_valid
            #self.settings_obj.set_button("save", dns_is_valid)
        
    def ip_toggle_on(self):
        self.setting.clear_addresses()
        #self.ip = ["","",""]
        self.setting.method = 'auto'
        self.set_group_sensitive("ip", False)
        ########
        if self.settings_obj:
            self.settings_obj.ipv4_ip_is_valid = True
            self.settings_obj.set_button("save", True)

    def ip_toggle_off(self):
        self.setting.method = 'manual'
        addr, mask, gate = self.ip
        if addr:
            self.addr_row[1].emit("changed", addr)
        if mask:
            self.mask_row[1].emit("changed", mask)
        if gate:
            self.gate_row[1].emit("changed", gate)
        
        #if self.connection.check_setting_finish():
            #ip_is_valid = True
        #else:
            #ip_is_valid = False
        ## TODO 手动配置ip地址时，应该检查ip输入框的值是否合法，然后再设置保存按钮的状态
        #if self.settings_obj:
            #self.settings_obj.ipv4_ip_is_valid = ip_is_valid
            #self.settings_obj.set_button("save", ip_is_valid)


class IPV6Conf(gtk.VBox):
    ENTRY_WIDTH = 300
    def __init__(self, connection=None, set_button_callback=None, settings_obj=None, link_local=False):
        
        gtk.VBox.__init__(self)
        self.connection = connection 
        self.tab_name = _("IPv6 settings")
        self.set_button = set_button_callback
        # 新增settings_obj变量，用于访问shared_methods.Settings对象
        self.settings_obj = settings_obj

        # Ip configuration
        self.ip_table = gtk.Table(3, 2, False)
        #self.ip_section = SettingSection(_("Automatic get IP address"),text_size=CONTENT_FONT_SIZE, has_seperator=False, always_show=False, revert=True, label_right=True)
        self.link_section = Title(_("Link-Local Only"), toggle_callback = self.link_local_callback, label_right=True)
        self.ip_section = DefaultToggle(_("Automatic IP address"))
        self.ip_section.toggle_on = self.ip_toggle_off
        self.ip_section.toggle_off = self.ip_toggle_on

        self.addr_row = self.__set_row(_("IP Address:"), 0)
        self.mask_row = self.__set_row(_("Prefix:"), 1)
        self.gate_row = self.__set_row(_("Gateway:"), 2)
        
        self.__table_attach(self.ip_table, self.addr_row, 0)
        self.__table_attach(self.ip_table, self.mask_row, 1)
        self.__table_attach(self.ip_table, self.gate_row, 2)
        self.ip_section.load([self.ip_table])

        #DNS configuration
        self.dns_table = gtk.Table(2, 2, False)
        self.dns_section = DefaultToggle(_("Automatic DNS server address"))
        self.dns_section.toggle_on = self.dns_toggle_off
        self.dns_section.toggle_off = self.dns_toggle_on

        self.master_row = self.__set_row(_("Primary DNS server address:"), 0, "dns")
        self.slave_row = self.__set_row(_("Slave DNS server address:"), 1, "dns")

        self.__table_attach(self.dns_table, self.master_row, 0)
        self.__table_attach(self.dns_table, self.slave_row, 1)
        self.dns_section.load([self.dns_table])
        
        # TODO UI change
        style.draw_background_color(self)
        style.set_table(self.ip_table)
        style.set_table(self.dns_table)

        self.show_all()

        self.ip = ["", "", ""]
        self.dns = ["", ""]
        self.setting =None
        self.pack_start(self.ip_section, False, False)
        self.pack_start(self.dns_section, False, False)
        if link_local:
            self.pack_start(self.link_section, False, False)
        self.reset(connection)

        #if type(self.connection) is NMRemoteConnection:
            #Dispatcher.set_button("apply", True)
        #else:
            #if self.connection.check_setting_finish():
                #Dispatcher.set_button("save", True)
            #else:
                #Dispatcher.set_button("save", False)
    def link_local_callback(self, widget):
        self._ip_group_sensitive(not widget.get_active())
        if widget.get_active():
            self.setting.method = 'link-local'
        else:
            self.setting.method = 'auto'
        self.settings_obj.set_button('save', True)

    def _ip_group_sensitive(self, state):
        self.ip_section.set_sensitive(state)
        self.dns_section.set_sensitive(state)

    def __set_row(self, name, arg, types="ip"):
        label = Label(name, text_size=CONTENT_FONT_SIZE,
                               enable_select=False,
                               enable_double_click=False)
        entry = InputEntry()
        if types == "ip":
            #print "ip row changed"
            entry.entry.connect("changed", self.set_ip_address, arg)
        else:
            #print "dns row changed"
            entry.entry.connect("changed", self.set_dns_address, arg)
        entry.set_size(self.ENTRY_WIDTH, WIDGET_HEIGHT)

        return (label, entry)

    def __table_attach(self, table, row_item, row):
        for i, item in enumerate(row_item):
            if i >=1:
                align = style.wrap_with_align(item, align="left")
            else:
                align = style.wrap_with_align(item)
                align.set_size_request(210, -1)
            table.attach(align, i, i +1, row, row + 1)

    def reset_table(self):
        pass

    def reset(self, connection):
        self.setting = connection.get_setting("ipv6")       

        if "ipv6" not in connection.settings_dict.iterkeys():
            log.debug("ipv6 not in settings dict, will create one")
            self.setting.method = "auto"
            connection.settings_dict["ipv6"] = self.setting.prop_dict
        
        #  FIXME: ipv6 method刚开始为None并且还会记住上次操作,应该每次开始时为auto。
        if self.setting.method == 'link-local':
            self.link_section.switch.set_active(True)
        else:
            if self.setting.method == "auto" or self.setting.method is None:
                self.ip_section.set_active(True)
                self.set_group_sensitive("ip", False)
                
            else:
                self.ip_section.set_active(False)
                self.set_group_sensitive("ip", True)
                if not self.setting.addresses == []:
                    addr, mask, gate = self.setting.addresses[0]

                    self.addr_row[1].set_text(addr)
                    self.mask_row[1].set_text(mask)
                    self.gate_row[1].set_text(gate)
                    self.ip = self.setting.addresses

        if self.setting.dns == []:
            self.dns_section.set_active(True)
            self.set_group_sensitive("dns", False)
        else:
            #self.manual_dns.set_active(True)
            self.set_group_sensitive("dns", True)
            self.master_row[1].set_text(self.setting.dns[0])
            self.dns = self.setting_dns +[""]
            if len(self.setting.dns) > 1:
                self.slave_row[1].set_text(self.setting.dns[1])
                self.dns = self.setting.dns

        self.reset_table()

    def set_group_sensitive(self, group_name, sensitive):
        pass
        #if group_name is "ip":
            #self.addr_label.set_sensitive(sensitive)
            #self.mask_label.set_sensitive(sensitive)
            #self.gate_label.set_sensitive(sensitive)
            #self.addr_entry.set_sensitive(sensitive)
            #self.mask_entry.set_sensitive(sensitive)
            #self.gate_entry.set_sensitive(sensitive)
            #if not sensitive:
                #self.addr_entry.set_text("")
                #self.mask_entry.set_text("")
                #self.gate_entry.set_text("")
        #elif group_name is "dns":
            #self.master_dns.set_sensitive(sensitive)
            #self.slave_dns.set_sensitive(sensitive)
            #self.master_entry.set_sensitive(sensitive)
            #self.slave_entry.set_sensitive(sensitive)
            #if not sensitive:
                #self.master_entry.set_text("")
                #self.slave_entry.set_text("")

    def set_ip_address(self, widget, content, index):
        names = ["ip6", "netmask", "gw"]
        self.ip[index] = content
        if self.check_valid(names[index]):
            setattr(self, names[index] + "_flag", True)
        else:
            setattr(self, names[index] + "_flag", False)

        if self.check_valid("gw"):
            #print "update ip4"
            if self.setting.addresses:
                self.setting.clear_addresses()
            self.setting.add_address(self.ip)
        else:
            self.setting.clear_addresses()

        ############
        # 检查ip、子网掩码、网关是否正确
        for n in names:
            is_valid = self.check_valid(n)
            print "--------------------", n, is_valid
            if not is_valid:
                break
        if self.settings_obj:
            self.settings_obj.ipv6_ip_is_valid = is_valid
            self.settings_obj.set_button("save", is_valid)

    def set_dns_address(self, widget, content, index):
        self.dns[index] = content
        names = ["master", "slaver"]
        dns = self.check_complete_dns()
        if dns:
            is_valid = True
            self.setting.clear_dns()
            for d in dns:
                self.setting.add_dns(d)
        else:
            is_valid = False
            self.setting.clear_dns()

        if TypeConvert.is_valid_ip6(content):
            setattr(self, names[index] + "_flag", True)
        else:
            setattr(self, names[index] + "_flag", False)

        ############
        # 检查dns
        if self.settings_obj:
            self.settings_obj.ipv6_dns_is_valid = is_valid
            self.settings_obj.set_button("save", is_valid)
            
    def check_complete_dns(self):
        dns = []
        for address in self.dns:
            if TypeConvert.is_valid_ip6(address):
                dns.append(address)
            else:
                return dns
        return dns

    def check_valid(self, name):
        if name == "ip6":
            return TypeConvert.is_valid_ip6(self.ip[0])
        # FIXME 应该用ipv6的网关检查
        elif name == "netmask":
            #return TypeConvert.is_valid_netmask(self.ip[1])
            return self.ip[1].isdigit()
        elif name == "gw":
            #return TypeConvert.is_valid_gw(self.ip[0], self.ip[1], self.ip[2])
            return TypeConvert.is_valid_ip6(self.ip[2])

    def dns_toggle_on(self):
        self.setting.clear_dns()
        #self.dns = ["",""]
        self.set_group_sensitive("dns", False)
        ###########
        if self.settings_obj:
            self.settings_obj.ipv6_dns_is_valid = True
            self.settings_obj.set_button("save", True)

    def dns_toggle_off(self):
        self.set_group_sensitive("dns", True)
        master, slave = self.dns
        if master:
            self.master_row[1].entry.emit('changed', master)
        if slave:
            self.slave_row[1].entry.emit('changed', slave)
        #if self.connection.check_setting_finish():
            #dns_is_valid = True
        #else:
            #dns_is_valid = False
        ###########
        #if self.settings_obj:
            #self.settings_obj.ipv6_dns_is_valid = dns_is_valid
            #self.settings_obj.set_button("save", dns_is_valid)
    
    def ip_toggle_on(self):
        self.setting.clear_addresses()
        #self.ip = ["","",""]
        self.setting.method = 'auto'
        self.set_group_sensitive("ip", False)
        ########
        if self.settings_obj:
            self.settings_obj.ipv6_ip_is_valid = True
            self.settings_obj.set_button("save", True)

    def ip_toggle_off(self):
        self.setting.method = 'manual'
        self.set_group_sensitive("ip", True)
        addr, mask, gate = self.ip
        if addr:
            self.addr_row[1].entry.emit("changed", addr)
        if mask:
            self.mask_row[1].entry.emit("changed", mask)
        if gate:
            self.gate_row[1].entry.emit("changed", gate)
        #if self.connection.check_setting_finish():
            #ip_is_valid = True
        #else:
            #ip_is_valid = False
        ## TODO 手动配置ip地址时，应该检查ip输入框的值是否合法，然后再设置保存按钮的状态
        #if self.settings_obj:
            #self.settings_obj.ipv6_ip_is_valid = ip_is_valid
            #self.settings_obj.set_button("save", ip_is_valid)
