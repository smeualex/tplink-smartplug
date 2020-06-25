#!/usr/bin/env python3

import os
import sys
import json
import time
import importlib

from prometheus_client import CollectorRegistry, Gauge, Summary, start_http_server

settings = { }

# Prometheus - power info gauges
voltageGauge     = Gauge('tplink_voltage_mv',     'Voltage, Volts')
currentGauge     = Gauge('tplink_current_ma',     'Current, Amps' )
powerGauge       = Gauge('tplink_power_mw',       'Power, Watts'  )
totalWattsSum    = Gauge('tplink_total_power_wh', 'TotalPower, KiloWattHour')

# Prometheus - State info gauges
rssiGauge        = Gauge('tplink_rssi_db',        'WiFi Signal Strength, Decibels')
ledStateGauge    = Gauge('tplink_led_state',      'LED State, OnOff')
relayStateGauge  = Gauge('tplink_relay_state',    'Relay State, OnOff')
powerOnTimeGauge = Gauge('tplink_uptime',         'Uptime, Seconds')

def exportPowerInfoToPrometheus(data):
    try:
        recvJson = json.loads(data)
        voltageGauge.set      (recvJson["emeter"]["get_realtime"]["voltage_mv"] / 1000)
        currentGauge.set      (recvJson["emeter"]["get_realtime"]["current_ma"] / 1000)
        powerGauge.set        (recvJson["emeter"]["get_realtime"]["power_mw"  ] / 1000)
        totalWattsSum.set     (recvJson["emeter"]["get_realtime"]["total_wh"  ] / 1000)
    except json.JSONDecodeError as err:
        quit ("[tplink_smartplug] - JSON Decode Error: ", err)
    except KeyError as err:
            print ("[tplink_smartplug] - JSON Key Error: " , err)

def exportStatesToPrometheus(data):
    try:
        recvJson = json.loads(data)
        rssiGauge.set(recvJson['system']['get_sysinfo']['rssi'])
        
        if(recvJson['system']['get_sysinfo']['led_off'] == 0):
            ledStateGauge.set(1)
        else:
            ledStateGauge.set(0)

        relayStateGauge.set(recvJson['system']['get_sysinfo']['relay_state'])

        powerOnTimeGauge.set(recvJson['system']['get_sysinfo']['on_time'])
    except json.JSONDecodeError as err:
        print ("[tplink_smartplug] - JSON Decode Error: ", err)
    except KeyError as err:
        print ("[tplink_smartplug] - JSON Key Error: " , err)

def loadSettings(logSettings):
    global settings

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    with open(os.path.join(__location__, 'settings.json')) as settingsFile:
        settings = json.load(settingsFile)

    if(logSettings == True):
        print(" > Settings used: ", settings)

def main():
    loadSettings(True)
    tplink_settings     = settings['tplink_smartplug']
    prometheus_settings = settings['prometheus']

    start_http_server(prometheus_settings['export-port'])

    tplink_comm = importlib.import_module("tplink_smartplug_comm")
    while(True):
        exportPowerInfoToPrometheus( 
            tplink_comm.sendCommand(
                "energy",
                tplink_settings['ip'], 
                tplink_settings['port'], 
                tplink_settings['request_timeout_s']
            )
        )
        
        exportStatesToPrometheus(
            tplink_comm.sendCommand(
                "info",
                tplink_settings['ip'],
                tplink_settings['port'],
                tplink_settings['request_timeout_s']
            )
        )

        time.sleep(prometheus_settings['export-frequency-s'])

if __name__ == '__main__':
    main()

