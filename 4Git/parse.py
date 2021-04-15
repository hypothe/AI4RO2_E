#!/usr/bin/env python3
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Import dependencies
#import PySimpleGUI as sg 	# disabled for multiple run on docker
import os
import re
#import plotly.express as px
#import pandas as pd


#Set global variables
problem_name = "Custom.pddl"    # (str) Problem name, extension needed
wd = "run"			# (str) Working directory
output_string = "output_Custom.txt"

max_run_time = 120			# (int) maximum running time in seconds before stopping the run of the planning engine
output_keywords = ('Duration', 'Planning Time', 'Heuristic Time',
                    'Search Time', 'Expanded Nodes', 'States Evaluated')# list of (str): keywords for relevant outputs
index_keywords = ('H_VALUE', 'G_VALUE', 'SUCCESS')
#Paramenters
cwd = os.getcwd()

def parse(read_file):

    key_pos = {key:0 for key in output_keywords}
    key_val = {key:0 for key in output_keywords}
    index_pos = {key:0 for key in index_keywords}
    index_val = {key:0 for key in index_keywords}
    
    hg_val = {key:{} for key in output_keywords}
    
    print(index_pos)
    f_flag = 1
        
    while f_flag > 0:
        for k, v in index_pos.items():
        # sear for H, G,  SUCC, remove the string part and take the int value
            ind = str_out.find(k, v, -1)
            
            if ind < 0:
                f_flag = ind
                break
                
            index_pos[k] = ind + len(k)  
            print(k + " pos: " + str(index_pos[k]) + "\n")
              
            end = str_out.find("\n", index_pos[k], -1)
            tmp = str_out[index_pos[k]:end]
            index_val[k] = int(re.sub('\D', '', tmp)) #remove any leftover character from the int
            
            h_val = index_val[index_keywords[0]]
            g_val = index_val[index_keywords[1]]
            succ = index_val[index_keywords[2]]
        
        
        if f_flag < 0 or succ == 0:
        # if this try did not succeed try the next one; if we reached the end of the str exits
            continue
                
        print("H:" + str(h_val) + " G: " + str(g_val) + " SUCC: " + str(succ) + "\n")
        #input()
            
        for k, v in key_pos.items():
        # the new position of the keyword is the first one found after the prev one
            key_pos[k] = str_out.find(k, v, -1) + len(k)
            end = str_out.find("\n", key_pos[k], -1)
            tmp = str_out[key_pos[k]:end]
            key_val[k] = float(re.sub('[^0-9.]+', '', tmp)) #remove any leftover character from the int
            
            # matrix associating to the couple hw, gw the various parameters found when parsing
            hg_val[k][(h_val, g_val)] = key_val[k]
            print(tmp + "\n")
            

    return hg_val


if __name__ == '__main__':
    """ This function asks the user to insert the number of
        customers for each table and to specify the number of 
        hot drinks for each of them and it automatically generates
        the problem file for the pddl planning engine
    """
    #Input selector
    
    
    #Read the output file to detect the interesting keywords
    with open(cwd + "/" + wd + "/"+ output_string, "r") as read_run_output:
        str_out = read_run_output.read()
        hg_val = parse(str_out)
        
        for k in hg_val:
            print(k)
            for l, v in hg_val[k].items():
                print("\t" + str(l) + ":" + str(v) + "\n")
                    
