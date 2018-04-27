#python script to try and parse the grammar
#doesn't work for nested (()) but I think we can get rid of these easily by hand in the grammars
import xml.etree.ElementTree as ET

PRODUCTION = 0
SEMANTICS = 1

'''splits the production on consecutive whitespace and punctuation but ignores spaces between {} so
split_production("the {room 1}, the {beacon 1}") = ["the", "{room 1}", "the", "{beacon 1}"] '''
def split_ignore(string):
    ignores = [".",",","?"]
    state = "normal"
    split_result = []
    substring = ""
    for i, ch in enumerate(string):
        if ch is "{":
            state = "special"
            substring += ch
        elif ch is "}":
            state = "normal"
            substring += ch
        elif ch.isspace() or ch in ignores:
            if state == "normal":
                split_result.append(substring)
                substring = ""
                state = "ignore"
            elif state == "special":
                substring += ch
            elif state == "ignore":
                continue
        else:
            if state == "ignore":
                state = "normal"
            substring += ch
    split_result.append(substring)
    return split_result

def parse_rhs(prefix, production_string, state, rhs_list):
    #basecase
    if production_string == '':
        rhs_list.append(prefix + production_string)
        return rhs_list
    for i, ch in enumerate(production_string):
        #print(i,ch)
        if ch == "|":
            if state == "ALPH":
                rhs_list.append(prefix + production_string[0:i])
                return parse_rhs('', production_string[i+1:],state, rhs_list)
            elif state == "PAREN_START":
                state_n = "PAREN_END"
                prefix_n = prefix + production_string[0:i]
                parse_rhs(prefix_n, production_string[i+1:], state_n, rhs_list)
                #start another branch for production B in (A | B | ...)
                return parse_rhs(prefix, production_string[i+1:], state, rhs_list)
            elif state == "PAREN_END":
                continue #searching for )
        elif ch == "(":
            state_n = "PAREN_START"
            prefix_n = prefix + production_string[0:i]
            return parse_rhs(prefix_n, production_string[i+1:], state_n, rhs_list)
        elif ch == ")":
            if state == "PAREN_END":
                state = "ALPH"
                return parse_rhs(prefix, production_string[i+1:], state, rhs_list)
            elif state == "PAREN_START":
                state = "ALPH"
                prefix_n = prefix + production_string[0:i]
                return parse_rhs(prefix_n, production_string[i+1:],state, rhs_list)
    rhs_list.append(prefix + production_string)
    return rhs_list

                
            

def parseGrammar(line):
    eq_split = line.split("=")
    assert(len(eq_split) == 2)
    lhs = eq_split[0].strip()
    rhs_list_raw = parse_rhs("", eq_split[1].strip(), "ALPH", [])
    rhs_list = []
    for rhs in rhs_list_raw:
        rhs_list.append(' '.join(rhs.split()))
    
    return lhs, rhs_list
    
def recursively_fill(sentence, production_rules, all_sentences):
    found_match = False
    for rule in production_rules:
        if rule in sentence:
            #check if it's a full match or if a partial match, i.e. $take matches $takefrom but not correct match
            #see if next char is a space or if the rule ends the sentence, otherwise no match
            start_indx = sentence.find(rule)
            if len(sentence) == start_indx + len(rule) or not sentence[start_indx + len(rule)].isalpha():
                #replace with all of rule's productions
                
                for production in production_rules[rule]:
                    sentence_filled = sentence[:start_indx] + production + sentence[start_indx + len(rule):]
                    recursively_fill(sentence_filled, production_rules, all_sentences)
                found_match = True
                break
            
    #base case
    if not found_match:
        #print(' '.join(sentence.split()))
        all_sentences.append(' '.join(sentence.split()))
        return
        
def recursively_fill_necessary(sentence, production_rules, not_necessary, all_sentences):
    found_match = False
    for rule in production_rules:
        if rule not in not_necessary:
            if rule in sentence:
                #check if it's a full match or if a partial match, i.e. $take matches $takefrom but not correct match
                #see if next char is a space or if the rule ends the sentence, otherwise no match
                start_indx = sentence.find(rule)
                if len(sentence) == start_indx + len(rule) or not sentence[start_indx + len(rule)].isalpha():
                    #replace with all of rule's productions
                    
                    for production in production_rules[rule]:
                        sentence_filled = sentence[:start_indx] + production + sentence[start_indx + len(rule):]
                        recursively_fill_necessary(sentence_filled, production_rules, not_necessary, all_sentences)
                    found_match = True
                    break
            
    #base case
    if not found_match:
        all_sentences.append(' '.join(sentence.split()))
        return
        
    
def generate_all_sentences(start_symbol, production_rules):
    all_possible = []
    for production in production_rules[start_symbol]:
        #print(production)
        all_production = []
        recursively_fill(production, production_rules, all_production)
        all_possible.extend(all_production)
    return all_possible
    
    
def generate_all_highlevel_sentences(start_symbol, production_rules, not_necessary):
    all_possible = []
    #check if start symbol needs to be expanded
    if start_symbol in not_necessary:
        return all_possible
    for production in production_rules[start_symbol]:
        #print(production)
        all_production = []
        recursively_fill_necessary(production, production_rules, not_necessary, all_production)
        all_possible.extend(all_production)
    return all_possible


    
