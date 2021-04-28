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
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_selection import RFE
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from itertools import compress
import warnings
import math
import copy

import data_util

# Necessary due to old packages
warnings.filterwarnings('ignore')

graphs_wd = data_util.graphs_wd # directory to save the graphs in
ddd = False
regr_name_full_ = data_util.regr_name_full_



def corrdot(*args, **kwargs):
    """
    Generate correlation matix graphs and plots it
    """
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
    """
    Function to generate and train the linear regressor models
    on the saved dataset
    
    Data is gathered from a dictionary (in this case a csv)
    containing the results of multiple pl.eng. runs on various
    problem instances, each performed for a collection of tuplse
    (hw,gw).
    Data rows are splitted depending on the (hw,gw); for each
    of the goals ('Duration', 'Search Time') a number of features
    is selected using an RFE for any number of features - from 1
    to all the available ones - choosing the model with the best
    r^2 score over 5-fold cross-validation.
    
    Args:
        data_dict (dict):   dictionary containing test data
        h_val (float):      restrict the search to only one
                            value of hw
                            (default=None, consider all entries)
        g_val (float):      restrict the search to only one
                            value of gw
                            (default=None, consider all entries)
                            
    Returns:
        x, z, regr, nof_regr_approx
        x (dict):           collection of input features
        z (dict):           collection of output features
        regr (dict):        collection of all the trained models
        nof_regr_approx (dict):
                            collection of the models trained only
                            on the 2 most important features for
                            each (hw,gw)x(goal), which are then
                            used for plotting
        
    """

    

    pars = ['waiter','tot', 'avg_x', 'avg_y', 'hot_tot', 'hot_avg_x', 'hot_avg_y']
    
    des = data_util.regr_goals_ #'dur', 'search'  
    z = {}# each element is {key:list() for key in ('dur', 'pltime', 'heur', 'search', 'ex_nod', 'ev_stat')}
    x = {}# each element is {in_par:list() for in_par in pars}
    tot_run = {}
    fail_run = {}
     
    for row in data_dict:
        
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
        Y = {key:list() for key in des}
        ### log chosen since from graphs an exp like behaviour seems to emerge
        for dd in des:
            Y[dd] = [ math.log(oo) for oo in z[hg_key][dd] ]
            z[hg_key]['Q_'+dd] = Y[dd]
            
        #Regression
        X_arr = np.array(X).T
        #regr[hg_key] = list()
        nof_regr_approx[hg_key] = {}
        print("Run: {} tot: {} fail: {}".format(hg_key, tot_run[hg_key], fail_run[hg_key]))
        
        lin_regressor = {}
        lr_score = {}
        
        for dd, yy in Y.items():
            plot_nof = 2
            num_params = X_arr.shape[1]
            
            X_train = X_arr
            y_train = np.array(yy)
            
            top_score = -float('inf')
            
            for nof in range(1, num_params+1):
            
                model = Pipeline([('scaler', StandardScaler()), ('linear_regression', Ridge())])
                ## Recursive Feature Elimination, generate a model getting as imput only the 'nof' most impacting
                ## features, keep the better performing one
                rfe = RFE(model, nof, importance_getter = 'named_steps.linear_regression.coef_')
                
                nof_score = cross_val_score(rfe, X_train, y_train, cv=5)
                
                if nof_score.mean() > top_score:
                    lin_regressor[dd] = copy.deepcopy(rfe)
                    lin_regressor[dd].fit(X_train, y_train)
                    top_score = nof_score.mean()
                ## keep the model with 2 feats in any case, it will be used for plotting
                if nof == 2:
                    rfe.fit(X_train, y_train)
                    nof_coef = rfe.estimator_.named_steps.linear_regression.coef_
                    nof_supp = list(compress(pars, rfe.support_))
                    ## coef of the nof most impacting features
                    nof_regr_approx[hg_key][dd] = rfe.estimator_
                    setattr(nof_regr_approx[hg_key][dd], "pars", nof_supp)

            lr_score[dd] = cross_val_score(lin_regressor[dd], X_train, y_train, cv=5)
            

            #Display regression output
            print("Hw: {}\tGw: {}".format(hg_key[0], hg_key[1]))
            print("Ratio of successful run:\t{}".format((tot_run[hg_key]-fail_run[hg_key])/tot_run[(hg_key)]))
            print("Regression INPUT:\t{}".format(pars))
            print("Regression OUTPUT:\t[{}]".format(dd))
            print("Regression coefficients:\t{}".format(lin_regressor[dd].estimator_.named_steps.linear_regression.coef_))
            print("Regression intercept:\t{}".format(lin_regressor[dd].estimator_.named_steps.linear_regression.intercept_))
            print("Regression score:\t{} [{}]".format(lr_score[dd].mean(), lr_score[dd].std()))
            print("Score with {} features {} [{}]".format(nof, nof_score.mean(), nof_score.std()))
            print("The {} most relevat features are: {}".format(lin_regressor[dd].n_features_,
                                                                list(compress(pars, lin_regressor[dd].support_))))
            print("##-------------##")
        
        ### TODO: for the moment, if a model is deemed unable to provide trustworthy results
        ######### (here evaluated thanks to r^2) it is simply ignored
        ######### In the future would be interesting to perhaps make this value impact the quality
        ######### of the solution found in 'run.py'    
        if all(val.mean() > 0.5 for val in lr_score.values()):
            regr[hg_key] = {des:regr for des,regr in lin_regressor.items()}
            
        print("#################")
        
    return x, z, regr, nof_regr_approx
    
