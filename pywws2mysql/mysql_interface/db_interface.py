#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

"""
	Module to interface with DataBase
    Copyright (C) 2014 	x4x 	georg.la8585@gmx.at

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

	Name: mysql_interface.py
	Programteil: Module to interface with MySQL
	Thema: See- und Wetterueberwachung
	Datum: 22.3.2013
	Version: 0.0.3 for Python2.7
"""

import importlib
import datetime
import time
import sys

def del_dict_None_values( dict_a):
	""" Removes all enterris off dict with None Values."""
	del_list = []
	for k, v in dict_a.iteritems():
		if v is None:
			del_list.append(k)
	for k in del_list:
		del dict_a[k]
	return dict_a
		
def datetime_to_db_str( time_date_a):
	""" Convert time and date from datime Object to MySQL time string."""
	return time_date_a.strftime("%Y-%m-%d %H:%M:%S")

def dict_datetime_to_db_str( dict_a):
	""" Sucht datetime.datetime Objekte in dict und wandelt sie in SQL kompatiblen String."""
	# einzelens umschreiben von dicht_a in dicht_b damit dicht_b neue id hat und alte werte nicht manipulirt werden
	dict_b={}
	for k, v in dict_a.iteritems():
		if isinstance( v, datetime.datetime):
			dict_b[k] = datetime_to_db_str(dict_a[k])
		else:
			dict_b[k]= v
	return dict_b

