#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 21:16:54 2020

Reads a given .LIFT file
Dumps to JSON.

First system arg is name of LIFT file
Second system arg is name of file to output to,
or empty to return a JSON string instead.

@author: markjosims
"""

import sys
import json
import xml.etree.cElementTree as ET
from pylift.ReadLiftTags import read_entry

def main():
    if len(sys.argv) == 1:
        raise TypeError("Please specify LIFT filepath in system arguments.")
    
    lift_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        out_file = sys.argv[2]
        return lift_to_json(lift_file, out_file)
    else:
        return lift_to_json(lift_file)

# reads lift file from given filepath and saves to a .json file
# if out_file is None (or Falsey), returns JSON string instead
def lift_to_json(lift_file, out_file=None):
    lift = ET.parse(lift_file).getroot()
    entries = {}
    
    # [1:] b/c we're skipping the header
    for element in lift[1:]:
        id = element.get('id')
        entries[id] = read_entry(element)
    if not out_file:
        return(json.dumps(entries, indent=4))
    else:
        with open(out_file, 'w') as f:
            json.dump(entries, f, indent=2)




if __name__ == '__main__':
    main()