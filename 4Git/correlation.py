#!/usr/bin/env python3

import sys, getopt

import csv
import run

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn import linear_model
import warnings

warnings.filterwarnings('ignore')

graphs_wd = "../graphs" # directory to save the graphs in
ddd = False

filename = graphs_wd + "/hg_val_permTest_0121.csv"


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

def evaluate_corr(csvfile, h_val, g_val):

    x = list()
    y = list()
    k = list()
    z = {key:list() for key in ('dur', 'pltime', 'heur', 'search', 'ex_nod', 'ev_stat')}

    par1 = 'avg_x'  #'eig_1'
    par2 = 'avg_y'  #'eig_2'
    par3 = 'tot'    #'hg_ratio'
    
    des = 'pltime'  #'dur'
    
    reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC) # set this when csv will be prop set
    #reader = csv.DictReader(csvfile) # basically a list of dict   
     
    for row in reader:
        #print(row.values())
        skip = False
        for v in row.values():
            if np.isnan(v):
                skip = True
                break
        
        if not skip and round(float(row['hw'])) == h_val and round(float(row['gw'])) == g_val:
        #if row['hg_ratio'] != '63.8729833462074175':
            x.append(float(row[par1]))
            y.append(float(row[par2]))   
            k.append(float(row[par3]))
            z['dur'].append(float(row['Duration']))
            z['pltime'].append(float(row['Planning Time']))
            z['heur'].append(float(row['Heuristic Time']))
            z['search'].append(float(row['Search Time']))
            z['ex_nod'].append(float(row['Expanded Nodes']))
            z['ev_stat'].append(float(row['States Evaluated']))
            #X = pd.DataFrame([x,y,k])
            X = pd.DataFrame([x,y,k])
            Y = z[des]

    #Regression
    X_arr = np.array(X).T
    regr = linear_model.LinearRegression()  
    regr.fit(X_arr,pd.np.array(Y))   
    regr.predict(X_arr)

    #print(z)
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
               
    plot_num = 111
    ddd = True
    for name, z_val in z.items():
        fig = plt.figure(name)
        filename = graphs_wd+"/"+name.replace(" ", "_")+'h'+str(h_val).replace(".", "_")+'g'+str(g_val).replace(".", "_")+".pdf"

        if ddd:
            ax = fig.add_subplot(plot_num, projection='3d')     
            plot = ax.scatter(x, y, z_val, cmap = 'rainbow', c=z_val)            
            ax.set_xlim(1.1*min(x),1.1*max(x))
            ax.set_ylim(1.1*min(y),1.1*max(y)) 
            ax.set_zlim(0.9*min(z_val), 1.1*max(z_val))
            ax.set_xlabel(par1)
            ax.set_ylabel(par2)                       
            ax.set_title(name)
            for xx, yy, zz in zip(x, y, z_val):
                ax.plot([xx, xx], [yy, yy], [0.9*min(z_val),zz], 'k--', alpha=0.5, linewidth=0.5)
                
            ax.view_init(azim=-110, elev=20)
                
        else:
            plot = plt.scatter(x, y, c=z_val, cmap = 'rainbow')
            plt.xlabel(par1)
            plt.ylabel(par2)
            plt.title(name)
                
        fig.colorbar(plot)
        plt.savefig(filename)
            
    plt.show(block=False)
        
    #Display regression output
    print("Regression INPUT: [{}, {}, {}]".format(par1, par2, par3))
    print("Regression OUTPUT: [{}]".format(des))
    print("Regression coefficient:\t{}".format(regr.coef_))
    print("Regression score:\t{}".format(regr.score(X_arr,Y)))
    input("Close open windows...")
    plt.close('ALL')


def main(argv):
    
    h_val = 1.0
    g_val = 15.0
    
    usage = ("usage: pyhton3 " + argv[0] + "\n" +
             "(default values will be used in case options are not provided)\n"
             "\t-c, --csv <arg>\tpath and name of the csv file to read\n",
             "\t-d, --hg_val <arg>\tcouple of hw and gw [hw,gw]\n",
             "\t-h, --help\t\tdisplay this help\n"
            )
    try:
        opts, args = getopt.getopt(argv[1:], "hc:d:", ["help","csv=", "hg_val="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        elif opt in ("-c", "--csv"):
            filename = arg
        elif opt in ("-d", "--hg_val"):
            ll = re.findall("\d\.?\d*", arg)
            try:
                h_val = float(ll[0])
                g_val = float(ll[1])
            except ValueError:
                print("h and g values should be float")
                sys.exit()
            except IndexError:
                print("Too few arguments")
                sys.exit()

    try:
        with open(filename, newline='') as csvfile:
            print("Starting correlation step for data in {} with h:{} g:{}".format(filename, h_val, g_val))
            evaluate_corr(csvfile, h_val, g_val)
        
    except FileNotFoundError:
        print("File {} not found".format(arg))
        sys.exit() 
             

if __name__ == '__main__':
    main(sys.argv)
