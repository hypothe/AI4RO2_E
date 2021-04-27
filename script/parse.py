#!/usr/bin/env python3

# Import dependencies

import sys, getopt

import os
import re
import pandas as pd
import numpy as np


#Set global variables
problem_name = "output_Custom.pddl"    	# (str) Problem name, extension needed
out_wd = "/root/AI4RO_II/AI4RO2_E/output"			# (str) Working directory

output_keywords = ('Duration', 'Planning Time', 'Heuristic Time',
                    'Search Time', 'Expanded Nodes', 'States Evaluated')	# list of (str): keywords for relevant outputs
index_keywords = ('H_VALUE', 'G_VALUE', 'SUCCESS')
three_D = True
ratio = False

graphs_wd = "../graphs" # directory to save the graphs in

#Paramenters
cwd = os.getcwd()

def parse(str_out):

    key_pos = {key:0 for key in output_keywords}
    key_val = {key:0 for key in output_keywords}
    index_pos = {key:0 for key in index_keywords}
    index_val = {key:0 for key in index_keywords}
        
    hg_val = {}
    
    f_flag = 1
        
    while f_flag > 0:
        for k, v in index_pos.items():
        # sear for H, G,  SUCC, remove the string part and take the int value
            ind = str_out.find(k, v, -1)
            
            if ind < 0:
                f_flag = ind
                break
                
            index_pos[k] = ind + len(k)
              
            end = str_out.find("\n", index_pos[k], -1)
            tmp = str_out[index_pos[k]:end]
            index_val[k] = float(re.sub('[^\d\.]', '', tmp)) #remove any leftover character from the int
            
            h_val = index_val[index_keywords[0]]
            g_val = index_val[index_keywords[1]]
            succ = index_val[index_keywords[2]]
                
        if f_flag < 0:
        # if this try did not succeed try the next one; if we reached the end of the str exits
            continue
        
        hg_val[(h_val, g_val)] = {key:{} for key in output_keywords}    
        
        for k, v in key_pos.items():
        # the new position of the keyword is the first one found after the prev one
            if succ == 0: #unsuccessful run, fill values with placeholder
                hg_val[(h_val, g_val)][k] = float('nan')
                continue
                
            key_pos[k] = str_out.find(k, v, -1) + len(k)
            end = str_out.find("\n", key_pos[k], -1)
            tmp = str_out[key_pos[k]:end]
            key_val[k] = float(re.sub('[^\d\.]+', '', tmp)) #remove any leftover character from the int
            
            # matrix associating to the couple hw, gw the various parameters found when parsing
            
            hg_val[(h_val, g_val)][k] = key_val[k]
            
    return hg_val
    
def parse_problem(problem_filename):
    #fl_hot = "(= (fl-hot drinkA) 1)"
    #table = "(ordered drinkA table1 )"
    with open(problem_filename, 'r') as f:
        problem = f.read()
        
        drinks_str = re.findall("\(=\s+\(fl-hot\s+drink\w+\)\s+\d\)", problem)
        drink_dict = {}
        
        waiter_str = re.findall("\(free-waiter\s+w\d+\)", problem)
        n_waiters = len(waiter_str)
        
        table_str = re.search("table.*\s*-\s*Table", problem).group()
        table_num = len(re.findall("table\d+", table_str))
        
        for drink in drinks_str:
            ## find name of the dirnk, eg "drinkA"
            d_id = re.sub("(\(=\s+\(fl-hot\s+|\)\s+\d\))", "", drink)
            ## find if such drink was hot (1) or cold (0)
            d_fl = int(re.sub("(^\(=\s+\(fl-hot\s+drink\w+\)\s+|\s*\)$)", "", drink))
            drink_dict[d_id] = d_fl
        
        order_str = re.findall("\(ordered\s+drink\w+\s+table\w+\s*\)", problem)
        #print("ORDER_STR".format(order_str))
        
        table_orders = [list() for ii in range(0, table_num)]
        
        for order in order_str:
            ## find number of the table
            t_id = int(re.sub("(^\(ordered\s+drink\w+\s+table|\s*\)$)", "", order))
            ## find name of the drink
            t_dr = re.sub("(^\(ordered\s+|\s+table\w+\s*\)$)", "", order)
            ## ducktaping a lot
            table_orders[t_id-1].append(t_dr)
            #try:
            #    table_dict[t_id]
            #except KeyError:
            #    table_dict[t_id] = list()
            #finally:
            #    table_dict[t_id].append(t_dr)

        drink4table = [0 for ii in range(0, table_num)]
        hot4table = [0 for ii in range(0, table_num)]

        for t_id in range(0, table_num):
            drink4table[t_id-1] = len(table_orders[t_id-1])
            for drink in table_orders[t_id-1]:
                if drink_dict[drink] > 0:
                    hot4table[t_id-1] += 1
                    
        return n_waiters, drink4table, hot4table
            
def main(argv):
    """ This function asks the user to insert the number of
        customers for each table and to specify the number of 
        hot drinks for each of them and it automatically generates
        the problem file for the pddl planning engine
    """
    
    usage = ("usage: pyhton3 " + argv[0] + "\n" +
             "(default values will be used in case options are not provided)\n"
             "\t-n, --output-path <arg>\tpath and name of the output file\n" +
             "\t-h, --help\t\tdisplay this help\n"
            )
    output_string = ""
    ddd = three_D
    #Input selector
    try:
        opts, args = getopt.getopt(argv[1:], "hn:", ["help", "output-path=", "3d", "tex"])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        elif opt in ("-n", "--output-name"):
            output_string = arg
    
    if not output_string:
        output_string = out_wd + "/" + problem_name[:-5] + ".txt"
    
    #Read the output file to detect the interesting keywords
    with open(output_string, "r") as read_run_output:
        str_out = read_run_output.read()
        hg_val = parse(str_out)
     

if __name__ == '__main__':
    main(sys.argv)
