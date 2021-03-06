# =================================================================
#
# Author: Thinesh Sornalingam <thinesh.sornalingam@canada.ca>,
#         Robert Westhaver <robert.westhaver.eccc@gccollaboration.ca>
#
# Copyright (c) 2020 Thinesh Sornalingam
# Copyright (c) 2020 Robert Westhaver
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import os
import logging
import xml.etree.ElementTree as et

LOGGER = logging.getLogger(__name__)


def parse_swob(swob_file):
    """
    Read swob at swob_path and return object
    :param swob_path: file path to SWOB XML
    :returns: dictionary of SWOB
    """

    namespaces = {'gml': 'http://www.opengis.net/gml',
                  'om': 'http://www.opengis.net/om/1.0',
                  'xlink': 'http://www.w3.org/1999/xlink',
                  'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                  'dset': 'http://dms.ec.gc.ca/schema/point-observation/2.0'}

    swob_values = {}
    elevation = ''
    latitude = ''
    longitude = ''

    # extract the swob xml source name
    swob_name = os.path.basename(swob_file)

    # make sure the xml is parse-able
    try:
        xml_tree = et.parse(swob_file)
    except (FileNotFoundError, et.ParseError):
        msg = 'Error: file {} cannot be parsed as xml'.format(swob_file)
        LOGGER.debug(msg)
        raise RuntimeError(msg)

    gen_path = './/om:Observation/om:metadata/dset:set/dset:general'
    general_info_tree = (xml_tree.findall(gen_path, namespaces))
    general_info_elements = list(general_info_tree[0].iter())
    properties = {}

    # extract swob dataset
    for element in general_info_elements:
        if 'name' in element.attrib.keys():
            if element.tag.split('}')[1] == 'dataset':
                properties[element.tag.split('}')[1]] = (
                    element.attrib['name'].replace('/', '-'))

    # add swob source name to properties
    properties["id"] = swob_name

    # extract ID related properties
    id_path = ('.//om:Observation/om:metadata/' +
               'dset:set/dset:identification-elements')
    identification_tree = xml_tree.findall(id_path, namespaces)
    identification_elements = list(identification_tree[0].iter())

    for element in identification_elements:
        element_name = ''
        if 'name' in element.attrib.keys():
            for key in element.attrib.keys():
                if key == 'name':
                    if element.attrib[key] == 'stn_elev':
                        elevation = float(element.attrib['value'])
                        break
                    elif element.attrib[key] == 'lat':
                        latitude = float(element.attrib['value'])
                        break
                    elif element.attrib[key] == 'long':
                        longitude = float(element.attrib['value'])
                        break
                    else:
                        element_name = element.attrib[key]
                else:
                    properties["{}-{}".format(element_name, key)] = (
                            element.attrib[key])

    # set up cords and time stamps
    swob_values['coordinates'] = [longitude, latitude, elevation]

    s_time = ('.//om:Observation/om:samplingTime/' +
              'gml:TimeInstant/gml:timePosition')
    time_sample = list(xml_tree.findall(s_time, namespaces)[0].iter())[0]
    properties['obs_date_tm'] = time_sample.text

    r_time = ('.//om:Observation/om:resultTime/' +
              'gml:TimeInstant/gml:timePosition')
    time_result = list(xml_tree.findall(r_time, namespaces)[0].iter())[0]
    properties['processed_date_tm'] = time_result.text

    # extract the result data from the swob
    res_path = './/om:Observation/om:result/dset:elements'
    result_tree = xml_tree.findall(res_path, namespaces)
    result_elements = list(result_tree[0].iter())

    last_element = ''
    for element in result_elements:
        nested = element.iter()
        for nest_elem in nested:
            value = ''
            uom = ''
            if 'name' in nest_elem.attrib.keys():
                name = nest_elem.attrib['name']
                if 'value' in nest_elem.attrib.keys():
                    value = nest_elem.attrib['value']
                    
                    # Checks to see if value string can be casted to float/int
                    try:
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        msg = (('Warning the value: "{}" could not be ' +
                               'converted to a number, this can be because ' +
                               'of an improperly formatted number value or ' +
                               'because of an intentional string value')
                               .format(value))
                        LOGGER.debug(msg)
                        pass

                if 'uom' in nest_elem.attrib.keys():
                    if nest_elem.attrib['uom'] != 'unitless':
                        uom = nest_elem.attrib['uom'].replace('\u00c2', '')

                # element can be 1 of 3 things:
                #   1. a data piece
                #   2. a qa summary
                #   3. a data flag
                if all([name != 'qa_summary', name != 'data_flag']):
                    properties[name] = value
                    if uom:
                        properties["{}-{}".format(name, 'uom')] = uom
                    last_element = name
                elif name == 'qa_summary':
                    properties["{}-{}".format(last_element, 'qa')] = value
                elif name == 'data_flag':
                    properties["{}-{}-{}".format(last_element, 'data_flag',
                                                 'uom')] = uom
                    properties["{}-{}-{}".format(last_element, 'data_flag',
                                                 'code_src')] = (
                        nest_elem.attrib['code-src'])
                    properties["{}-{}-{}".format(last_element, 'data_flag',
                                                 'value')] = (
                            value)

        swob_values['properties'] = properties

        return swob_values


def swob2geojson(swob_file):
    """
    Produce GeoJSON from dict
    :param swob_dict: swob in memory
    :returns: geojson
    """

    swob_dict = parse_swob(swob_file)
    json_output = {}

    try:
        if len(swob_dict) == 0:
            msg = ('Error: dictionary passed into swob2geojson is blank')
            LOGGER.debug(msg)
            raise RuntimeError(msg)
    except TypeError:
        msg = "Error: NoneType passed in as swob dict"
        LOGGER.debug(msg)
        raise RuntimeError(msg)

    # verify dictionary contains the data we need to avoid error
    if 'properties' in swob_dict.keys() and 'coordinates' in swob_dict.keys():
        json_output['type'] = 'Feature'
        json_output["geometry"] = (
            {"type": "Point", "coordinates": swob_dict['coordinates']})
        json_output["properties"] = swob_dict["properties"]
        return json_output
    else:
        msg = ('Error: dictionary passed into swob2geojson lacks' +
               ' required fields')
        LOGGER.debug(msg)
        raise RuntimeError(msg)
