#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

"""
	Uses jim-easterbrook/pywws to interface with a USB Weterstation and writes data to MySQL Database.
    Copyright (C) 2013	x4x 	georg.la8585@gmx.at

    This program is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 2
	of the License, or (at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

	Name: wwsSQL.py
	Programteil: Uses jim-easterbrook/pywws to interface with a USB Weterstation and writes data to MySQL Database.
	Thema: See- und Wetterueberwachung
	Datum: 15.3.2013
	Version: 0.0.4 open Alpha fuer Python2.7
"""

__usage__ = """ Uses jim-easterbrook/pywws to interface with a USB Weterstation and writes data to MySQL Database. """

import syslog
import ConfigParser, os
import sys
import time
import datetime
from datetime import timedelta
from pywws import WeatherStation
from mysql_interface import mysql_interface as db

import pprint

def WeatherStation_init():
	""" create kumunication Object für WeatherStation."""
	try:
		ws = WeatherStation.weather_station()
	except:
		raise NameError("WS conection error")
	return (ws)
	
def WeatherStation_synctime(ws):
	""" Time synkronisiren mit WS. Achtung kann bis zu 10min dauern!""" 
	for data, last_ptr, logged in ws.live_data(True):
		last_date = data['idx'] # Timestemp of entry
		if logged:
			pprint.pprint( data) 
			break
	# set secunden to 0
	last_date.replace(second=0)
	return (last_date)
	
def WeatherStation_fixed_block(ws):
	""" Leist den Fixblock aus"""
	return ws.get_fixed_block()
	
def WeatherStation_ptr_pos(fixb):
	""" Liest Fixblock aus und giebt die Anzahl gepeischerter Datensetze zurück."""
	return (fixb['current_pos'] )

def verify_wws2db_timing(wws_time, last_db_time, tolerance):
	""" Vergleiche ob Weterstaions Eintrag aktueller als Datenbank eintrag.
	tolerance in minuten"""
	tolerance_td= timedelta (minutes = tolerance)
	if(wws_time > last_db_time + tolerance_td):
		return True
	else:
		return False

def get_last_db_entry(sqldb, table):
	""" Reads last entery from Database. If no entry exixts function returns None.""" 
	return (sqldb.dict_read( table, key='ID', operator='=', value='MAX(id)', returnmode='fetchone'))
	
def write_to_file(filepath, fixb, all_data):
	""" Write Data to text file."""
	filepath= "out.txt"
	file = open( filepath, 'w')
	file.write( "# WS Data: " + fixb['date_time'] + "\n\n" )
	pprint.pprint(all_data, file)
	file.write("\n")
	file.close()
	
