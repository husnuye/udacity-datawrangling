# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 14:20:24 2017

@author: user
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "sample.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

street_mapping = {"151": "",
           "15th": "15th Street",
           "2": "",
           "Avenue,":"Avenue",
           "Avenue,Moreton":"Avenue",
           "203": "",
           "302": "",
           "3500": "",
           "3658": "",
           "4": "",
           "404": "",
           "502": "",
           "AVE": "Avenue",
           "Airport": "San Francisco International Airport",
           "Alameda": "Alameda Street",
           "Alto": "Alto Route",
           "Ave": "Avenue",
           "Ave. ": "Avenue",
           "Blvd": "Boulevard",
           "Blvd, ": "Boulevard",
           "Blvd.": "Boulevard",
           "California": "California Street",
           "Cres": "Crescent",
           "Ctr": "Center",
               "Dr": "Drive",
           "Hwy": "Highway",
           "Garden": "Gardens",
           "Ln.": "Lane",
           "North": "",
           "Rd": "Road",
           "road": "Road",
           "road,": "Road",
           "St": "Street",
           "St.": "Street",
           "broadway": "Broadway",
           "square": "Square",
           "st": "Street",
           "street":"Street",
           "Strand":"Street",
           "VIllage":"Village",
           "way":"Way",
            }
##In [12]:
# cleaning functions

# cleaning street names
def update_street(name, mapping):
    m = street_type_re.search(name)
    other_street_types = []
    if m:
        street_type= m.group( )
        print m
        if street_type in mapping.keys( ):
            name = re.sub(street_type,mapping[street_type],name)
        else:
            other_street_types.append(street_type)
    return name


# cleaning post codes
def update_code(post_code):   
    if(post_code[0] != '9' and post_code[0] != 'C'):
        post_code = 'Invalid Zip Code'
    elif(post_code == 'CA'):
        post_code = 'Invalid Zip Code'
    elif(len(post_code) > 5): #truncate zip codes that have secondary codes with a (-)
        if(post_code[:3] == 'CA ' or post_code[:3] == 'CA:'): # 'CA 94080' case
            post_code = post_code[3:]
        elif(post_code[:3] == 'CA9'):
            post_code = post_code[2:]
    return post_code
##In [ ]:
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    if element.tag == 'node':
        for node in NODE_FIELDS:
            try:
                node_attribs[node] = element.attrib[node]
            except:
                node_attribs[node] = '00000'
                pass
        #fill out node dictionary
        #fill out node_tags list of dictionaries
        for child in element:
            tag={'id': element.attrib['id'],'key':child.attrib['k'],'value':child.attrib['v'],'type':"regular"}
            if problem_chars.search(child.attrib["k"]):
                continue
            elif LOWER_COLON.search(child.attrib["k"]): # clean here
                tag_split = re.split(':',child.attrib["k"],1)
                tag['key']=tag_split[1]
                tag['type']=tag_split[0]
                # street clean
                if child.attrib["k"] == 'addr:street': 
                    tag["value"] = update_street(child.attrib["v"], street_mapping)
                else:
                    tag["value"] = child.attrib["v"]         
                # postal code clean
                if child.attrib["k"] == 'addr:postcode': 
                    tag["value"] = update_code(child.attrib["v"])
                else:
                    tag["value"] = child.attrib["v"]
                
            tags.append(tag)
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        #fill out way dictionary
        for wfield in way_attr_fields:
            way_attribs[wfield]=element.attrib[wfield]
        #fill out way_nodes dictionary
        counter = 0 
        for child in element:
            if(child.tag=='tag'):
                tag={'id': element.attrib['id'],'key':child.attrib['k'],'value':child.attrib['v'],'type':"regular"}
                if problem_chars.search(child.attrib["k"]):
                    continue
                elif LOWER_COLON.search(child.attrib["k"]):# clean here
                    tag_split = re.split(':',child.attrib["k"],1)
                    tag['key']=tag_split[1]
                    tag['type']=tag_split[0]
                         # street clean
                    if child.attrib["k"] == 'addr:street': 
                        tag["value"] = update_street(child.attrib["v"], street_mapping)
                    else:
                        tag["value"] = child.attrib["v"]
                    # postal code clean
                    if child.attrib["k"] == 'addr:postcode': 
                        tag["value"] = update_code(child.attrib["v"])
                    else:
                        tag["value"] = child.attrib["v"]
                tags.append(tag)
            elif(child.tag=='nd'):
                wnode={'id':element.attrib['id'],'node_id':0,'position':counter}
                counter+=1
                wnode['node_id']=child.attrib['ref']
                way_nodes.append(wnode)
                
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}






# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

process_map(OSM_PATH, validate=False)