def plot_corr(z_dict, save_fig=False, show_fig=False):
    """
    Plot the correlation matrix graphs between the output
    features
    
    Args:
        z_dict (dict):      collection of output features
        save_fig (bool):    wheter to save the plots (as pdf)
                            or not
        show_fig (bool):    wheter to show the plots (as pdf)
                            or not
    """
    
    print("Generating correlation figures, please wait...")
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
            plt.savefig(graphs_wd+"/Correlation_Matrix_"+str(hg_key[0])+"_"+str(hg_key[1]) + ".pdf")
            
    if show_fig:        
        plt.show(block=False)       
        input("Close open correlation matrix windows...")
        plt.close('ALL')
    
def lim_d(d):
    """
    Lower axis extrema
    """
    md = min(d)
    return 1.1*md if md<0 else 0.9*md
def lim_u(u):
    """
    Upper axis extrema
    """
    mu = max(u)
    return 1.1*mu if mu>0 else 0.9*mu

def delog_predict(model, x, y):
    """
    Get the predicted value given 2 input features
    """
    return math.exp(model.predict([[x,y]]))

### Vectorization of the prediction function    
predict_approx = np.vectorize(delog_predict, excluded=[0])

    
def plot_graphs(k,j, nof_regr_approx, save_fig=False, show_fig=False):
    """
    Plot the goal prediction graphs
    
    The x and y axes represent the 2 most important features
    for the 2-features RFE model, while the z axis shows real
    data as colored points and the regression curve generated
    by the model.
    
    Args:
        k (dict):           collection of input features
        j (dict):           collection of output features
        save_fig (bool):    wheter to save the plots (as pdf)
                            or not
        show_fig (bool):    wheter to show the plots (as pdf)
                            or not
    """
    print("Generating goal graphs, please wait...")
    # Display correlation matrix of ther output
    goals = data_util.regr_goals_
    plot_num = 111
    
    for hg_key in nof_regr_approx.keys():
        
        z = {key:val for key, val in j[hg_key].items() if key in goals}
        z_approx = {}
        h_val = hg_key[0]
        g_val = hg_key[1]
        
        for name, z_val in z.items():
            pars = nof_regr_approx[hg_key][name].pars
            x = k[hg_key][pars[0]]
            y = k[hg_key][pars[1]]
            
            figname = name + "_" + str(hg_key[0])+"_"+str(hg_key[1]) 
            fig = plt.figure(figname)
            filename = graphs_wd+"/"+figname.replace(" ", "_")+".pdf"
            
            ax = fig.add_subplot(plot_num, projection='3d')     
            plot = ax.scatter(x, y, z_val, cmap = 'rainbow', c=z_val)
                
            X, Y = np.meshgrid(np.linspace(lim_d(x), lim_u(x), 30), np.linspace(lim_d(y), lim_u(y), 30))
                
            z_approx = predict_approx(nof_regr_approx[hg_key][name], X, Y)
                
            ax.plot_wireframe(X, Y, z_approx, alpha=0.3)
                
            ax.set_xlim(lim_d(x),lim_u(x))
            ax.set_ylim(lim_d(y),lim_u(y))
            ax.set_zlim(lim_d(z_val), lim_u(z_val))
            ax.set_xlabel(pars[0])
            ax.set_ylabel(pars[1])                       
            ax.set_title(name)
            # lines projection of points
            for xx, yy, zz in zip(x, y, z_val):
                ax.plot([xx, xx], [yy, yy], [lim_d(z_val),zz], 'k--', alpha=0.5, linewidth=0.5)
                   
            ax.view_init(azim=-110, elev=20)
                    
            fig.colorbar(plot)
            if save_fig:
                plt.savefig(filename)
                
    if show_fig:        
        plt.show(block=False)
        input("Close open windows...")
        plt.close('ALL')


def main(argv):
    """
    Script to perform regression and check correlation between data
    on the results of multiple planning engin run, collected in a csv.
    """
    
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
        if show_corr_plot or save_fig:    
            plot_corr(z, save_fig = save_fig, show_fig = show_corr_plot)
        if show_goal_plot or save_fig:    
            plot_graphs(k, z, nof_regr_approx, save_fig = save_fig, show_fig = show_goal_plot)    
             
        ## save regression model
        with open(regr_name_full_, 'wb') as f:
            pickle.dump(regr_dict, f)
        
    except FileNotFoundError as e:
        print("File {} not found".format(e.filename))
        sys.exit() 
             

if __name__ == '__main__':
    main(sys.argv)
