import numpy as np
import parser_utils as gen
import copy 
from yaml import load



class SemanticNode():
    def __init__(self, value, semantics, parent):
        self.value = value          #string literal
        self.children = set()    #set of nodes
        self.semantics = copy.deepcopy(semantics)  #dictionary of string literals to meanings
        self.children_values = {}   #dictionary that maps values to children
        self.parent = parent
        
    def add_child(self, child_node):
        if child_node.value not in self.children_values:
            self.children.add(child_node)   
            self.children_values[child_node.value] = child_node
            
    def get_child(self, value):
        if value not in self.children_values:
            return None
        else:
            return self.children_values[value]
            
        
    '''Add semantics to current semantics'''
    def add_semantics(self, new_semantics):
        self.semantics.update(new_semantics)
        
    def __str__(self):
        node_string = "value: " + str(self.value) + ", semantics: " + str(self.semantics) 
        if self.parent is not None:
            node_string += ", parent: " + str(self.parent.value)
        node_string += ", children = {"
        for c in self.children:
            node_string += str(c.value) + ","
        node_string += "}"
        return node_string
        
    

class ParseTree():
    def __init__(self, production_rules):
        self.root = SemanticNode("root", {}, None)
        self.production_rules = production_rules
        
    def add_sentences(self, sentences, semantic):
        for s in sentences:
            words = gen.split_ignore(s)
            self.add_to_tree(self.root, words, semantic)

    def add_to_tree(self, cur_node, word_list, semantic):
        value = word_list[0]
        if value not in cur_node.children_values:
            child = SemanticNode(value, {}, cur_node)
            cur_node.add_child(child)
        else:
            child = cur_node.get_child(value)
        if len(word_list) > 1:
            self.add_to_tree(child, word_list[1:], semantic)
        else:
            #leaf node so add the semantics
            child.add_semantics(semantic)
        
    def print_tree_breadthfirst(self):
        #TODO should be a queue
        node_list = []
        node_list.append(self.root)
        while len(node_list) > 0:
            node = node_list[0]
            print(node)
            for c in node.children:
                node_list.append(c)
            node_list = node_list[1:]
   
    '''a helper function that takes parse dictionary and fills in the terminals
#{task="", location = "", whattosay=""}
'''
    def simplify_parse(self, parse):
        simple_parse = {}    
        print(parse)
        parse_comma_splitted = parse["task"].split(";")
        simple_parse["task"] = parse_comma_splitted[0]
        for i in range(1,len(parse_comma_splitted)):
            data = parse_comma_splitted[i].split("=")
            for key in parse:
                if key == data[1].strip():
                    simple_parse[data[0].strip()] = parse[key].strip()
            
        return simple_parse   
        
    def parse_utterance(self, utterance):
        #remove extra whitespace and punctuation
        utterance = " ".join(gen.split_ignore(utterance))
        utterance = utterance.lower()
        result = self.parse_r(self.root, utterance)
        if result is None:
            print("Error can't parse: ", utterance)
            return None
        else:
            return self.simplify_parse(result)
        
    def parse_r(self, node, utterance):
        #leafnode basecase
        if len(node.children) == 0 or utterance == "":
            return node.semantics
        #check node value with prefix of utterance
        for child_value in node.children_values:
            if self.is_non_terminal(child_value):
                matches, match_string = self.matches_literal(child_value, utterance)
                if matches:
                    child = node.children_values[child_value]
                    child.add_semantics(node.semantics)
                    #delete substring from utterance and recurse
                    utterance_sub = utterance[len(match_string):].strip()
                    result = self.parse_r(node.children_values[child_value], utterance_sub)
                    if result is not None:
                        return result
            else: #is a terminal
                #matches, match_string = self.matches_nonterminal(child_value, utterance)
                if child_value == "{question}":
                    #handle testing by me
                    matches, match_string = self.matches_literal("question", utterance)
                    if matches:
                        child = node.children_values[child_value]
                        child.add_semantics(node.semantics)
                        #delete substring from utterance and recurse
                        utterance_sub = utterance[len(match_string):].strip()
                        result = self.parse_r(node.children_values[child_value], utterance_sub)
                        if result is not None:
                            return result
                    #handle actual question generated by CmdGen
                    matches, match_string = self.matches_literal("{question}", utterance)
                    if matches:
                        child = node.children_values[child_value]
                        child.add_semantics(node.semantics)
                        #delete substring from utterance and recurse
                        utterance_sub = utterance[len(match_string):].strip()
                        result = self.parse_r(node.children_values[child_value], utterance_sub)
                        if result is not None:
                            return result
                    
                #check in production rules for all terminals resulting from nonterminal
                for terminal in self.production_rules[child_value]:
                    matches, match_string = self.matches_literal(terminal, utterance)
                    if matches:
                 
                        #add new semantics to child node 
                        new_semantics = {}
                        new_semantics[child_value]=match_string
                        child = node.children_values[child_value]
                        #add newly extracted semantics and parent semantics
                        child.add_semantics(new_semantics)
                        child.add_semantics(node.semantics)
                        
                        #delete substring from utterance and recurse
                        utterance_sub = utterance[len(match_string):].strip()
                        result = self.parse_r(child, utterance_sub)
                        if result is not None:
                            return result
                    
            
        #failure case, can't parse
        return None
        
    def matches_literal(self, value, utterance):
        if utterance[:len(value)].lower() == value.lower():
            return True, value
        else:
            return False, ""

    def is_non_terminal(self, string_value):
        if "{" in string_value or "$" in string_value:
            return False
        else:
            return True

    def matches_nonterminal(self, nonterminal, utterance):
        #handle special case of {question} essentially being a terminal
        if nonterminal == "{question}":
            #handle testing by me
            matches, match = self.matches_literal("question", utterance)
            if matches:
                return matches, match
            #handle actual question generated by CmdGen
            matches, match = self.matches_literal("{question}", utterance)
            if matches:
                return matches, match
            
        #check in production rules for all terminals resulting from nonterminal
        for terminal in self.production_rules[nonterminal]:
            matches, match = self.matches_literal(terminal, utterance)
            if matches:
                return matches, match
        #if we get here, we haven't found any matches
        return False, ""
            
        
