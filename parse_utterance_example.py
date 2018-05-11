# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 23:32:36 2018

@author: daniel
"""

import sys
from yaml import load
import parse_tree as pt

yaml_config_file = "/home/dsbrown/Code/AustinVillaatHome/GPSRParser/parser_config.yaml"

##testing yaml
#data = load(file(yaml_config_file, 'r'))
#print(data)

parser = pt.build_parser(yaml_config_file)
#utterance = sys.argv[1]
#utterance = 'Bring me the banana'
#utterance = "Bring the banana from the bathroom to the center table"
utterance = "give me the pasta"
print("input: " + utterance)
parsed_utterance = parser.parse_utterance(utterance)
if parsed_utterance is None:
    print("can't parse")
else:
    print(parsed_utterance)
