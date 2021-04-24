#!/usr/bin/env python3

# Import dependencies

import sys, getopt

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D


#Set global variables
problem_name = "output_AAA.txt"    			# (str) Problem name, extension needed
out_wd = "/root/AI4RO_II/AI4RO2_E/output"		# (str) Working directory

output_keywords = ('Duration', 'Planning Time', 'Heuristic Time',
                    'Search Time', 'Expanded Nodes', 'States Evaluated')	# list of (str): keywords for relevant outputs
index_keywords = ('H_VALUE', 'G_VALUE', 'SUCCESS')
three_D = True
ratio = False

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
            
    
def plot_hg(hg_val, ddd):
    plot_num = 111
    #print(hg_val.keys())

    h = []
    g = []
    z = {key:[] for key in output_keywords}    
    
    for hg_key in hg_val.keys(): 
        h.append(int(hg_key[0]))
        g.append(int(hg_key[1]))
        
        if plot_num == 111:
            for sub_key in hg_val[hg_key].keys():
                z[sub_key].append(hg_val[hg_key][sub_key])
    
    # Display correlation matrix of ther output
    output_df = pd.DataFrame(z)
    plt.figure("corr")
    sns.set(font_scale=1.6)
    #Parameters for latexstyle plot
    #plt.rc('text', usetex=True)
    #plt.rc('font', family='serif')
    g = sns.PairGrid(output_df, aspect=1.4, diag_sharey=False)
    g.map_lower(sns.regplot, lowess=True, ci=False, line_kws={'color': 'black'})
    g.map_diag(sns.distplot, kde_kws={'color': 'black'})
    g.map_upper(corrdot)
    #Save figure   
    plt.savefig(graphs_wd+"/Correlation_Matrix.pdf")
    plt.close("corr")
    # Plot the output
    for key in z:
        fig = plt.figure(key)
        
        if ddd:      
            ax = fig.add_subplot(plot_num, projection='3d')     
            plot = ax.scatter(h, g, z[key], cmap = 'rainbow', c=z[key])            
            ax.set_xlim(0,1.1*max(h))
            ax.set_ylim(0,1.1*max(g)) 
            ax.set_zlim(0.9*min(z[key]), 1.1*max(z[key]))
            ax.set_xlabel('h')
            ax.set_ylabel('g')                       
            ax.set_title(key)
        else:
            plot = plt.scatter(np.true_divide(np.array(h), np.array(g)), z[key], c=z[key], cmap = 'rainbow')
            plt.xlabel(r"$ \frac{w_h}{w_g}$")
            plt.ylabel(key)
        fig.colorbar(plot) 

        #Save figure
        plt.savefig(graphs_wd+"/"+key.replace(" ", "_")+".pdf")
        plt.close(key)



def corrdot(*args, **kwargs):
    corr_r = args[0].corr(args[1], 'pearson')
    corr_text = f"{corr_r:2.2f}".replace("0.", ".")
    ax = plt.gca()
    ax.set_axis_off()
    marker_size = abs(corr_r) * 10000
    ax.scatter([.5], [.5], marker_size, [corr_r], alpha=0.6, cmap="coolwarm",
               vmin=-1, vmax=1, transform=ax.transAxes)
    font_size = abs(corr_r) * 40 + 5
    ax.annotate(corr_text, [.5, .5,],  xycoords="axes fraction",
                ha='center', va='center', fontsize=font_size)


def main(argv):
    """ This function asks the user an output file of a enhsp run
    	to extract the relevant pieces of information and produce 
    	a summary of the output to be processed by the correlation.py
    	script.
    	Relevant data are also plotted.
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
        output_string = out_wd + "/" + problem_name
    
    #Read the output file to detect the interesting keywords
    with open(output_string, "r") as read_run_output:
        str_out = read_run_output.read()
        hg_val = parse(str_out)
   
    plot_hg(hg_val, ddd)     
    

if __name__ == '__main__':
    main(sys.argv)