def main():
	# read wws2mysql.ini config
	config = ConfigParser.ConfigParser()
	config.readfp(open('wws2mysql.ini'))

	# init slogging
	syslog.openlog(ident=config.get('syslog', 'ident'),logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL7)
	
	# db connection information
	dbcon= {
		'user': config.get('mysql_db', 'user'),
		'password': config.get('mysql_db', 'password'),
		'host': config.get('mysql_db', 'host'),
		'database': config.get('mysql_db', 'database'),
		'table': config.get('mysql_db', 'table')
	}

	print (dbcon)
	
	#tries to reconnection
	i=6
	conection=True
	#reconnect loop
	while(conection and (i> 0)):
	  conection=False
	  i-=1
	  # init interface to Wetter station
	  print( "start wws connection")
	  try:
	    ws = WeatherStation_init()
	  except:
	    conection=True
	    print( "wws connection error")
	    continue
	  syslog.syslog(syslog.LOG_DEBUG, "connected to weather station" )
	  
	  # init time synchronization
	  print( "synchronization of wws timing")
	  try:
	    last_date = WeatherStation_synctime(ws)
	  except:
	    conection=True
	    print( "timing error")
	    continue
	  syslog.syslog(syslog.LOG_DEBUG, "weather station is synchronized" )
	  
	  # init database connection
	  print("init database")
	  try:
	    sqldb = db.mysql_interface(dbcon['user'], dbcon['password'], dbcon['host'], dbcon['database'])
	  except:
	    conection=True
	    print("db conection error!")
	    continue
	  syslog.syslog(syslog.LOG_DEBUG, "database connection initialized" )
	# if connection field multiple times raise error
	if(conection):
	  syslog.syslog(syslog.LOG_ERR, "Connection establishment field multiple times!" )
	  raise NameError("Waring! connection field multiple times!")
	  
	
	# read Fixblock
	fixb= WeatherStation_fixed_block(ws)
	
	# fined ptr position
	max_data = WeatherStation_ptr_pos(fixb)
	
	# read data from ring buffer
	# currant position in ring buffer
	r_pos_a= r_pos = ws.current_pos()
	
	# read last db entry
	last_entry= sqldb.read_last_entry( dbcon['table'], last_by='ID' )
	# Value 5 in list is the time of the measurement.
	# Value
	delay= 5
	
	# if db is empty use a dummy entry.
	if(last_entry== None):
		syslog.syslog(syslog.LOG_INFO, "weather station database is probably empty" )
		last_entry= [0,1,2,3,4,datetime.datetime(1970,1,1,0,0,0),6,7,8,9,10,360,360]
	
	print (last_entry)
	
	# all data of ring buffer
	all_data= {}
	max_data= 0
	
	#debug
	#r_ptss= []
	
	# if data from wws is newer then in db start synchronization.
	if (verify_wws2db_timing( last_date, last_entry[5], delay-2)):
		block = ws.get_data(r_pos)
		last_date = last_date - datetime.timedelta(minutes = block['delay'], seconds= 0)
		last_date.replace(second=0)
		block['idz'] = last_date 
		
		# determinant current end of ring buffer
		if(last_entry == [0,1,2,3,4,datetime.datetime(1970,1,1,0,0,0),6,7,8,9,10,360,360]):
			ptr_stop = 256
		else:
			ptr_stop = ws.inc_ptr(r_pos)
		
		# read ring buffer
		while (r_pos_a != ptr_stop) and (last_date > last_entry[5]):
		#while (r_pos_a != ptr_stop) and (verify_wws2db_timing( last_date, last_entry[5], delay-2)):
			r_pos_a = ws.dec_ptr(r_pos_a)
			
			# debug
			#r_ptss.append(r_pos_a)
			
			#tray to reconnect
			i=4
			while(i> 0):
			  try:
				  block = ws.get_data(r_pos_a, unbuffered=False )
			  except:  
				  i-=1
				  print("\n USB Timed out!\n")
				  # reconnect to wws
				  del ws
				  try:
					  ws = WeatherStation.weather_station()
				  except:
					  print( "wws connection error" )
					  syslog.syslog(syslog.LOG_ERR, "Connection field multiple times well synchronizing!" )
					  raise NameError("Waring!Connection field multiple times well synchronizing!")
				  print("\n reconnected!\n\n")
				  continue
			  break

			# add timestamps
			# ATTENTION!! Time allwaise in utc time 
			# http://de.wikipedia.org/wiki/Koordinierte_Weltzeit
			last_date = last_date - datetime.timedelta(minutes= block['delay'],seconds= 0)
			last_date.replace(second=0)
			block['idz'] = last_date
			# add pointer to list
			block['ptr'] = r_pos_a  

			print block
			all_data[max_data]= block
			max_data += 1


		# write data to db	
		# daten in umgekerter reienfolge in db schreiben.  damit sie cronologisch richtig sind mit der id.
		i = len(all_data) -2 # maximale anzahl zu syncronisirenden daten
		# -1 wegen 0 zehlbeginn; -1 wegen bereitz in db vorhandenen datensatz
		while (i >= 0):
			print i
			# insert in db
			print (all_data[i])
			sqldb.insert_in_db( dbcon['table'], all_data[i])
			# commuting cycle. every 10 entry auto commit.
			if( i%10 == 0):
			  sqldb.commit()
			i-=1
		# final commit for uncommitted enters
		sqldb.commit()
			  
		syslog.syslog(syslog.LOG_INFO, "weather station synchronization was successful" )	
	else:
		print ("db already actual.")
		syslog.syslog(syslog.LOG_INFO, "weather station db was already actual" )
	
	
	# test output to file
	if( config.getboolean('file_output', 'output')):
	      print "writing to file"
	      write_to_file('out.txt', fixb, all_data)
	
	print "all complete"
	del ws
	del sqldb
	
	return 0

if __name__ == "__main__":
    sys.exit(main())