def build_parser(yaml_config_file):
    with open(yaml_config_file) as f:
        configs = load(f)
    grammar_files = configs['grammar_files']
    grammar_location = configs['grammar_location']
    objects_xml_file = configs['objects_xml_file']
    locations_xml_file = configs['locations_xml_file']
    names_xml_file = configs['names_xml_file']
    semantics_file = configs['semantics_file']
    artificial_terminals = configs['artificial_terminals']
    #now start with a certain token and build out all the possibilities
    #get highlevel rules
    production_rules_highlevel = gen.parse_production_rules(grammar_files, grammar_location)
    production_rules = gen.parse_productions_and_xml(grammar_files, grammar_location, objects_xml_file, locations_xml_file, names_xml_file)
    
    
    tree = ParseTree(production_rules)
    #loop and generate sentences and semantics programatically and from semantics file, respectively
    
    
    prod_to_semantics_dict = gen.parse_semantics_file(semantics_file)
    
    #for each translation in semantic file
    for prod in prod_to_semantics_dict:
        if prod_to_semantics_dict[prod] != "":
            
            #fully expand the production down to non-terminals
            all_expansions = []
            gen.recursively_fill_necessary(prod, production_rules_highlevel, artificial_terminals, all_expansions)
            #print("all expansions")
            #for s in all_expansions:
            #    print(s)    
            #add these expansions along with appropriate semantics to semantic tree
            task_semantics = {}
            semantics = prod_to_semantics_dict[prod]  
            task_semantics["task"] = semantics
            #print("adding", semantics)  
            tree.add_sentences(all_expansions, task_semantics)
    
    return tree
        
        
if __name__=="__main__":
    from yaml import load
    import parse_tree as pt

    yaml_config_file = "./parser_config.yaml"    
    
    with open(yaml_config_file) as f:
        configs = load(f)
    grammar_files = configs['grammar_files']
    grammar_location = configs['grammar_location']
    objects_xml_file = configs['objects_xml_file']
    locations_xml_file = configs['locations_xml_file']
    names_xml_file = configs['names_xml_file']
    #semantics_file = "./semantics_debug.csv"
    semantics_file = configs['semantics_file']
    artificial_terminals = configs['artificial_terminals']
    
    #now start with a certain token and build out all the possibilities
    #get highlevel rules
    production_rules_highlevel = gen.parse_production_rules(grammar_files, grammar_location)
    production_rules = gen.parse_productions_and_xml(grammar_files, grammar_location, objects_xml_file, locations_xml_file, names_xml_file)
    
    
    tree = ParseTree(production_rules)
    #loop and generate sentences and semantics programatically and from semantics file, respectively
    
    
    prod_to_semantics_dict = gen.parse_semantics_file(semantics_file)
    
    #for each translation in semantic file
    for prod in prod_to_semantics_dict:
        if prod_to_semantics_dict[prod] != "":
            
            #fully expand the production down to non-terminals
            all_expansions = []
            gen.recursively_fill_necessary(prod, production_rules_highlevel, artificial_terminals, all_expansions)
            print("all expansions")
            for s in all_expansions:
                print(s)    
            #add these expansions along with appropriate semantics to semantic tree
            task_semantics = {}
            semantics = prod_to_semantics_dict[prod]  
            task_semantics["task"] = semantics
            print("adding", semantics)  
            tree.add_sentences(all_expansions, task_semantics)
    
    
#    #debug single sentence
#    utterance = "navigate to the bathroom, look for a person, and say your team's country"
#    print(utterance)
#    parsed_utterance = tree.parse_utterance(utterance)
#    print(parsed_utterance)
#    
   
    #test all utterances
    print("-----------")
    print("testing all full sentences we have semantics for")
    print("-----------")
    sentence_count = 0
    parsed_count = 0
    for prod in prod_to_semantics_dict:
        print("testing all expansions of: ", prod)
        all_productions = []
        gen.recursively_fill(prod, production_rules, all_productions)
        for utterance in all_productions:
            sentence_count += 1
            #print("parsing: ", utterance)
            parsed_utterance = tree.parse_utterance(utterance)
            if parsed_utterance is not None:
                #print(parsed_utterance) 
                parsed_count += 1
        print(parsed_count)
    print("parsing accuracy: " + str(parsed_count) + " out of " + str(sentence_count))
