# TP-Link WiFi SmartPlug Client and Prometheus exporter

## Project forked form [here](https://github.com/softScheck/tplink-smartplug)
Used as a base for exporting the HS110 data to Prometheus.
For the full, original readme please check the [Tplink Smartplug project](https://github.com/softScheck/tplink-smartplug)

For the full story, see [Reverse Engineering the TP-Link HS110](https://www.softscheck.com/en/reverse-engineering-tp-link-hs110/)

## tplink_smartplug_comm.py ##

A python client for the proprietary TP-Link Smart Home protocol to control TP-Link HS100 and HS110 WiFi Smart Plugs.
The SmartHome protocol runs on TCP port 9999 and uses a trivial XOR autokey encryption that provides no security. 

There is no authentication mechanism and commands are accepted independent of device state (configured/unconfigured).


Commands are formatted using JSON, for example:

  `{"system":{"get_sysinfo":null}}`

Instead of `null` we can also write `{}`. Commands can be nested, for example:

  `{"system":{"get_sysinfo":null},"time":{"get_time":null}}`

A full list of commands is provided in [tplink-smarthome-commands.txt](tplink-smarthome-commands.txt).

## tplink_smartplug_prometheus_exporter.py ##

Python which calls the `tplink_smartplug_comm.py` client, parses the data and sends them to Prometheus.
It's called by `start.sh` which in turn can be added to a systemd service for autostart on system boot.

For the moment it exports only energy related data.

The settings are got from `settings.json`

## settings.json ##

Main settings of the prometheus exporter script.
```json
{
    "prometheus":{
        "export-port": 1234,
        "export-frequency-s": 10
    },
    "tplink_smartplug":{
        "ip":"192.168.1.10",
        "port":9999,
        "request_timeout_s": 2
    }
}
```


| Property                             | Description |
|--------------------------------------|-------------|
| prometheus.export-port               | Port on which the http server will be started. Prometheus must be configured to this address|
| prometheus.export-frequency-s        | Export frequency in seconds. Sleep duration after a request is finished.|
| tplink_smartplug.ip                  | Smartplug's ip address            |
| tplink_smartplug.port                | Smartplug's port. Default is 9999 |
| tplink_smartplug.request_timeout_s   | Timout for waiting for an answer  |

## Commands ##

| Command     | Description                                            |
|-------------|--------------------------------------------------------|
| on          | Turns on the plug                                      |
| off         | Turns off the plug                                     |
| info        | Returns device info                                    |
| cloudinfo   | Returns cloud connectivity info                        |
| wlanscan    | Scan for nearby access points                          |
| time        | Returns the system time                                |
| schedule    | Lists configured schedule rules                        |
| countdown   | Lists configured countdown rules                       |
| antitheft   | Lists configured antitheft rules                       |
| reboot      | Reboot the device                                      |
| reset       | Reset the device to factory settings                   |
| energy      | Return realtime voltage/current/power                  |
| stats_month | Power consumption in the current year grouped by month |
| stats_day   | Power consumption in the current month grouped by day  |

Please consult [tplink-smarthome-commands.txt](tplink-smarthome-commands.txt) for a comprehensive list of commands.