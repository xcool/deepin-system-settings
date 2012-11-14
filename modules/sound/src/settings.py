#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
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

import core
import device
import dbus
import traceback

#Channel positions
#
#0 : Mono; 1 : Front left; 2 : Front right; 3 : Front center; 4 : Rear center; 5 : Rear left
#6 : Rear right; 7 : LFE; 8 : Front left of center; 9 : Front right of center; 10 : Side left
#11 : Side right; 12 : Aux 0; 13 : Aux 1; 14 : Aux 2; 15 : Aux 3
#16 : Aux 4; 17 : Aux 5; 18 : Aux 6; 19 : Aux 7; 20 : Aux 8
#21 : Aux 9; 22 : Aux 10; 23 : Aux 11; 24 : Aux 12; 25 : Aux 13
#26 : Aux 14; 27 : Aux 15; 28 : Aux 16; 29 : Aux 17; 30 : Aux 18
#31 : Aux 19; 32 : Aux 20; 33 : Aux 21; 34 : Aux 22; 35 : Aux 23
#36 : Aux 24; 37 : Aux 25; 38 : Aux 26; 39 : Aux 27; 40 : Aux 28
#41 : Aux 29; 42 : Aux 30; 43 : Aux 31; 44 : Top center; 45 : Top front left
#46 : Top front right; 47 : Top front center; 48 : Top rear left; 49 : Top rear right; 50 : Top rear center 
#
#Device states
#
#    0 : Running, the device is being used by at least one non-corked stream.
#    1 : Idle, the device is active, but no non-corked streams are connected to it.
#    2 : Suspended, the device is not in use and may be currently closed. 

DEVICE_STATE_RUNNING = 0
DEVICE_STATE_IDLE = 1
DEVICE_STATE_SUSPENDED = 2

FULL_VOLUME_VALUE = 65536   # the 100% volume
MAX_VOLUME_VALUE = 99957    # the max volume

try:
    PA_CORE = core.Core()
    PA_SINK_LIST = PA_CORE.get_sinks()
    PA_SOURCE_LIST = PA_CORE.get_sources()
    PA_CARD_LIST = PA_CORE.get_cards()
except:
    print "PulseAudio dbus error: ---------------------------------------------"
    traceback.print_exc()
    PA_CORE = None
    PA_SINK_LIST = []
    PA_SOURCE_LIST = []
    PA_CARD_LIST = []

CURRENT_SINK = None
CURRENT_SOURCE = None

PA_CARDS = {}           # All Device that this Card container.
if PA_CORE:
    if PA_CARD_LIST:
        CURRENT_CARD = PA_CARD_LIST[0]
    else:
        CURRENT_CARD = None
    for card in PA_CARD_LIST:
        PA_CARDS[card] = {"sink": [], "source": []}

PA_INPUT_DEVICE = {}    # All Sources Device
PA_INPUT_CHANNELS = {}  # Each Sources' Channels
PA_OUTPUT_DEVICE = {}   # All Sinks Device
PA_OUTPUT_CHANNELS = {} # Each Sinks' Channel

LEFT_CHANNELS = [1, 5, 8, 10, 45, 48]
RIGHT_CHANNELS = [2, 6, 9, 11, 46, 49]
for sink in PA_SINK_LIST:
    dev = device.Device(sink)
    if not dev.get_ports(): # if the device does not have any ports, ignore it
        continue
    PA_OUTPUT_DEVICE[sink] = dev
    dev_channels = {}
    channels = PA_OUTPUT_DEVICE[sink].get_channels()
    dev_channels["channel_num"] = len(channels)
    dev_channels["left"] = []
    dev_channels["right"] = []
    dev_channels["other"] = []
    i = 0
    while i < dev_channels["channel_num"]:
        if channels[i] in LEFT_CHANNELS:
            dev_channels["left"].append(i)
        elif channels[i] in RIGHT_CHANNELS:
            dev_channels["right"].append(i)
        else:
            dev_channels["other"].append(i)
        i += 1
    try:
        card = dev.get_card()
        if card == CURRENT_CARD and CURRENT_SINK is None:
            CURRENT_SINK = sink
        PA_CARDS[card]["sink"].append(dev)
    except:
        traceback.print_exc()
    PA_OUTPUT_CHANNELS[sink] = dev_channels

for source in PA_SOURCE_LIST:
    dev = device.Device(source)
    if not dev.get_ports(): # if the device does not have any ports, ignore it
        continue
    PA_INPUT_DEVICE[source] = dev
    dev_channels = {}
    channels = PA_INPUT_DEVICE[source].get_channels()
    dev_channels["channel_num"] = len(channels)
    dev_channels["left"] = []
    dev_channels["right"] = []
    dev_channels["other"] = []
    i = 0
    while i < dev_channels["channel_num"]:
        if channels[i] in LEFT_CHANNELS:
            dev_channels["left"].append(i)
        elif channels[i] in RIGHT_CHANNELS:
            dev_channels["right"].append(i)
        else:
            dev_channels["other"].append(i)
        i += 1
    try:
        card = dev.get_card()
        if card == CURRENT_CARD and CURRENT_SOURCE is None:
            CURRENT_SOURCE = source
        PA_CARDS[card]["source"].append(dev)
    except:
        traceback.print_exc()
    PA_INPUT_CHANNELS[source] = dev_channels

def get_object_property_list(obj):
    '''
    get DBus Object PropertyList
    @param obj: a PulseAudio DBus Object object
    @return: a dict type
    '''
    prop_list = obj.get_property_list()
    prop = {}
    if not prop_list:
        return prop
    for k in prop_list:
        prop[k] = str(bytearray(prop_list[k]))
    return prop

def get_volume(dev):
    '''
    get device volume
    @param dev: a device path
    @return: a int type
    '''
    return max(device.Device(dev).get_volume())

def get_mute(dev):
    '''
    get device whether mute
    @param dev: a device path
    @return: a bool type
    '''
    return device.Device(dev).get_mute()

def get_port_list(dev):
    '''
    get device port list
    @param dev: a device path
    @return: a list contain some tuple which format :(device_port, ...), index
    '''
    d = device.Device(dev)
    ports = d.get_ports()
    if not ports:
        return []
    back = []
    active_port = d.get_active_port()
    i = 0
    n = 0
    for port in ports:
        p = device.DevicePort(port)
        if port == active_port:
            n = i
        back.append(p)
        i += 1
    return (back, n)
    

#print PA_INPUT_CHANNELS
#print PA_INPUT_DEVICE
#print PA_OUTPUT_CHANNELS
#print PA_OUTPUT_DEVICE
#print PA_CARDS
