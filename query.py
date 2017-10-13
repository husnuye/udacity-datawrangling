# -*- coding: utf-8 -*-
"""
Created on Sat Jul 29 10:49:01 2017

@author: husnu
"""
#first 5 rows nodes


import sqlite3

con = sqlite3.connect("husnuye.db")
con.text_factory = str
curs = con.cursor()


curs.execute('select * from nodes limit 5')
print curs.fetchall()

#first 5 rows nodes_tags
curs.execute('select * from nodes_tags limit 5')
print curs.fetchall()

#first 5 rows ways

curs.execute('select * from ways limit 5')
print curs.fetchall()

#first 5 rows ways_tags
curs.execute('select * from ways_tags limit 5')
print curs.fetchall()

#first 5 rows ways_nodes

curs.execute('select * from ways_nodes limit 5')
print curs.fetchall()


curs.execute('SELECT COUNT(*) FROM nodes')
print curs.fetchall()
##13549

curs.execute('SELECT COUNT(*) FROM ways')
print curs.fetchall()
##2704

curs.execute('SELECT COUNT(DISTINCT(uid)) FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways)')
print curs.fetchall()
##296

curs.execute('SELECT user, COUNT(*) as num FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) GROUP BY user ORDER BY num DESC Limit 10')
print curs.fetchall()

##[('daviesp12', 10546), ('khbritish', 920), ('jrdx', 510), ('UniEagle', 337), ('Dyserth', 279), ('duxxa', 204), ('F1rst_Timer', 197), ('xj25vm', 190), ('thewilk', 188), ('John Embrey', 183)]


curs.execute('SELECT value, COUNT(*) as num FROM nodes_tags WHERE key = "amenity" GROUP BY VALUE ORDER BY num DESC LIMIT 10')
print curs.fetchall()

##[('post_box', 7), ('restaurant', 6), ('pub', 5), ('fast_food', 3), ('place_of_worship', 2), ('atm', 1), ('bank', 1), ('bench', 1), ('bicycle_parking', 1), ('cafe', 1)]


curs.execute('SELECT nodes_tags.value, COUNT(*) as num \
            FROM nodes_tags \
                JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="fast_food") i \
                ON nodes_tags.id=i.id \
            WHERE nodes_tags.key="name" \
            GROUP BY nodes_tags.value \
            ORDER BY num DESC Limit 10')
print curs.fetchall()

##[('Banquet House Chinese Take Away', 1), ('Lobster Pot', 1), ("Luke's Chippy", 1)]

curs.execute('SELECT nodes_tags.value, COUNT(*) as num \
            FROM nodes_tags \
                JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="cafe") i \
                ON nodes_tags.id=i.id \
            WHERE nodes_tags.key="name" \
            GROUP BY nodes_tags.value \
            ORDER BY num DESC Limit 10')
print curs.fetchall()

##[('Espresso', 1)]

   
curs.execute('SELECT nodes_tags.value, COUNT(*) as num \
             FROM nodes_tags \
                JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="place_of_worship") i \
                ON nodes_tags.id=i.id \
            WHERE nodes_tags.key="religion" \
            GROUP BY nodes_tags.value \
            ORDER BY num DESC LIMIT 1')
print curs.fetchall()

##[('christian', 1)]
