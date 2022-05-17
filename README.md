# USWS-HA-Addon
Home Assistant AppDaemon script to create sensor entity from Uni Stuttgart Wetterstation Lauchäcker (https://lhg-902.iws.uni-stuttgart.de/). The weather sensor entity is updated every minute.

## Installation & Configuration

New: Steps 3-5 can be replaced with the [install script]. 

1. Install the [Home Assistant AppDaemon 4 add-on][appdaemon4] (if not already installed)
2. Add the required python packages to the add-on config
```
python_packages:
  - bs4
  - urllib3
```
3. Copy `vodafone_station_restarter.py` to `/config/appdaemon/apps/`
````bash
git clone git@github.com:G0RIAN/USWS-HA-Addon.git
cp ./USWS-HA-Addon/usws.py /config/appdaemon/apps/
````
4. Copy the app config to your `apps.yaml` and change the `request_time_sec`´or `sensor_name` if needed:
```bash
cat ./USWS-HA-Addon/apps.yaml >> /config/appdaemon/apps/apps.yaml
```
or add it manually
```yaml
usws:
    module: usws
    class: USWS
    request_time_sec: 42        # at which second of every minute the sensor is updated 
                                # (optional, defaults to randomly chosen value between 0 and 60)
    sensor_name: "sensor.usws"  # name of the sensor entity to be created, 'sensor.' can be omitted 
                                # (optional, defaults to "sensor.usws")
```

[appdaemon4]: https://github.com/hassio-addons/repository/tree/master/appdaemon
[install script]: (install.sh)