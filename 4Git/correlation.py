#!/usr/bin/env python3

import csv
import run

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D



graphs_wd = "../graphs" # directory to save the graphs in

filename = graphs_wd + "/hg_val_permTest_0121.csv"

def main():
    data_dict = {}
    
    x = list()
    y = list()
    z = {key:list() for key in ('dur', 'pltime')}

    par1 = 'avg_x' #'eig_1'
    par2 = 'avg_y' #'eig_2'
    
    with open(filename, newline='') as csvfile:
        # reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC) # set this when csv will be prop set
        reader = csv.DictReader(csvfile) # basically a list of dict
        
        
        h_val = 1
        g_val = 15
        for row in reader:
            #print(row)
            #input()
            if round(float(row['hw'])) == h_val and round(float(row['gw'])) == g_val:
                x.append(float(row[par1]))
                y.append(float(row[par2]))
                z['dur'].append(float(row['Duration']))
                z['pltime'].append(float(row['Planning Time']))
               
        plot_num = 111
        ddd = True
        for name, z_val in z.items():
            fig = plt.figure(name)
            title = name + " h: " + str(h_val) + " g: " + str(g_val)
            if ddd:
                ax = fig.add_subplot(plot_num, projection='3d')     
                plot = ax.scatter(x, y, z_val, cmap = 'rainbow', c=z_val)            
                ax.set_xlim(1.1*min(x),1.1*max(x))
                ax.set_ylim(1.1*min(y),1.1*max(y)) 
                ax.set_zlim(0.9*min(z_val), 1.1*max(z_val))
                ax.set_xlabel(par1)
                ax.set_ylabel(par2)                       
                ax.set_title(title)
                for xx, yy, zz in zip(x, y, z_val):
                    
                    ax.plot([xx, xx], [yy, yy], [0.9*min(z_val),zz], 'k--', alpha=0.5, linewidth=0.5)
                
                ax.view_init(azim=-110, elev=20)
                
                
            else:
                plot = plt.scatter(x, y, c=z_val, cmap = 'rainbow')
                plt.xlabel(par1)
                plt.ylabel(par2)
                plt.title(title)
                
            fig.colorbar(plot)
            plt.savefig(graphs_wd+"/"+name.replace(" ", "_")+'h'+str(h_val)+'g'+str(g_val)+".pdf")
            
        plt.show(block=False)
        input("Close open windows...")
        plt.close('ALL')
        

if __name__ == '__main__':
    main()
