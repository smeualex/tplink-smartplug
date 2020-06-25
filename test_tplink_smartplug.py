import sys
import json
import time
import importlib

tplink_comm = importlib.import_module("tplink_smartplug_comm")

settings = { }
def loadSettings():
    global settings
    with open('settings-test.json') as settingsFile:
        settings = json.load(settingsFile)

# only for debug
def printTplinkData(cmd):
    print(" > SENDING: ", cmd)
    print("--------------------------------------------------------------------")
    tplink=settings['tplink-smartplug']
    data = tplink_comm.sendCommand(
        cmd, 
        tplink['ip'], 
        tplink['port'], 
        tplink['request-timeout-s']
    )
    recvJson = json.loads(data)
    print("")
    print(" > RECEIVED: ")
    print(json.dumps(recvJson, indent=4))

    if(cmd == "info"):
        try:
            print("\t RSSI     = " + str(recvJson['system']['get_sysinfo']['rssi']))
            print("\t LED OFF  = " + str(recvJson['system']['get_sysinfo']['led_off']))
            print("\t RELAY    = " + str(recvJson['system']['get_sysinfo']['relay_state']))
            print("\t ON TIME  = " + str(recvJson['system']['get_sysinfo']['on_time']))
            print("\t ERROR    = " + str(recvJson['get_sysinfo']['on_time']))
        except json.JSONDecodeError as err:
            print ("[tplink_smartplug] - JSON Decode Error: ", err)
        except KeyError as err:
            print ("[tplink_smartplug] - JSON Key Error: " , err)
    print("")

def main():
    print("settings before:", settings)
    loadSettings()
    print("settings after:", settings)
    [printTplinkData(cmd) for cmd in settings['test']['command-list']]

if __name__ == "__main__":
    main()
