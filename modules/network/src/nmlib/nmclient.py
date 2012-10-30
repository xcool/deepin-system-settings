#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
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

import gobject
from nmobject import NMObject
from nm_utils import TypeConvert
# from nmdevice import NMDevice
# from nm_active_connection import NMActiveConnection
import traceback
from nmcache import cache

class NMClient(NMObject):
    '''NMClient'''
        
    __gsignals__  = {
            "device-added":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str, )),
            "device-removed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (str,)),
            "state-changed":(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_UINT, )),
            "permisson-changed":(gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE, (gobject.TYPE_UINT,gobject.TYPE_UINT))
            }

    def __init__(self):
        NMObject.__init__(self, "/org/freedesktop/NetworkManager", "org.freedesktop.NetworkManager")
        self.manager_running = False
        self.init_nmobject_with_properties()

        self.bus.add_signal_receiver(self.permisson_changed_cb, dbus_interface = self.object_interface, signal_name = "CheckPermissions")
        self.bus.add_signal_receiver(self.device_added_cb, dbus_interface = self.object_interface, signal_name = "DeviceAdded")
        self.bus.add_signal_receiver(self.device_removed_cb, dbus_interface = self.object_interface, signal_name = "DeviceRemoved")
        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = self.object_interface, signal_name = "PropertiesChanged")
        self.bus.add_signal_receiver(self.state_changed_cb,dbus_interface = self.object_interface, signal_name = "StateChanged")


    def get_devices(self):
        '''return father device objects'''
        return map(lambda x: cache.getobject(x), TypeConvert.dbus2py(self.dbus_method("GetDevices")))

    def get_wired_devices(self):
        return filter(lambda x:x.get_device_type() == 1, self.get_devices())

    def get_wired_device(self):
        return self.get_wired_devices()[0]

    def get_wireless_devices(self):
        return filter(lambda x:x.get_device_type() == 2, self.get_devices())

    def get_wireless_device(self):
        return self.get_wireless_devices()[0]

    def get_modem_devices(self):
        return filter(lambda x:x.get_device_type() == 8, self.get_devices())

    def get_modem_device(self):
        return self.get_modem_devices()[0]

    def get_device_by_iface(self, iface):
        return cache.getobject(self.dbus_method("GetDeviceByIpIface", iface))

    def activate_connection(self, connection_path, device_path, specific_object_path):
        '''return active_connection_path object'''
        return cache.getobject(self.dbus_method("ActivateConnection", connection_path, device_path, specific_object_path))

    def activate_connection_async(self, connection_path, device_path, specific_object_path):
        try:
            self.dbus_interface.ActivateConnection(connection_path, device_path, specific_object_path,                                                                                reply_handler = self.activate_finish, error_handler = self.activate_error)
        except:
            traceback.print_exc()

    def activate_finish(self, active_connection):
        return cache.getobject(active_connection)
    
    def activate_error(self, error):
        print "activate connection failed!\n"
        print error

    def add_and_activate_connection(self, connection_path, device_path, specific_object_path):
        return self.dbus_method("AddAndActivateConnection", connection_path, device_path, specific_object_path)

    def add_and_activate_connection_async(self, connection_path, device_path, specific_object_path):
        try:
            self.dbus_interface.AddAndActivateConnection(connection_path, device_path, specific_object_path,
                                             reply_handler = self.add_activate_finish, error_handler = self.add_activate_error)
        except:
            traceback.print_exc()
        

    def add_activate_finish(self, *reply):
        return reply

    def add_activate_error(self, *error):
        pass

    def deactive_connection(self, active_object_path):
        return self.dbus_method("DeactivateConnection", active_object_path)

    def deactive_connection_async(self, active_object_path):
        try:
            self.dbus_interface.DeactivateConnection(active_object_path, reply_handler = self.deactive_finish, 
                                                     error_handler = self.deactive_error)
        except:
            traceback.print_exc()

    def deactive_finish(self):
        print "devactive connection finish!\n"

    def deactive_error(self, error):
        print "devactive connection failed!\n"
        print error

    def nm_client_sleep(self, sleep_flag):
        return self.dbus_method("Sleep", sleep_flag)

    def get_permissions(self):
        return self.dbus_method("GetPermissions")

    def get_permission_result(self, permission):
        return self.get_permissions()[permission]

    def networking_set_enabled(self, enabled):
        return self.dbus_method("Enable", enabled)
            
    def networking_get_enabled(self):
        return self.properties["NetworkingEnabled"]

    def wireless_get_enabled(self):
        return self.properties["WirelessEnabled"]

    def wireless_set_enabled(self, enabled):
        self.set_property("WirelessEnabled", enabled)
    
    def wireless_hardware_get_enabled(self):
        return self.properties["WirelessHardwareEnabled"]

    def wwan_get_enabled(self):
        return self.properties["WwanEnabled"]

    def wwan_set_enabled(self, enabled):
        self.set_property("WwanEnabled", enabled)

    def wwan_hardware_get_enabled(self):
        return self.properties["WwanHardwareEnabled"]

    def wimax_get_enabled(self):
        return self.properties["WimaxEnabled"]

    def wimax_set_enabled(self, enabled):
        self.set_property("WimaxEnabled", enabled)

    def wimax_get_hardware_enabled(self):
        return self.properties["WimaxHardwareEnabled"]

    def get_version(self):
        return self.properties["Version"]

    def get_state(self):
        return self.properties["State"]

    def get_manager_running(self):
        return self.manager_running

    def get_active_connections(self):
        '''return active connections objects'''
        return map(lambda x: cache.getobject(x), self.properties["ActiveConnections"])

    def get_vpn_active_connection(self):
        return filter(lambda x:x.get_vpn() == 1, self.get_active_connections())[0]

    def get_wired_active_connection(self):
        return filter(lambda x:x.get_devices()[0] == self.get_wired_device(), self.get_active_connections())[0]

    def get_wireless_active_connection(self):
        return filter(lambda x:x.get_devices()[0] == self.get_wireless_device(), self.get_active_connections())[0]

    def get_pppoe_active_connection(self):
        pass

    def get_gsm_active_connection(self):
        pass

    def get_cdma_active_connection(self):
        # return filter(lambda x:NMActiveConnection(x).get_devices()[0] == self.get_cdma_device(), self.get_active_connections())[0]
        pass

    ###Signals ###
    def device_added_cb(self, device_object_path):
        self.emit("device-added", device_object_path)

    def device_removed_cb(self, device_object_path):
        self.emit("device-removed", device_object_path)

    def permisson_changed_cb(self):
        self.emit("permission-changed")

    def state_changed_cb(self, state):
        self.emit("state-changed", TypeConvert.dbus2py(state))
    
    def properties_changed_cb(self, prop_dict):
        # self.emit("properties-changed", TypeConvert.dbus2py(prop_dict))
        pass

nmclient = NMClient()

if __name__ == "__main__":
    from nmobject import dbus_loop
    
    # print nmclient.get_state()
    # nmclient.networking_set_enabled(False)

    # nmclient.update_properties()
    # print nmclient.get_state()

    # nmclient.networking_set_enabled(True)
    # nmclient.update_properties()
    # print nmclient.get_state()

    nmclient.dbus_proxy.StateChanged(10)

    dbus_loop.run()