/* ***************************************************************************
	Module to interface with MySQL
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


USE wwsdb;

DROP TABLE wwsdb;

CREATE table wwsdb
( ID			INTEGER 	Primary Key	AUTO_INCREMENT
 ,abs_pressure	FLOAT(4,1) 	COMMENT '[hpa]'
 ,delay			SMALLINT	UNSIGNED COMMENT '[min] Debug: Delay aus dem idz errechnet.'
 ,hum_in		SMALLINT(3) UNSIGNED COMMENT '[%]'
 ,hum_out 		SMALLINT(3) UNSIGNED COMMENT '[%]'
 ,idz			datetime	DEFAULT '0000-00-00 00:00:00'	not null	UNIQUE	COMMENT '[UTC] Zeit und Datum der Messung.'
 ,ptr			SMALLINT	UNSIGNED COMMENT '[byte] Position in wws Ringpuffer'
 ,rain			FLOAT		COMMENT '[mm]'
 ,status		SMALLINT	COMMENT '[] Debug: uneuesed'
 ,temp_in		FLOAT(4,1)	COMMENT '[°C]'
 ,temp_out		FLOAT(4,1)	COMMENT '[°C]'
 ,wind_ave		FLOAT(5,2)	COMMENT '[mph]'
 ,wind_dir		SMALLINT 	UNSIGNED COMMENT '[*30°] 0=N; 0bis12 je 30°; 134=NULL'
 ,wind_gust		FLOAT(5,1)	COMMENT '[mph]'
);
