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
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_selection import RFE
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from itertools import compress
import warnings
import math
import random

import data_util

warnings.filterwarnings('ignore')

graphs_wd = data_util.graphs_wd # directory to save the graphs in
ddd = False
regr_name_full_ = data_util.regr_name_full_

random.seed()


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
    global scaler
    ## Make this find a regression model for all (h,g) couples

    z = {}# each element is {key:list() for key in ('dur', 'pltime', 'heur', 'search', 'ex_nod', 'ev_stat')}

    pars = ['waiter','tot', 'avg_x', 'avg_y', 'hot_tot', 'hot_avg_x', 'hot_avg_y']
    
    x = {}# each element is {in_par:list() for in_par in pars}
    #des = "log(dur) + log(search/1000)"
    des1 = data_util.regr_goal1_ #'dur'
    des2 =  data_util.regr_goal2_ #'search'  
    
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
    nof_regr_approx = {}
    
    for hg_key in x.keys():        
        X = pd.DataFrame(x[hg_key].values())
        ### log chosen since from graphs an exp like behaviour seems to emerge
        Y1 = [ math.log(oo) for oo in z[hg_key][des1] ]
        Y2 = [ math.log(oo) for oo in z[hg_key][des2] ]  #1/1000 to pass into seconds from ms
        
        z[hg_key]['Q1'] = Y1
        z[hg_key]['Q2'] = Y2
        #Regression
        X_arr = np.array(X).T
        regr[hg_key] = list()
        nof_regr_approx[hg_key] = {}#{key:{} for key in [des1, des2]}
        print("Run: {} tot: {} fail: {}".format(hg_key, tot_run[hg_key], fail_run[hg_key]))
        
        for Y, des in zip([Y1, Y2], [des1, des2]):
            
            nof = 2
            X_train = X_arr
            y_train = np.array(Y)
            ### model = Pipeline([('scaler', StandardScaler()), ('linear_regression', LinearRegression())])
            model = Pipeline([('linear_regression', LinearRegression(normalize=True))])
        
            rfe = RFE(model, nof, importance_getter = 'named_steps.linear_regression.coef_')
            X_train_rfe = rfe.fit_transform(X_train, y_train)
            
            
            nof_score = cross_val_score(model, X_train_rfe, y_train, cv=5)
            #print("CV SCORES 2 {}, {}".format(lr_scores, lr_scores.mean()))
            model.fit(X_train_rfe, y_train)
            
            
            ### nof_score = model.score(X_test_rfe, y_test) 
            nof_coef = model.named_steps.linear_regression.coef_
                #    nof = nof_list[n]
            nof_supp = list(compress(pars, rfe.support_))
            
            ## coef of the nof most impacting features
            nof_regr_approx[hg_key][des] = model
           
            setattr(nof_regr_approx[hg_key][des], "pars", nof_supp)

            #Detect best features
            ### lin_regressor = Pipeline([('scaler', StandardScaler()), ('linear_regression', LinearRegression())])
            lin_regressor = Pipeline([('linear_regression', LinearRegression(normalize=True))])
            #rfe = RFE(RFE_regressor, nof)
            
            #RFE_regressor = Pipeline([('scaler', StandardScaler()), ('linear_regression', LinearRegression())])
            #rfe = RFE(RFE_regressor, nof, importance_getter= 'named_steps.linear_regression.coef_')
            
            ## removed rfe here, since the info on it are already computed in the prev. loop
            
            #X_rfe = rfe.fit_transform(X_arr, np.array(Y))
            lr_score = cross_val_score(lin_regressor, X_train, y_train, cv=5)
            
            
            lin_regressor.fit(X_arr, np.array(Y))
            
            regr[hg_key].append(lin_regressor)

            #Display regression output
            print("Hw: {}\tGw: {}".format(hg_key[0], hg_key[1]))
            print("Ratio of successful run:\t{}".format((tot_run[hg_key]-fail_run[hg_key])/tot_run[(hg_key)]))
            print("Regression INPUT:\t{}".format(pars))
            print("Regression OUTPUT:\t[{}]".format(des))
            print("Regression coefficients:\t{}".format(lin_regressor.named_steps.linear_regression.coef_)) #(top_coef))
            print("Regression intercept:\t{}".format(lin_regressor.named_steps.linear_regression.intercept_))
            print("Regression score:\t{}[{}]".format(lr_score.mean(), lr_score.std()))
            #print("Optimum number of feature: %d" %nof)
            print("Score with %d features {}[{}]".format(nof_score.mean(), nof_score.std()))
            print("The {} most relevat features are: {}".format(nof, nof_supp))
            print("##-------------##")
        print("#################")
    return x, z, regr, nof_regr_approx
    
def plot_corr(z_dict, save_fig=False):
    print("Plotting correlation figures, please wait...")
    for hg_key, z in z_dict.items():
    
        plotname = "corr " + str(hg_key)
        output_df = pd.DataFrame(z)
        sns.set(font_scale=1.6)
        #Parameters for latexstyle plot
        g = sns.PairGrid(output_df, aspect=1.4, diag_sharey=False)
        g.map_lower(sns.regplot, lowess=True, ci=False, line_kws={'color': 'black'})
        g.map_diag(sns.distplot, kde_kws={'color': 'black'})
        g.map_upper(corrdot)
        g.fig.canvas.set_window_title(plotname)
        #Save figure   
        if save_fig:
            plt.savefig(graphs_wd+"/Correlation_Matrix" + str(hg_key) + ".pdf")
            
    plt.show(block=False)       
    input("Close open correlation matrix windows...")
    plt.close('ALL')
    
