# =================================================================
#
# Author: Thinesh Sornalingam <thinesh.sornalingam@canada.ca>,
#         Robert Westhaver <robert.westhaver.eccc@gccollaboration.ca>
#
# Copyright (c) 2020 Thinesh Sornalingam, Robert Westhaver
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

import unittest
import json
import swob2geojsonV2 as swob2gjson

def write_output(test_num, list_dict):
    with open(test_num + '_result.json', 'w') as fp:
        for feature in list_dict:
            fp.write(json.dumps(feature, indent=4, sort_keys=True))
            
def read_json(file_name):
    with open(file_name) as fp:
        return json.load(fp)


class Sob2GeoJsonTest(unittest.TestCase):
    """Test suite for converting swobs to geojson"""
    
    def test_CGCH_minute(self):
        test_file = 'test_files/2020-07-01-0007-CGCH-AUTO-minute-swob.xml'
        master_file = 'test_master_files/CGCH_minute_master.json'
        master_geojson = read_json(master_file)
        self.assertEqual(swob2gjson.swob2geojson(test_file),
                         master_geojson)
        
        
    def test_CAFC_minute(self):
        test_file = 'test_files/2020-07-01-0007-CAFC-AUTO-minute-swob.xml'
        master_file = 'test_master_files/CAFC_minute_master.json'
        master_geojson = read_json(master_file)
        self.assertEqual(swob2gjson.swob2geojson(test_file),
                         master_geojson)
    
    def test_CPOX_minute(self):
        test_file = 'test_files/2020-06-08-0000-CPOX-AUTO-minute-swob.xml'
        master_file = 'test_master_files/CPOX_minute_master.json'
        master_geojson = read_json(master_file)
        self.assertEqual(swob2gjson.swob2geojson(test_file),
                         master_geojson)
    
    def test_CAAW_minute(self):
        test_file = 'test_files/2020-06-08-0000-CAAW-AUTO-minute-swob.xml'
        master_file = 'test_master_files/CAAW_minute_master.json'
        master_geojson = read_json(master_file)
        self.assertEqual(swob2gjson.swob2geojson(test_file),
                         master_geojson)
        
    def test_CYBQ_swob(self):
        test_file = 'test_files/2020-05-31-0200-CYBQ-AUTO-swob.xml'
        master_file = 'test_master_files/CYBQ_swob_master.json'
        master_geojson = read_json(master_file)
        self.assertEqual(swob2gjson.swob2geojson(test_file),
                         master_geojson)
        
    
        
# main
if __name__ == '__main__':
    unittest.main()