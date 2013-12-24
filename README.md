# pywws2mysql

Extension for jim-easterbrook/pywws to use MySQL as Database.


## Installation

To install it copy the files from the pywws2mysql folder to the root folder of pywws.
Then create a MySQL user and a table for the weather data with Create.sql.
Configure all MySQL access credentials in the wws2mysql.ini file.
Write a Crontab entry to start pywws2mysql automatically.

Note: pywws2mysql uses [mysql.connector](https://dev.mysql.com/downloads/connector/python/) as MySQL API!

## Features

* a status report is logged with syslog.
* only new datasets from the wetterstation are synchronized.
* automatic reconnect attempt after 'USB time out' error.
* additional output of the weather data as text file possible.
* live status information of the synchronisation can be printed on screen