'''I want this to take any right hand side and build out all of the possibilities
for example if the right hand side:
$vbbring (me | to $whowhere) the {kobject} from the {placement}
is given as input, it should figure out all possibilities from parsing and expanding this
'''
def generate_all_expansions(right_hand_side, production_rules):
    all_expansions = []
    top_level_parses = parse_rhs("", right_hand_side, "ALPH", [])
    for parse in top_level_parses:
        expands = []
        recursively_fill(parse, production_rules, expands)
        all_expansions.extend(expands)
    return all_expansions
    
'''Find all non terminals that don't need to be expanded since they dont result in any {}'''    
def find_not_necessary_expansions(production_rules, artificial_terminals):
    not_necessary = []
    for lhs in production_rules:
        expansions = generate_all_highlevel_sentences(lhs, production_rules, artificial_terminals)
        #check if {} is found or something in nec_exceptions
        is_necessary = False
        for expanded in expansions:
            if "{" in expanded:
                is_necessary = True
            for aterminal in artificial_terminals:
                if aterminal in expanded:
                    is_necessary = True
        if not is_necessary:
            not_necessary.append(lhs)
    return not_necessary
            
        
    

#parse into a dictionary with extensions for everything '$something = ' as a key and values for all productions
def parse_production_rules(grammar_file_list, grammar_location):
    production_rules = {}
    for grammar_file in grammar_file_list:
        with open(grammar_location + grammar_file) as f:
            for line in f:
                line = line.strip()
                if len(line) > 0 and line[0] == '$':
                    #print(line)
                    #parse into possible productions
                    lhs, rhs_productions = parseGrammar(line)
                    #print(lhs)
                    #print(rhs_productions)
                    #add to dictionary, if already there then append to list of rules
                    #using set to avoid duplicates
                    if lhs not in production_rules:
                        production_rules[lhs] = rhs_productions
                    else:
                        production_rules[lhs].extend(rhs_productions)
    return production_rules
    
def parse_objects(objects_xml_file):
    all_objects = []
    tree = ET.parse(objects_xml_file)
    root = tree.getroot()
    for cat in root.findall("./category"):
        for obj in cat:
            all_objects.append(obj.attrib['name'])
    return all_objects

def parse_categories(objects_xml_file):
    all_categories = []
    tree = ET.parse(objects_xml_file)
    root = tree.getroot()
    for cat in root.findall("./category"):
        all_categories.append(cat.attrib['name'])
    return all_categories
    
def parse_rooms(locations_xml_file):
    all_rooms = []
    tree = ET.parse(locations_xml_file)
    root = tree.getroot()
    for room in root.findall("./room"):
        all_rooms.append(room.attrib['name'])
    return all_rooms

def parse_locations(locations_xml_file):    
    all_locations = []
    tree = ET.parse(locations_xml_file)
    root = tree.getroot()
    for room in root.findall("./room"):
        for location in room:
            all_locations.append(location.attrib['name'])
    return all_locations

def parse_placements(locations_xml_file):
    all_placements = []
    tree = ET.parse(locations_xml_file)
    root = tree.getroot()
    for room in root.findall("./room"):
        for location in room:
            if 'isPlacement' in location.attrib:
                if location.attrib['isPlacement'] == "true":
                    all_placements.append(location.attrib['name'])
    return all_placements
    
def parse_beacons(locations_xml_file):
    all_beacons = []
    tree = ET.parse(locations_xml_file)
    root = tree.getroot()
    for room in root.findall("./room"):
        for location in room:
            if 'isBeacon' in location.attrib:
                if location.attrib['isBeacon'] == "true":
                    all_beacons.append(location.attrib['name'])
    return all_beacons
    
def parse_names(names_xml_file):
    all_names = []
    tree = ET.parse(names_xml_file)
    root = tree.getroot()
    for name in root.findall("./name"):
        all_names.append(name.text)
    return all_names
                

def generate_all_sentences_with_terminals(start_symbol, production_rules):
    all_possible = []
    for production in production_rules[start_symbol]:
        #print(production)
        all_production = []
        recursively_fill(production, production_rules, all_production)
        all_possible.extend(all_production)
    return all_possible
                
def parse_productions_and_xml(grammar_files, grammar_location, objects_xml_file, locations_xml_file, names_xml_file):
    production_rules = parse_production_rules(grammar_files, grammar_location)
    objects = parse_objects(objects_xml_file)
    categories = parse_categories(objects_xml_file)
    names = parse_names(names_xml_file)
    locations = parse_locations(locations_xml_file)
    rooms = parse_rooms(locations_xml_file)
    #add objects
    production_rules['{kobject}'] = objects
    production_rules['{aobject}'] = objects
    production_rules['{object}'] = objects
    production_rules['{category}'] = "objects"
    production_rules['{kobject?}'] = categories
    production_rules['{aobject?}'] = categories
    production_rules['{object?}'] = categories
    #add names
    production_rules['{name}'] = names
    production_rules['{name 1}'] = names
    production_rules['{name 2}'] = names
    #add locations
    production_rules['{placement}'] = locations
    production_rules['{placement 1}'] = locations
    production_rules['{placement 2}'] = locations
    production_rules['{beacon}'] = locations
    production_rules['{beacon 1}'] = locations
    production_rules['{beacon 2}'] = locations
    production_rules['{room}'] = rooms
    production_rules['{room 1}'] = rooms
    production_rules['{room 2}'] = rooms
    production_rules['{placement?}'] = rooms
    production_rules['{beacon?}'] = rooms
    production_rules['{room?}'] = "room"
    
    return production_rules
    
