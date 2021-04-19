#!/usr/bin/env python3

# Import dependencies

import sys, getopt

import os
import re

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D


#Set global variables
problem_name = "Custom.pddl"    	# (str) Problem name, extension needed
out_wd = "../output"			# (str) Working directory

output_keywords = ('Duration', 'Planning Time', 'Heuristic Time',
                    'Search Time', 'Expanded Nodes', 'States Evaluated')	# list of (str): keywords for relevant outputs
index_keywords = ('H_VALUE', 'G_VALUE', 'SUCCESS')
three_D = False
ratio = True

graphs_wd = "../graphs" # directory to save the graphs in

#Paramenters
cwd = os.getcwd()
#Parameters for latexstyle plot
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

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
    
def plot_hg(hg_val, ddd):
    plot_num = 111
    #print(hg_val.keys())

    x = []
    y = []
    z = {key:[] for key in output_keywords}
    
    for hg_key in hg_val.keys(): #(h,g)
        #print(key)
        x.append(int(hg_key[0]))
        y.append(int(hg_key[1]))
        
        if plot_num == 111:
            for sub_key in hg_val[hg_key].keys():
                z[sub_key].append(hg_val[hg_key][sub_key])
    for key in z:
        fig = plt.figure(key)
        
        if ddd:      
            ax = fig.add_subplot(plot_num, projection='3d')     
            plot = ax.scatter(x, y, z[key], cmap = 'rainbow', c=z[key])            
            ax.set_xlim(0,1.1*max(x))
            ax.set_ylim(0,1.1*max(y)) 
            ax.set_zlim(0.9*min(z[key]), 1.1*max(z[key]))
            ax.set_xlabel('g')
            ax.set_ylabel('h')                       
            ax.set_title(key)
        else:
            plot = plt.scatter(np.true_divide(np.array(x), np.array(y)), z[key], c=z[key], cmap = 'rainbow')
            plt.xlabel(r"$ \frac{w_g}{w_h}$")
            plt.ylabel(key)
        fig.colorbar(plot) 

        #Save figure
        plt.savefig(graphs_wd+"/"+key.replace(" ", "_")+".pdf")
        plt.close(key)

def main(argv):
    """ This function asks the user to insert the number of
        customers for each table and to specify the number of 
        hot drinks for each of them and it automatically generates
        the problem file for the pddl planning engine
    """
    
    usage = ("usage: pyhton3 " + argv[0] + "\n" +
             "(default values will be used in case options are not provided)\n"
             "\t-n, --output-path <arg>\tpath and name of the output file\n" +
             "\t--3d\t\t\tgenerate 3D plots instead of 2D ones\n" +
             "\t--tex\t\t\tgenerate plots with LaTeX style\n" +
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
        elif opt in ("--3d"):
            ddd = True
        elif opt in ("--tex"):
            plt.rc('text', usetex=True)
    
    if not output_string:
        output_string = cwd + "/" + out_wd + "/output_" + problem_name[:-5] + ".txt"
    
    #Read the output file to detect the interesting keywords
    with open(output_string, "r") as read_run_output:
        str_out = read_run_output.read()
        hg_val = parse(str_out)
   
    plot_hg(hg_val, ddd)     

    #Output visualization
    

if __name__ == '__main__':
    main(sys.argv)
