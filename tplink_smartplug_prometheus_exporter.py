#!/usr/bin/env python3

import sys
import json
import time
import importlib

from prometheus_client import CollectorRegistry, Gauge, Summary, start_http_server

PROMETHEUS_EXPORT_PORT=9130

voltageGauge     = Gauge('tplink_voltage_mv',     'Voltage, Volts')
currentGauge     = Gauge('tplink_current_ma',     'Current, Amps' )
powerGauge       = Gauge('tplink_power_mw',       'Power, Watts'  )
totalWattsSum    = Gauge('tplink_total_power_wh', 'TotalPower, KiloWattHour')

def exportPowerInfoToPrometheus(data):
    try:
        jsonData = json.loads(data)
        voltageGauge.set      (jsonData["emeter"]["get_realtime"]["voltage_mv"] / 1000);
        currentGauge.set      (jsonData["emeter"]["get_realtime"]["current_ma"] / 1000);
        powerGauge.set        (jsonData["emeter"]["get_realtime"]["power_mw"  ] / 1000);
        totalWattsSum.set     (jsonData["emeter"]["get_realtime"]["total_wh"  ] / 1000);
    except json.JSONDecodeError as err:
        quit ("[tplink_smartplug] - JSON Decode Error: ", err)

# only for debug
def printTplinkData(data):
    recvJson = json.loads(data)
    print("Received data: ")
    print(json.dumps(recvJson, indent=4))

def main():
    ###############################################################################################
    # start http server
    start_http_server(PROMETHEUS_EXPORT_PORT)
    # import the tplink comm module
    tplink_comm = importlib.import_module("tplink_smartplug_comm")
    
    while(True):
        # get the data
        #tplink_comm.sendCommand("stats_day")
        exportPowerInfoToPrometheus(tplink_comm.sendCommand("energy"))
        time.sleep(10)

if __name__ == '__main__':
    main()