def lim_d(d):
    return 1.1*d if d<0 else 0.9*d
def lim_u(u):
    return 1.1*u if u>0 else 0.9*u

def delog_out(model, x, y):
    #print(pipe_params)
    #input()
    #model = Pipeline(pipe_params)
    return math.exp(model.predict([[x,y]]))
    
predict_approx = np.vectorize(delog_out, excluded=[0])
   
    
def plot_graphs(k,j, nof_regr_approx, save_fig=False):
    # Display correlation matrix of ther output
    goals = (data_util.regr_goal1_, data_util.regr_goal2_)
    den_coeffs = {goals[0]:1, goals[1]:1000}

    for hg_key in nof_regr_approx.keys():
        
        z = {key:val for key, val in j[hg_key].items() if key in goals}
        z_approx = {}
        
            
        plot_num = 111
        ddd = True
        h_val = hg_key[0]
        g_val = hg_key[1]
        
        for name, z_val in z.items():
            pars = nof_regr_approx[hg_key][name].pars
            x = k[hg_key][pars[0]]
            y = k[hg_key][pars[1]]
            
            #cx = nof_regr_approx[hg_key][name][pars[0]]
            #cy = nof_regr_approx[hg_key][name][pars[1]]
            #ipt = nof_regr_approx[hg_key][name]['intercept']
            
            #cc = den_coeffs[name]
            
            figname = name + str(hg_key)
            fig = plt.figure(figname)
            filename = graphs_wd+"/"+figname.replace(" ", "_")+".pdf"
            #z_approx = [cc*math.exp(xx*nof_regr_approx[hg_key][name][pars[0]] + yy*nof_regr_approx[hg_key][name][pars[1]])
                                #for xx, yy in zip(x, y)]
            if ddd:
                ax = fig.add_subplot(plot_num, projection='3d')     
                plot = ax.scatter(x, y, z_val, cmap = 'rainbow', c=z_val)
                
                X, Y = np.meshgrid(np.linspace(lim_d(min(x)), lim_u(max(x)), 30), np.linspace(lim_d(min(y)), lim_u(max(y)), 30))
                
                #xxx = np.linspace(lim_d(min(x)), lim_u(max(x)), 30)
                #yyy = np.linspace(lim_d(min(y)), lim_u(max(y)), 30)
                
                #sx = scaler.inverse_transform([xxx, yyy])
                #sy = scaler.inverse_transform()
                
                #sX, sY = np.meshgrid(sx, sy)
                z_approx = predict_approx(nof_regr_approx[hg_key][name], X, Y)
                
                ax.plot_wireframe(X, Y, z_approx)
                
                ax.set_xlim(lim_d(min(x)),lim_u(max(x)))
                ax.set_ylim(lim_d(min(y)),lim_u(max(y)))
                ax.set_zlim(lim_d(min(z_val)), lim_u(max(z_val)))
                ax.set_xlabel(pars[0])
                ax.set_ylabel(pars[1])                       
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
    g_val = 1.0
    in_par1 = 'avg_x'
    in_par2 = 'avg_y'
    filename = ""
    show_goal_plot = False
    show_corr_plot = False
    save_fig = False
    
    usage = ("usage: pyhton3 " + argv[0] + "\n" +
             "(default values will be used in case options are not provided)\n" +
             "\t-c, --csv <arg>\t\tpath and name of the csv file to read (mandatory)\n" +
             "\t-d, --hg_val <arg>\tcouple of hw and gw [hw,gw]\n" +
             "\t-p, --corr-plot\t\tenable correlation matrices plots\n" +
             "\t-g, --goal-plot\t\tenable goals plots\n" +
             "\t-s, --save-figures\tsave all figures as pdf (in 'graphs' folder)\n" +
             "\t-h, --help\t\tdisplay this help\n"
            )
    try:
        opts, args = getopt.getopt(argv[1:], "hc:d:gps", ["help","csv=", "hg_val=", "goal-plot", "corr-plot", "save-figures"])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        elif opt in ("-c", "--csv"):
            filename = arg
        elif opt in ("-g", "--goal-plot"):
            show_goal_plot = True
        elif opt in ("-p", "--corr-plot"):
            show_corr_plot = True
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
                print("Not enough arguments")
                sys.exit()
    
    if not filename:
        print("Missing mandatory argument '-c' <csv_filepath>")
        sys.exit()
    
    try:
        print("try")
        with open(filename, newline='') as csvfile:
            print("Starting correlation step for data in {} with h:{} g:{}".format(filename, h_val, g_val))
            reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC) # set this when csv will be prop set
            
            k, z, regr_dict, nof_regr_approx = evaluate_corr(reader) #, h_val=h_val, g_val=g_val)
            ## load already explored drinks configurations
            
        ### SAVE REGR WITH PICKLE
        if show_corr_plot:    
            plot_corr(z, save_fig = save_fig)
        if show_goal_plot:    
            plot_graphs(k, z, nof_regr_approx, save_fig = save_fig)    
             
        ## save regression model
        with open(regr_name_full_, 'wb') as f:
            pickle.dump(regr_dict, f)
        
    except FileNotFoundError as e:
        print("File {} not found".format(e.filename))
        sys.exit() 
             

if __name__ == '__main__':
    main(sys.argv)
