# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 10:21:10 2018

@author: dsbrown
""" 

import sys
from yaml import load
import parse_tree as pt




    

'''generate a precanned response to a question'''
class QuestionConfirmer():
    def __init__(self, yaml_config_file):
        with open(yaml_config_file) as f:
            configs = load(f)
        self.responses_dict = self.process_confirmations(configs['confirmations_file'])
        
        
    def generateConfirmation(self, parse):
        if parse is None:
            return "I'm sorry, I couldn't parse that. Could you repeat what you said?"
        #parse = simplify_parse(parse)
        print("confirming: ", parse)
        semantic_task = parse["task"]
        raw_response = self.responses_dict[semantic_task]
        print("canned template", raw_response)
        #find and replace strings in raw_response using parse values
        for key in parse:
            if key != "task":
                #print(key)
                raw_response = raw_response.replace("$" + key, parse[key].strip())
        #find and replace common phrases to make it sound better
        raw_response = raw_response.replace("your", "my")
        raw_response = raw_response.replace("yourself", "myself")
        print(raw_response)
        return "You want me to {}, is that correct?".format(raw_response)
        
        
    def process_confirmations(self, confirmation_file_path):
        conf_dict = {}
        with open(confirmation_file_path) as f:
            for line in f:
                semantics_response = line.split(":")
                semantics = semantics_response[0].strip()
                response = semantics_response[1].strip()
                conf_dict[semantics] = response
        return conf_dict
        
        
if __name__=="__main__":
    #testing
    yaml_config_file = "/home/dsbrown/Code/AustinVillaatHome/GPSRParser/parser_config.yaml"
    confirmations_file = "./confirmations.csv"
    parser = pt.build_parser(yaml_config_file)
    #utterance = sys.argv[1]
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
    
    confirmer = QuestionConfirmer(confirmations_file)
    confirm_utterance = confirmer.generateConfirmation(parsed_utterance)
    print(confirm_utterance)
    
    

        