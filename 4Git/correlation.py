#!/usr/bin/env python3

import csv
import run


import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn import linear_model



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

def main():
    data_dict = {}
    
    x = list()
    y = list()
    h_g = list()
    z = {key:list() for key in ('dur', 'pltime', 'heur', 'search', 'ex_nod', 'ev_stat')}

    
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile) # basically a list of dict
        
        for row in reader:
            print(row)
            #input()
            if row['hg_ratio'] != '63.8729833462074175':
                x.append(float(row['avg_x']))
                y.append(float(row['avg_y']))   
                h_g.append(float(row['hg_ratio']))
                z['dur'].append(float(row['Duration']))
                z['pltime'].append(float(row['Planning Time']))
                z['heur'].append(float(row['Heuristic Time']))
                z['search'].append(float(row['Search Time']))
                z['ex_nod'].append(float(row['Expanded Nodes']))
                z['ev_stat'].append(float(row['States Evaluated']))
                X = pd.DataFrame([x,y,h_g])
                Y1 = z['dur']
                Y2 = z['pltime']


        #Regression
        X_arr = np.array(X).T
        regr = linear_model.LinearRegression()  
        regr.fit(X_arr,pd.np.array(Y2))   
        regr.predict(X_arr)

        print(z)
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
        for name, z_val in z.items():
            fig = plt.figure(name)
            if ddd:
                ax = fig.add_subplot(plot_num, projection='3d')     
                plot = ax.scatter(x, y, z_val, cmap = 'rainbow', c=z_val)            
                ax.set_xlim(1.1*min(x),1.1*max(x))
                ax.set_ylim(1.1*min(y),1.1*max(y)) 
                ax.set_zlim(0.9*min(z_val), 1.1*max(z_val))
                ax.set_xlabel('avg_x')
                ax.set_ylabel('avg_y')                       
                ax.set_title(name)
            else:
                plot = plt.scatter(h_g, z_val)
                plt.xlabel(r"$ \frac{w_h}{w_g}$")
                plt.ylabel(name)   
      
            fig.colorbar(plot) 
            plt.savefig(graphs_wd+"/"+name.replace(" ", "_")+".pdf")
            plt.close(name)
   

        #Display regression output
        print(regr.coef_) 
        print(regr.score(X_arr,Y2))

if __name__ == '__main__':
    main()
