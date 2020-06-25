#!/usr/bin/env python3
#
# TP-Link Wi-Fi Smart Plug Protocol Client
# For use with TP-Link HS-100 or HS-110
#
# by Lubomir Stroetmann
# Copyright 2016 softScheck GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import time
import socket
import argparse
import datetime
from struct import pack

version = 0.4

# Check if hostname is valid
def validHostname(hostname):
    try:
        socket.gethostbyname(hostname)
    except socket.error:
        parser.error("Invalid hostname.")
    return hostname

# Check if port is valid
def validPort(port):
        try:
            port = int(port)
        except ValueError:
            parser.error("Invalid port number.")

        if ((port <= 1024) or (port >65535)) :
            parser.error("Invalid port number.")

        return port


# Predefined Smart Plug Commands
# For a full list of commands, consult tplink_commands.txt
commands = {        
            'info'          : '{"system":{"get_sysinfo":{}}}',
            'on'            : '{"system":{"set_relay_state":{"state":1}}}',
            'off'           : '{"system":{"set_relay_state":{"state":0}}}',
            'ledoff'        : '{"system":{"set_led_off":{"off":1}}}',
            'ledon'         : '{"system":{"set_led_off":{"off":0}}}',
            'cloudinfo'     : '{"cnCloud":{"get_info":{}}}',
            'wlanscan'      : '{"netif":{"get_scaninfo":{"refresh":0}}}',
            'time'          : '{"time":{"get_time":{}}}',
            'schedule'      : '{"schedule":{"get_rules":{}}}',
            'countdown'     : '{"count_down":{"get_rules":{}}}',
            'antitheft'     : '{"anti_theft":{"get_rules":{}}}',
            'reboot'        : '{"system":{"reboot":{"delay":1}}}',
            'reset'         : '{"system":{"reset":{"delay":1}}}',
            'energy'        : '{"emeter":{"get_realtime":{}}}',
            'stats_month'   : '{"emeter":{""get_monthstat":{"year":YYYY}}}',
            'stats_day'     : '{"emeter":{"get_daystat":{"month":MMMM,"year":YYYY}}}'
}

# Encryption and Decryption of TP-Link Smart Home Protocol
# XOR Autokey Cipher with starting key = 171
# Python 3.x Version
if sys.version_info[0] > 2:
    def encrypt(string):
        key = 171
        result = pack('>I', len(string))
        for i in string:
            a = key ^ ord(i)
            key = a
            result += bytes([a])
        return result

    def decrypt(string):
        key = 171
        result = ""
        for i in string:
            a = key ^ i
            key = i
            result += chr(a)
        return result

# Python 2.x Version
else:
    def encrypt(string):
        key = 171
        result = pack('>I', len(string))
        for i in string:
            a = key ^ ord(i)
            key = a
            result += chr(a)
        return result

    def decrypt(string):
        key = 171
        result = ""
        for i in string:
            a = key ^ ord(i)
            key = ord(i)
            result += chr(a)
        return result

def getData(commandName, ip, port, timeout):
    # Send command and receive reply
    try:
        cmd = commands[commandName]

        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.settimeout(int(timeout))
        sock_tcp.connect((ip, port))
        sock_tcp.settimeout(None)
        sock_tcp.send(encrypt(cmd))
        data = sock_tcp.recv(2048)
        sock_tcp.close()

        decrypted = decrypt(data[4:])

        return decrypted

    except socket.error:
        quit("Could not connect to host " + ip + ":" + str(port))

def setUpCmdParams():
    """
    Set up parameters in commands:
        'stats_month': '{"emeter":{""get_monthstat":{"year":XXXXXXXX}}}' 
            - year will have current year
    """
    # set the current year
    currentYear = str(datetime.datetime.now().year)
    commands['stats_month'] = commands['stats_month'].replace("YYYY", currentYear)

    #set the current month and year
    currentMonth = str(datetime.datetime.now().month)
    commands['stats_day'] = commands['stats_day'].replace("YYYY", currentYear)
    commands['stats_day'] = commands['stats_day'].replace("MMMM", currentMonth)

def sendCommand(cmd, ip, port, timeout):
    setUpCmdParams()
    tplinkData = getData(cmd, ip, port, timeout)

    return tplinkData
