#!/usr/bin/env python3

import sys, getopt, re

import csv
import pickle

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn import linear_model
import warnings
import math

warnings.filterwarnings('ignore')

graphs_wd = "../graphs" # directory to save the graphs in
ddd = False
regr_name_full_ = "../lib/regr_model.pkl"


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

def evaluate_corr(data_dict, h_val=None, g_val=None):
    ## Make this find a regression model for all (h,g) couples

    z = {}# each element is {key:list() for key in ('dur', 'pltime', 'heur', 'search', 'ex_nod', 'ev_stat')}

    pars = ['waiter','tot', 'avg_x', 'avg_y', 'hot_tot', 'hot_avg_x', 'hot_avg_y']
    
    x = {}# each element is {in_par:list() for in_par in pars}
    #des = "log(dur) + log(search/1000)"
    des1 = 'dur'
    des2 = 'search' #'heur'   #'pltime' 
    
    tot_run = {}
    fail_run = {}
     
    for row in data_dict:
        #print(row.values())
        
        h = float(row['hw'])
        g = float(row['gw'])
        try:
            tot_run[(h, g)]
        except KeyError:
            tot_run[(h, g)] = 0
        finally:
            tot_run[(h, g)] += 1
            
        skip = False
        for v in row.values():
            if np.isnan(v):
                skip = True
                try:
                    fail_run[(h, g)]
                except KeyError:
                    fail_run[(h, g)] = 0
                finally:
                    fail_run[(h, g)] += 1
                break
        ## if h_val or g_val are not explicitly passed they'll be None, thus alway matching
        if not skip and h_val in (h, None) and g_val in (g, None):
            
            try:
                x[(h, g)]
            except KeyError:
                x[(h,g)] = {in_par:list() for in_par in pars}
            finally:
                for in_par in pars:
                    x[(h, g)][in_par].append(float(row[in_par]))
                    
            try:
                z[(h, g)]
            except KeyError:
                z[(h,g)] = {key:list() for key in ('dur', 'pltime', 'heur', 'search', 'ex_nod', 'ev_stat')}
            finally:
                z[(h,g)]['dur'].append(float(row['Duration']))
                z[(h,g)]['pltime'].append(float(row['Planning Time']))
                z[(h,g)]['heur'].append(float(row['Heuristic Time']))
                z[(h,g)]['search'].append(float(row['Search Time']))
                z[(h,g)]['ex_nod'].append(float(row['Expanded Nodes']))
                z[(h,g)]['ev_stat'].append(float(row['States Evaluated']))
                
    ## regr is a dict with keys (h,g) pair; in each cell are two elements,
    ## the two regression models for Y1 and Y2
    regr = {}
    
    for hg_key in x.keys():        
        X = pd.DataFrame(x[hg_key].values())
        #Y = z[des]
        ## FIRST attempt Quality function
        ### log chosen since from graphs an exp like behaviour seems to emerge
        #Y = [ math.log(oo1/10 + oo2/10000) for oo1, oo2 in zip(z[des1], z[des2])]
        #Y = [ math.log(oo1) + math.log(oo2/1000) for oo1, oo2 in zip(z[des1], z[des2])]
        Y1 = [ math.log(oo) for oo in z[hg_key][des1] ]
        Y2 = [ math.log(oo/1000) for oo in z[hg_key][des2] ]
        
        z[hg_key]['Q1'] = Y1
        z[hg_key]['Q2'] = Y2
        #Regression
        X_arr = np.array(X).T
        
        regr[hg_key] = list()
        
        for Y, des in zip([Y1, Y2], [des1, des2]):
            rr = linear_model.LinearRegression()  
            rr.fit(X_arr,pd.np.array(Y))   
            rr.predict(X_arr)
            
            regr[hg_key].append(rr)

            #Display regression output
            print("Hw: {}\tGw: {}".format(hg_key[0], hg_key[1]))
            print("Ratio of successful run:\t{}".format((tot_run[hg_key]-fail_run[hg_key])/tot_run[(hg_key)]))
            print("Regression INPUT:\t{}".format(pars))
            print("Regression OUTPUT:\t[{}]".format(des))
            print("Regression coefficient:\t{}".format(rr.coef_))
            print("Regression intercept:\t{}".format(rr.intercept_))
            print("Regression score:\t{}".format(rr.score(X_arr,Y)))
            print("##-------------##")
        print("#################")
    return x, z, regr
    
    
def plot_graphs(k, par1, par2, j, h_val, g_val, save_fig=False):
    # Display correlation matrix of ther output
    x = k[(h_val, g_val)][par1]
    y = k[(h_val, g_val)][par2]
    z = j[(h_val, g_val)]
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
    if save_fig:
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
        if save_fig:
            plt.savefig(filename)
            
    plt.show(block=False)
        
    input("Close open windows...")
    plt.close('ALL')


def main(argv):
    
    h_val = 1.0
    g_val = 15.0
    in_par1 = 'avg_x'
    in_par2 = 'avg_y'
    filename = ""
    show_plot = False
    save_fig = False
    
    usage = ("usage: pyhton3 " + argv[0] + "\n" +
             "(default values will be used in case options are not provided)\n" +
             "\t-c, --csv <arg>\t\tpath and name of the csv file to read (mandatory)\n" +
             "\t-d, --hg_val <arg>\tcouple of hw and gw [hw,gw]\n" +
             "\t-p, --plot\t\tenable plots\n" +
             "\t-s, --save-figures\tsave all figures as pdf (in 'graphs' folder)\n" +
             "\t-h, --help\t\tdisplay this help\n"
            )
    try:
        opts, args = getopt.getopt(argv[1:], "hc:d:ps", ["help","csv=", "hg_val=", "plot", "save-figures"])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        elif opt in ("-c", "--csv"):
            filename = arg
        elif opt in ("-p", "--plot"):
            show_plot = True
        elif opt in ("-s", "--save-figures"):
            save_fig = True
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
    
    if not filename:
        print("Missing mandatory argument '-c' <csv_filepath>")
        sys.exit()
    
    try:
        with open(filename, newline='') as csvfile:
            print("Starting correlation step for data in {} with h:{} g:{}".format(filename, h_val, g_val))
            reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC) # set this when csv will be prop set
            
            k, z, regr_dict = evaluate_corr(reader) #, h_val=h_val, g_val=g_val)
            ## load already explored drinks configurations
            
        ### SAVE REGR WITH PICKLE
        if show_plot:    
            plot_graphs(k, in_par1, in_par2, z, h_val, g_val, save_fig = save_fig)    
             
        ## save regression model
        with open(regr_name_full_, 'wb') as f:
            pickle.dump(regr_dict, f)
        
    except FileNotFoundError as e:
        print("File {} not found".format(e.filename))
        sys.exit() 
             

if __name__ == '__main__':
    main(sys.argv)
