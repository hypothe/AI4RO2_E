#!/usr/bin/env python3

import csv
import run


import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D



graphs_wd = "../graphs" # directory to save the graphs in

filename = graphs_wd + "/hg_val_2611515120.csv"

def main():
    data_dict = {}
    
    x = list()
    y = list()
    z = {key:list() for key in ('dur', 'pltime')}

    
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile) # basically a list of dict
        
        for row in reader:
            #print(row)
            #input()
            if row['hw'] == row['gw'] == '1.0':
                x.append(float(row['avg_x']))
                y.append(float(row['avg_y']))
                z['dur'].append(float(row['Duration']))
                z['pltime'].append(float(row['Planning Time']))
               
        plot_num = 111
        for name, z_val in z.items():
            fig = plt.figure(name)
            ax = fig.add_subplot(plot_num, projection='3d')     
            plot = ax.scatter(x, y, z_val, cmap = 'rainbow', c=z_val)            
            ax.set_xlim(1.1*min(x),1.1*max(x))
            ax.set_ylim(1.1*min(y),1.1*max(y)) 
            ax.set_zlim(0.9*min(z_val), 1.1*max(z_val))
            ax.set_xlabel('avg_x')
            ax.set_ylabel('avg_y')                       
            ax.set_title(name)
            
            fig.colorbar(plot) 
            plt.savefig(graphs_wd+"/"+name.replace(" ", "_")+".pdf")
            plt.close(name)

if __name__ == '__main__':
    main()
