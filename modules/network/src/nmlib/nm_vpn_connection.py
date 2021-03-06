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
from nm_active_connection import NMActiveConnection
from nmcache import get_cache
try:
    from network.src.nmlib.nm_dispatcher import nm_events
except:
    from nm_dispatcher import nm_events
#try:
    #from network.src.helper import event_manager
#except:
    #from helper import event_manager

#from nm_dispatcher import nm_events

class NMVpnConnection(NMActiveConnection):
    '''NMVpnConnection'''
        
    __gsignals__  = {
            "vpn-state-changed":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_UINT)),
            "vpn-connected":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            "vpn-connecting":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            "vpn-disconnected":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            "vpn-user-disconnect":(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
            }

    def __init__(self, vpn_connection_object_path):
        NMActiveConnection.__init__(self, vpn_connection_object_path, "org.freedesktop.NetworkManager.VPN.Connection")

        self.bus.add_signal_receiver(self.vpn_state_changed_cb, dbus_interface = "org.freedesktop.NetworkManager.VPN.Connection",
                                     path = self.object_path, signal_name = "VpnStateChanged")

        self.bus.add_signal_receiver(self.properties_changed_cb, dbus_interface = "org.freedesktop.NetworkManager.VPN.Connection",
                                     path = self.object_path, signal_name = "PropertiesChanged")

        self.prop_list = ["VpnState", "Banner"]
        self.init_nmobject_with_properties()

    def get_banner(self):
        return self.properties["Banner"]

    def get_vpnstate(self):
        return self.properties["VpnState"]

    ###Signals###
    def vpn_state_changed_cb(self, state, reason):
        #print state, reason
        self.init_nmobject_with_properties()
        nm_remote_settings = get_cache().getobject("/org/freedesktop/NetworkManager/Settings")
        if state in [1, 2, 3, 4]:
            #self.emit("vpn-connecting")
            nm_events.emit('vpn-connecting', self.object_path)
            print "vpn-connecting"
        elif state == 5:
            #self.emit("vpn-connected")
            #print "vpn-connected"
            nm_events.emit('vpn-connected', self.object_path)
            conn_uuid = get_cache().getobject(self.object_path).get_connection().settings_dict["connection"]["uuid"]
            try:
                priority = int(nm_remote_settings.cf.getint("conn_priority", conn_uuid)) + 1
            except:
                priority = 1

            nm_remote_settings.cf.set("conn_priority", conn_uuid, priority)
            nm_remote_settings.cf.write(open(nm_remote_settings.config_file, "w"))
        #elif state == 7:
            #nm_events.emit('vpn-user-disconnect', self.object_path)
        else:
            nm_events.emit('vpn-disconnected', self.object_path)
            


if __name__ == "__main__":
    pass
