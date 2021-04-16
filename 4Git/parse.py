#!/usr/bin/env python3

# Import dependencies

import sys, getopt

import os
import re

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from scipy.interpolate import griddata


#Set global variables
problem_name = "Custom.pddl"    # (str) Problem name, extension needed
out_wd = "../output"			# (str) Working directory
#output_string = "output_Custom.txt"

max_run_time = 120			# (int) maximum running time in seconds before stopping the run of the planning engine
output_keywords = ('Duration', 'Planning Time', 'Heuristic Time',
                    'Search Time', 'Expanded Nodes', 'States Evaluated')# list of (str): keywords for relevant outputs
index_keywords = ('H_VALUE', 'G_VALUE', 'SUCCESS')
#Paramenters
cwd = os.getcwd()

def parse(str_out):

    key_pos = {key:0 for key in output_keywords}
    key_val = {key:0 for key in output_keywords}
    index_pos = {key:0 for key in index_keywords}
    index_val = {key:0 for key in index_keywords}
    
    hg_val = {key:{} for key in output_keywords}
    
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
            index_val[k] = int(re.sub('\D', '', tmp)) #remove any leftover character from the int
            
            h_val = index_val[index_keywords[0]]
            g_val = index_val[index_keywords[1]]
            succ = index_val[index_keywords[2]]
        
        
        if f_flag < 0 or succ == 0:
        # if this try did not succeed try the next one; if we reached the end of the str exits
            continue
            
        for k, v in key_pos.items():
        # the new position of the keyword is the first one found after the prev one
            key_pos[k] = str_out.find(k, v, -1) + len(k)
            end = str_out.find("\n", key_pos[k], -1)
            tmp = str_out[key_pos[k]:end]
            key_val[k] = float(re.sub('[^0-9.]+', '', tmp)) #remove any leftover character from the int
            
            # matrix associating to the couple hw, gw the various parameters found when parsing
            hg_val[k][(h_val, g_val)] = key_val[k]
            
    return hg_val


def main(argv):
    """ This function asks the user to insert the number of
        customers for each table and to specify the number of 
        hot drinks for each of them and it automatically generates
        the problem file for the pddl planning engine
    """
    
    usage = ("usage: pyhton3 " + argv[0] + "\n" +
             "(default values will be used in case options are not provided)\n"
             "\t-n, --output-path <arg>\t\t path and name of the output file\n" +
             "\t-h, --help\t\t display this help\n"
            )
    output_string = ""
            
    #Input selector
    try:
        opts, args = getopt.getopt(argv[1:], "hn:", ["help", "output-path"])
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
        output_string = cwd + "/" + out_wd + "/output_" + problem_name[:-5] + ".txt"
    
    #Read the output file to detect the interesting keywords
    with open(output_string, "r") as read_run_output:
        str_out = read_run_output.read()
        hg_val = parse(str_out)
        
        for k in hg_val:
            print(k)
            for l, v in hg_val[k].items():
                print("\t" + str(l) + ":" + str(v) + "\n")

    #Output visualization
    plot_num = 111
    print(hg_val.keys())
    for key in hg_val.keys():
        print(key)
        if plot_num == 111:
            x = []
            y = []
            for sub_key in hg_val[key].keys():
                x.append(int(sub_key[0]))
                y.append(int(sub_key[1]))
        xi = np.linspace(min(x),max(x)) 
        yi = np.linspace(min(y),max(y)) 
        print(xi)
        print(yi)
        X, Y = np.meshgrid(xi, yi)
        z = list(hg_val[key].values())
        Z = griddata((x, y), z, (xi, yi),method='cubic')
        print(x)
        print(y)
        print(z)
        print(Z)
        fig = plt.figure(key)
        ax = fig.add_subplot(plot_num, projection='3d')


        #m = cm.ScalarMappable()
        #m.set_array(Z)
        #col = plt.colorbar(m)
        surf = ax.plot_trisurf(x, y, z)#, cmap = m.cmap, norm = m.norm)
        ax.set_xlim(0,1.1*max(x))
        ax.set_ylim(0,1.1*max(y))
        ax.set_zlim(0, 1.1*max(z))
        ax.set_xlabel('g')
        ax.set_ylabel('h')
        ax.set_zlabel(key)
        
        #Save figure
        plt.savefig(str(key+".pdf"))
        plt.close(key)

if __name__ == '__main__':
    main(sys.argv)
