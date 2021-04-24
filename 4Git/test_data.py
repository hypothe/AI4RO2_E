#!/usr/bin/env python3

import build
import run
import parse
import data_util

import numpy as np
import random
import itertools
import pickle

from sklearn.decomposition import PCA
import csv
import os, getopt, sys
import copy

max_drinks_ = 4 # 4
num_tables_ = 4
tot_drinks = 6 # 8
rounds_ = 0
waiter_number_ = 2 # 2
#g_values = [1, 5]
#h_values = [1, 5]
ratio_min = 1 #1.0
ratio_max = 20  #15
ratio_num = 7   #5
#ratios_ = np.geomspace(ratio_min, ratio_max, num = ratio_num).tolist()
ratios_ = np.linspace(ratio_min, ratio_max, num = ratio_num).tolist()
## g_values = [1, 3, 7, 10]
## h_values = [1, 3, 7, 10]
run_time_ = 300 #120

engine_path_ = run.engine_path
domain_name_full_ = data_util.domain_name_full_
problem_name_full_ = data_util.problem_name_full_
output_name_full_ = data_util.output_name_full_
csv_name_full_ = data_util.csv_name_full_ 
exp_name_full_ = data_util.exp_name_full_
writer_ = None

explored_cases = list()
all_cases = list()
results_ = list()

n_comb = [list() for ii in range(0, tot_drinks+1)]
for ii in range(0, tot_drinks+1):
    n_comb[ii] = [0 for jj in range(0, ii+1)]

def rec_gen(table, last_table, drink4table, hot4table, placed_drinks):
    global explored_cases
    if table < last_table and placed_drinks <= tot_drinks:
    
        for drink in range(0,min(max_drinks_+1, tot_drinks - placed_drinks+1)):
            drink4table[table] = drink
            
            for hot in range(0, drink+1):
                hot4table[table] = hot
                
                rec_gen(table+1, last_table, drink4table, hot4table, placed_drinks + drink)
            
                
    elif placed_drinks > 0:
        global all_cases, n_comb
        ordered_drinks = sum(drink4table)
        ordered_hot = sum(hot4table)
        
        for n_waiters in range(1, min(waiter_number_, int(8/ordered_drinks))+1):
        ## a sort of heuristic... didn't seem to work with more than 4 drinks for 2 waiters
            all_cases.append(copy.deepcopy((n_waiters, drink4table, hot4table)))
            n_comb[ordered_drinks][ordered_hot] += 1
 
def set_test(n_of_tests, run_time=None):
    global all_cases, explored_cases#, rounds_
    
    not_explored_cases = [case for case in all_cases if case not in explored_cases]
    ### for each case, its weight is inverselly proportional to the number of cases
    ### with the same tot drink and tot hot drinks
    
    weights = [1/n_comb[sum(case[1])][sum(case[2])] for case in not_explored_cases]
    
    cases_to_explore = random.choices(not_explored_cases, weights = weights, k = min(n_of_tests, len(not_explored_cases)))
    
    rr = 1
    tot_rounds = len(cases_to_explore)
    for config in cases_to_explore:
        print("Test #{} out of {}".format(rr, tot_rounds))
        test(config[0], config[1], config[2], run_time)
        explored_cases.append(copy.deepcopy(config))
        rr += 1
            
def test(n_waiters, drink4table, hot4table, run_time=None):
    global output_name_full, domain_name_full_, problem_name_full_
    global ratios_
    
    ## BUILD the problem file
    build.edit(n_waiters, drink4table, hot4table, problem_name_full_)
        
    ## RUN the problem file for all couples of h, g
    with open(output_name_full_, "w") as run_output_file:
        #for g_value in g_values:
        print("n_waiters: {}\ndrink4table: {}\nhot4table: {}".format(n_waiters, drink4table, hot4table)) 
        for gg in ratios_:
            if gg < 1.0:
                h_value = data_util.round_dec(1.0/gg, 3)
                g_value = 1.0
            else:
                h_value = 1.0
                g_value = data_util.round_dec(gg, 3)   
            res = run.run(domain_name_full_, problem_name_full_, False, g_value, h_value, run_output_file, run_time)
            if res:
                print("Succesful run")
            else:
                print("Unsuccesful run")
        
    ## PARSE the obtained output and save it
    with open(output_name_full_, "r") as run_output_file:    
        str_out = run_output_file.read()
         
        hg_val = parse.parse(str_out)
        ## SAVE the results in a csv
        save_results(n_waiters, hg_val, drink4table, hot4table)
        
