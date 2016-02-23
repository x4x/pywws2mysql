# pywws2mysql

Write Data from Wireless WeatherStations with [jim-easterbrook/pywws](http://github.com/jim-easterbrook/pywws) to a Database.


## Installation

Install pywws with pip
```sudo pip install pywws ```

Install required aptitude packages:
```sudo apt-get install python2.7 libusb-dev python-usb ```

Now use a Database like MySQL and create user and a table for the weather data with Create.sql.
Configure all Database access credentials in the wws2mysql.ini file.
Write a Crontab entry to start pywws2mysql automatically.
```*/12 * * * * python2.7 /opt/pywws2mysql/pywws2mysql.py > /dev/null ```

If you use a other user then root create a udev rule. e.g.:
```
# /etc/udev/rules.d/38-weather-station.rules
SUBSYSTEM=="usb", ACTION=="add", ATTRS{idVendor}=="1941",
ATTRS{idProduct}=="8021", GROUP="ws-servilis"
```

~~Note: pywws2mysql uses [mysql.connector](https://dev.mysql.com/downloads/connector/python/) as MySQL API!~~

## Features

* a status report is logged with syslog.
* only new datasets from the wetterstation are synchronized.
* automatic reconnect attempt after 'USB time out' error.
* additional output of the weather data as text file possible.
* live status information of the synchronisation can be printed on screen