class mysql_interface(object):

		
	def get_db_table_structure(self, table):
		""" Get the structur of the table as a dict with options."""
		sql_struct= "show columns from %s ;"
		self.cursor.execute( sql_struct % table)
		struct_string = self.cursor.fetchall()
        
		return(struct_string)
		
	def table_existenz(self, table):
		""" """
		sql_existens="EXPLAIN %s ;" % table	
		out= True
		try:
			# Execute the SQL command
			self.cursor.execute(sql_existens)
		except:
			#raise NameError("Table Existenz Error!!")
			out= False
		return (out)
	
	def read_last_entry(self, table, last_by='ID' ):
		""" Read the last """
		sql_read_last="SELECT * FROM %s ORDER BY %s DESC LIMIT 1;" % (table, last_by)
		
		try:
			# Execute the SQL command
			self.cursor.execute(sql_read_last)
			
		except:
			raise NameError("read_last Error!!")

                        # Workaround for PostgresSQL
                        #return None
		return ( self.cursor.fetchone())
		#return ( self.cursor.fetchall())
		
	def insert(self, table, insert_dict):
                """ Insert data in to a table from an dict. 
		All Values in the dicht should be Strings and the Keys, Value order is importend."""
                sql_insert = "INSERT INTO %s( %s ) VALUES ( %s );"
                
                # test if keys in table
		try:
                        self.cursor.execute( sql_insert % ( table, ', '.join(insert_dict.keys()), str(insert_dict.values())[1:-1] ) )

		except:
                        raise NameError("Insert Error! Dataset probably already existing!")
			
	def insert_in_db(self, table, insert_dict):
		""" Insert data in to a table from an dict.
		Slower and Recomendet. Bereitet dict zum screiben in die db auf."""
		
		print(id(insert_dict))
		new_dict= del_dict_None_values( insert_dict)
		print(id(new_dict))
		new_dict= dict_datetime_to_db_str( new_dict)
		self.insert(table, new_dict)
	
	def read(self, table, key='', operator='', value='', returnmode='fetchall' ):
		""" Read from table with SELECT comand and returns fatch.
		'key' is the table colum name.
		'operator' is the comperison operator (eg.: '=', '<', '>', ...).
		'value' is the Value to witch the operator compers.
		'returnmode'...
		
		 fetchone: This method fetches the next row of a query result set.
		 A result set is an object that is returned when a cursor object is used to query a table.

		 fetchall: This method fetches all the rows in a result set.
		 If some rows have already been extracted from the result set,
		 the fetchall() method retrieves the remaining rows from the result set.

		 rowcount: This is a read-only attribute and returns the number
		 of rows that were affected by an execute() method."""
		if(key== ''):
			sql_select = "SELECT * FROM %s ;" % ( table)
		else:
			sql_select = "SELECT * FROM %s WHERE %s %s '%s'" % ( table, key, operator, value )
			
		try:
			# Execute the SQL command
			self.cursor.execute(sql_select)
		except:
			raise NameError("Read Error!")
		
			
		# Fetch all the rows in a list of lists.
		if returnmode == 'fetchall':
			return( self.cursor.fetchall())
		elif returnmode == 'fetchone':
			return ( self.cursor.fetchone())
		elif returnmode == 'rowcount':
			return ( self.cursor.rowcount)
		else:
			# error
			raise NameError("No falid option for 'returnmode' parameter!!")
			
	def dict_read(self, table, key='', operator='', value='', returnmode='fetchall'):
		""" Verwendet read funtion, packt aber eingelesenes in dict mit struktur.
		Zurückgegebes dict enthelt Zelennummer zu dict mit Spaltenbezeichnung zu Daten."""
		# strucktur einlesen
		struckt_tuple_list= self.get_db_table_structure(table)
		# lesse Spalten namen aus struckt_tuple_list aus.
		struckt_list= map(lambda x: x[0], struckt_tuple_list)
		del struckt_tuple_list
		# liste einlesen
		read_list= self.read( table, key, operator, value, returnmode )
		
		dict_a= {}
		
		rows_len= len(read_list)
		#testen ob struktur und rows gleich lang sind
		if(len(struckt_list) == len(read_list[0])):
			for current_row_numb in xrange(0, rows_len):
				dict_a[current_row_numb]= dict(zip( struckt_list, read_list[current_row_numb]))
		else:
			raise NameError("Structure and Values does not match!")
		return (dict_a)
	
	def commit(self):
		""" Commit to the Databse. Insert functions commit automaticly. """
		try:
			self.__mysqldb_a.commit()
		except:
			raise NameError("Commit Error!!")
	
	def get_line(self, table, line_num):
		""" get line from database. (uses self.read())."""
		return self.read( table, key="ID", operator=line_num, returnmode='fetchone' )

	def del_line(self, table, key='', operator='', value='' ):
		""" Delite lines from the table.
		'key' is the table colum name.
		'operator' is the comperison operator (eg.: '=', '<', '>', ...).
		'value' is the Value to witch the operator compers."""
		
		if(key == ''):
			sql_del = "DELETE FROM %s ;" % ( table)
		else:
			sql_del = "DELETE FROM %s WHERE %s %s '%s' ;" % ( table, key, operator, value )
			
		try:
			self.cursor.execute(sql_del)
		except:
			raise NameError("del error!!")
			pass 
	
	def __del__(self):
		""" Close conection to Database. """
		self.__mysqldb_a.close()
	
        def __init__(self, engine, user, password, host, database, raise_on_warnings = True):
                """ Init the database comunication with options. Creates a cursor with olso can used from autseid the object. """

                # set db engine
                db = importlib.import_module( engine )

                self.__mysqldb_a = db.connect(user= user, password=password, host=host, database= database)

                """
                try:
                        self.__mysqldb_a = db.connect(user= user, password=password, host=host, database= database, raise_on_warnings=raise_on_warnings)
                except db.Error as err:
                        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                                raise NameError("Something is wrong your username or password")
                        elif err.errno == errorcode.ER_BAD_DB_ERROR:
                                raise NameError("Database does not exists")
                        else:
                                raise NameError(err)"""
                self.cursor = self.__mysqldb_a.cursor()
		

def main():
	""" Test for mysql_interface.py. """
	"""mq = mysql_interface('Python', '1234', '127.0.0.1', 'Python')
	
	print(mq)
	
	print("existenz:")
	print ( mq.table_existenz('wwsdb'))
	print ( mq.table_existenz('aaba'))
	
	print (mq.read_last_entry( 'wwsdb', last_by='ID' ))
		
	print ("object cloesd!")
	del mq
	"""

        """
          	  
__init__()
read_last_entry
insert_in_db
commit()
dict_read
"""
        # dbcon['user'], dbcon['password'], dbcon['host'], dbcon['database']
        sqldb= mysql_interface(engine= 'psycopg2' ,user='pywws',password= 'Stratos',host= '127.0.0.1',database= 'wwsdb')
        
        print "reading last entry"
        print sqldb.read_last_entry( 'wws', last_by='ID' )

        print ""
        sqldb.insert_in_db( 'wws', all_data[i])

        sqldb.commit()

        

	return 0

if __name__ == "__main__":
    sys.exit(main())
		
