# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 23:32:36 2018

@author: daniel
"""

import sys
from yaml import load
import parse_tree as pt
import confirm_question as cq

yaml_config_file = "/home/dsbrown/Code/AustinVillaatHome/GPSRParser/parser_config.yaml"

##testing yaml
#data = load(file(yaml_config_file, 'r'))
#print(data)

parser = pt.build_parser(yaml_config_file)
#utterance = sys.argv[1]
#utterance = 'Bring me the banana'
#utterance = "Bring the banana from the bathroom to the center table"
#utterance = "give me the pasta"
utterance = "look for a person in the bathroom and tell something about yourself"
#utterance = "Place the noodles on the cabinet"
#utterance = "look for the tea spoon in the bedroom"
#utterance = "Locate a person in the bathroom and answer a question"
#utterance = "Tell me the name of the person at the stove"
#utterance = "Tell me how many water there are on the cabinet"
#utterance = "Take the noodles from the washbasin and deliver it to me"

print("input: " + utterance)
parsed_utterance = parser.parse_utterance(utterance)
#print(parsed_utterance)

confirmer = cq.QuestionConfirmer(yaml_config_file)
confirm_utterance = confirmer.generateConfirmation(parsed_utterance)
print(confirm_utterance)
