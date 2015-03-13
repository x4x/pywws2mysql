/* ***************************************************************************
	Module to interface with PostgreSQL
    Copyright (C) 2013 	x4x 	georg.la8585@gmx.at

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

***************************************************************************** */


--USE wwsdb;
\c wwsdb

DROP TABLE wwsdb;
DROP TABLE wwsdb_id_seq;

CREATE table wwsdb
( ID                    SERIAL         Primary Key
 ,abs_pressure		numeric      
 ,delay                 SMALLINT
 ,hum_in                SMALLINT 
 ,hum_out               SMALLINT 
 ,idz                   TIMESTAMP          not null        UNIQUE  
 ,ptr                   INTEGER      
 ,rain                  numeric           
 ,status                SMALLINT        
 ,temp_in               numeric     
 ,temp_out              numeric      
 ,wind_ave              numeric      
 ,wind_dir              SMALLINT   
 ,wind_gust             numeric      
);

GRANT ALL ON wwsdb TO pywws;
GRANT ALL ON wwsdb_id_seq TO pywws;