#def perm_test(perm_order4table):
    ## conversion to set to remove duplicates
#    for order in set(tuple(tt) for tt in perm_order4table):
        #print(order)
#        test(order, [0,0,0,0])

            
def save_results(n_waiters, hg_val, drink4table, hot4table):
    global results_
    row = {}
    row['waiter'] = n_waiters 
    row['tot'], row['avg_x'], row['avg_y'], row['eig_1'], row['eig_2'] = [data_util.round_dec(val, 3) for val in data_util.avg_drink_pos(drink4table)]
    row['hot_tot'], row['hot_avg_x'], row['hot_avg_y'], row['hot_eig_1'], row['hot_eig_2'] = [data_util.round_dec(val, 3) for val in data_util.avg_drink_pos(hot4table)]
    #print("HG_VAL: {}".format(hg_val))
    for hg_key in hg_val:
        row['hw'] = hg_key[0]
        row['gw'] = hg_key[1]
        row['hg_ratio'] = hg_key[0]/hg_key[1]
        for par_key, v in hg_val[hg_key].items():
            # row[par_key] = v
            row[par_key] = data_util.round_dec(v, 3)
            
        
        results_.append(copy.deepcopy(row))
        ##print("RESULTS: {}".format(results_))
        ## input()    

               
def main(argv):

    global rounds_, csv_name_full, explored_cases, exp_name_full_, results_
    global problem_name_full_, domain_name_full_, output_name_full_, csv_name_full_

    drink4table = [0 for ii in range(0, num_tables_)]
    hot4table = [0 for ii in range(0, num_tables_)]
    table = 0
    last_table = num_tables_
    n_of_tests = 1
    run_time = run_time_
    
    usage = ("usage: pyhton3 " + argv[0] + "\n" +
             "(default values will be used in case options are not provided)\n" +
             "\t-n, --test-number <arg>\t\tnumber of tests to be carried out\n" +
             "\t-t, --time <arg>\ttimeout for each run instance (seconds)\n" +
             "\t-h, --help\t\tdisplay this help\n"
            )
    try:
        opts, args = getopt.getopt(argv[1:], "hn:", ["help","test-number="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        elif opt in ("-n", "--test-number"):
            n_of_tests = int(arg)
        elif opt in ("-t", "--time"):
            run_time = int(arg)
    
    
    identif = (max_drinks_, tot_drinks, run_time)
    
    #drink4table = [0, 1, 2, 1]
    #identif = ("permTest_", drink4table)
    
    problem_name_full_ = data_util.uniq_str(problem_name_full_, identif)
    output_name_full_ = data_util.uniq_str(output_name_full_, identif)
    csv_name_full_ = data_util.uniq_str(csv_name_full_, [run_time])
    exp_name_full_ = data_util.uniq_str(exp_name_full_, [run_time])
    
    ## load already explored drinks configurations
    try:
        with open(exp_name_full_, 'rb') as f:
            explored_cases = pickle.load(f)
    except FileNotFoundError:
        pass #in this case do nothing, explored_cases is already an empty list
        
    #print(explored_cases)
    ### PERFORM TEST RUN   
    rec_gen(table, last_table, drink4table, hot4table, 0)
    
    set_test(n_of_tests, run_time)
    
    try:
        with open(csv_name_full_, 'r', newline='') as csvfile:
            newfile = False
    except FileNotFoundError:
        newfile = True
        
    with open(csv_name_full_, 'a', newline='') as csvfile:
        fieldnames = ['waiter','tot','avg_x', 'avg_y', 'eig_1', 'eig_2',
                    'hot_tot', 'hot_avg_x', 'hot_avg_y', 'hot_eig_1', 'hot_eig_2',
                    'hw', 'gw','hg_ratio']
        for key in run.output_keywords:
            fieldnames.append(key)
    
        ## print(fieldnames)   
            
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
        if newfile:
            writer.writeheader()
            
        writer.writerows(results_)
        
    ## save newly explored drink configurations
    with open(exp_name_full_, 'wb') as f:
        pickle.dump(explored_cases, f)
        
    #print("ROUNDS: {}".format(rounds_))

if __name__ == '__main__':
    main(sys.argv)
