# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2008 Tadas Dailyda <tadas at dailyda dot com>
#
# Licensed under the GNU General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import gobject
import dbus
from SignalTracker import SignalTracker

class OdsBase(dbus.proxies.Interface, gobject.GObject):

        def __init__(self, service_name, obj_path):
                self.bus = dbus.SessionBus()
                self._signals = SignalTracker()

                service = self.bus.get_object("org.openobex", obj_path)
                gobject.GObject.__init__(self)
                dbus.proxies.Interface.__init__(self, service, service_name)

        def DisconnectAll(self):
                self._signals.DisconnectAll()

        def Handle(self, signame, handler):
                self._signals.Handle("dbus", self.bus, handler, signame, self.dbus_interface, None, self.object_path)

        def GHandle(self, *args):
                self._signals.Handle("gobject", self, *args)