def print_all_highlevel_sentences(start_symbol, production_rules_highlevel, artificial_terminals):
    print("--- not necessary---")
    not_necessary = find_not_necessary_expansions(production_rules_highlevel, artificial_terminals)
    print(not_necessary)
    

    print("start symbol", start_symbol)
    print("all high level sentences---")
    all_sentences = generate_all_highlevel_sentences(start_symbol, production_rules_highlevel, not_necessary)
    #remove duplicates
    all_sentences = list(set(all_sentences))
    all_sentences.sort()
    for s in all_sentences:
        print(s)
    print(len(all_sentences))
    
def parse_semantics_file(semantics_file):
    prod_to_semantics = {}    
    with open(semantics_file) as f:
        for line in f:
            if len(line.strip()) > 0:
                parse = line.split(":")
                prod = parse[PRODUCTION].strip()
                sem = parse[SEMANTICS].strip()
                prod_to_semantics[prod] = sem
    return prod_to_semantics
            
    
    
   

if __name__=="__main__":
    objects_xml_file = '/home/dsbrown/Code/AustinVillaatHome/GPSRCmdGen/CommonFiles/Objects.xml'
    locations_xml_file = '/home/dsbrown/Code/AustinVillaatHome/GPSRCmdGen/CommonFiles/Locations.xml'
    names_xml_file = '/home/dsbrown/Code/AustinVillaatHome/GPSRCmdGen/CommonFiles/Names.xml'

    

    #grammar_location = '/home/daniel/Code/GPSRCmdGen/EEGPSRCmdGen/Resources/'
    grammar_location = '/home/dsbrown/Code/AustinVillaatHome/GPSRCmdGen/GPSRCmdGen/Resources/'
    #grammar_location = './'
    #grammar_files = ['eegpsr_cat2.txt']
    grammar_files = ['Category1Grammar.txt','CommonRules.txt']
    #grammar_files = ['TestGrammar.txt']
    #grammar_file = 'Category1Grammar_test.txt'
    #grammar_file = 'CommonRules.txt'
    artificial_terminals = ['$whattosay']
    
    
    #now start with a certain token and build out all the possibilities
    #production_rules = parse_productions_and_xml(grammar_files, grammar_location, objects_xml_file, locations_xml_file, names_xml_file)
    production_rules_highlevel = parse_production_rules(grammar_files, grammar_location)
    print_all_highlevel_sentences("$fndppl", production_rules_highlevel, artificial_terminals)
    
    print("---------")
    sentence = "$vbfind a person in the {room} and $vbspeak $whattosay"
    print(" expansions for ", sentence)
    print("----------")
    all_expansions = []
    recursively_fill_necessary(sentence, production_rules_highlevel, artificial_terminals, all_expansions)
    for s in all_expansions:
        print(s)
        
    #TODO add to tree
#    production_rules = parse_productions_and_xml(grammar_files, grammar_location, objects_xml_file, locations_xml_file, names_xml_file)
#    
#    print("-----------")
#    print("all full sentences")
#    print("-----------")
#    all_productions = []
#    recursively_fill(sentence, production_rules, all_productions)
#    for s in all_productions:
#        print(s)
    
    
    #print(production_rules)
    #all_expansions = []
    #sentence = "$vbfind the {kobject} in the {room}"
    #sentence = '$takefrom and $place'
    #print(sentence)
    #recursively_fill(sentence, production_rules, all_expansions)
    #print(all_expansions)
    #print(len(all_expansions))
    #check if duplicates
    #all_expansions = list(set(all_expansions))
    #print(len(all_expansions))
    #start_symbol = '$Main'
    #print("start symbol", start_symbol)
    #print("all sentences---")
    #all_sentences = generate_all_sentences(start_symbol, production_rules)
    #for s in all_sentences:
    #    print(s)
    #print(len(all_sentences))
    #print(generate_all_expansions(
    #    "$vbbring (me | to $whowhere) the {kobject} from the {placement}", 
    #        production_rules))
    
    
    
#    print("--- not necessary---")
#    not_necessary = find_not_necessary_expansions(production_rules)
#    print(not_necessary)
    
    
#    start_symbol = '$Main'
#    print("start symbol", start_symbol)
#    print("all high level sentences---")
#    all_sentences = generate_all_highlevel_sentences(start_symbol, production_rules, not_necessary)
#    #remove duplicates
#    all_sentences = list(set(all_sentences))
#    for s in all_sentences:
#        print(s)
#    print(len(all_sentences))
    
    
