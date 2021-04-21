#!/usr/bin/env python3

import build
import run
import parse
import numpy as np
import random
import itertools
import pickle

from sklearn.decomposition import PCA
import csv
import os
import copy

max_drinks_ = 4 # 4
num_tables_ = 4
tot_drinks = 6 # 8
rounds_ = 0
waiter_number_ = 1 # 2
#g_values = [1, 5]
#h_values = [1, 5]
ratio_min = 1 #1.0
ratio_max = 15
ratio_num = 5
ratios_ = np.geomspace(ratio_min, ratio_max, num = ratio_num).tolist()
## g_values = [1, 3, 7, 10]
## h_values = [1, 3, 7, 10]
run_time = 120 # 300

engine_path_ = run.engine_path
domain_name_full_ = run.Pddl_domain_
problem_name_full_ = "../domains/dom_APE/problem_temp.pddl"
output_name_full_ = "../output/temp_output.txt"
csv_name_full_ = "../graphs/hg_val.csv"
exp_name_full_ = "../output/drinks_explored.pkl"
writer_ = None

explored_cases = list()
all_cases = list()
results_ = list()

def rec_gen(table, last_table, drink4table, hot4table, placed_drinks):
    global explored_cases
    if table < last_table and placed_drinks <= tot_drinks:
    
        for drink in range(0,min(max_drinks_+1, tot_drinks - placed_drinks+1)):
            drink4table[table] = drink
            
            for hot in range(0, drink+1):
                hot4table[table] = hot
                
                rec_gen(table+1, last_table, drink4table, hot4table, placed_drinks + drink)
            
                
    elif placed_drinks > 0:  ## and random.random() < 0.001:
        global all_cases
        all_cases.append(copy.deepcopy((drink4table, hot4table)))

 
def set_test(n_of_tests):
    global all_cases, explored_cases#, rounds_
    
    not_explored_cases = [case for case in all_cases if case not in explored_cases]
    cases_to_explore = random.choices(not_explored_cases, k = min(n_of_tests, len(not_explored_cases)))
    
    for config in cases_to_explore:
        test(config[0], config[1])
        explored_cases.append(copy.deepcopy(config))
            
def test(drink4table, hot4table):
    global output_name_full, domain_name_full_, problem_name_full_
    global ratios_, run_time
    
    ## BUILD the problem file
    build.edit(waiter_number_, drink4table, hot4table, problem_name_full_)
        
    ## RUN the problem file for all couples of h, g
    with open(output_name_full_, "w") as run_output_file:
        #for g_value in g_values:
        for gg in ratios_:
            if gg < 1.0:
                h_value = round_dec(1.0/gg, 3)
                g_value = 1.0
            else:
                h_value = 1.0
                g_value = round_dec(gg, 3)
                
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
        save_results(hg_val, drink4table, hot4table)
        
def perm_test(perm_order4table):
    ## conversion to set to remove duplicates
    for order in set(tuple(tt) for tt in perm_order4table):
        #print(order)
        test(order, [0,0,0,0])

            
def save_results(hg_val, drink4table, hot4table):
    global results_
    row = {}
    row['tot'], row['avg_x'], row['avg_y'], row['eig_1'], row['eig_2'] = [round_dec(val, 3) for val in avg_drink_pos(drink4table)]
    row['hot_tot'], row['hot_avg_x'], row['hot_avg_y'], row['hot_eig_1'], row['hot_eig_2'] = [round_dec(val, 3) for val in avg_drink_pos(hot4table)]
    #print("HG_VAL: {}".format(hg_val))
    for hg_key in hg_val:
        row['hw'] = hg_key[0]
        row['gw'] = hg_key[1]
        row['hg_ratio'] = hg_key[0]/hg_key[1]
        for par_key, v in hg_val[hg_key].items():
            # row[par_key] = v
            row[par_key] = round_dec(v, 3)
            
        
        results_.append(copy.deepcopy(row))
        ##print("RESULTS: {}".format(results_))
        ## input()    
        
def round_dec(val, dec):
    res = val
    try:
         res = round(val * 10**dec)/(10**dec)
    except ValueError:
        pass
    return res
    
def uniq_str(file_name, prop):

    l = file_name.rfind(".")
    ss = file_name[0:l] + '_'
    for ii in prop:
        try:
            for jj in ii: # if it's iterable
                ss = ss + str(jj)
        except  TypeError:
            ss = ss + str(ii)
            
    ss = ss + file_name[l:]
    # print(ss)
    return ss

def avg_drink_pos(stuff4table):
    """
    table1(-1,1)   table2(1,1)
    table3(-1,-1)  table4(1,-1)
    """
    x_sign = (-1, 1, -1, 1)
    y_sign = (1, 1, -1, -1)
    
    tot = sum(stuff4table)

    if tot == 0:
        return 0, 0, 0, 0, 0
    elif tot == 1:
        return 1, x_sign[np.where(np.array(stuff4table) != 0)[0][0]], y_sign[np.where(np.array(stuff4table) != 0)[0][0]], 0 , 0

    x_d = []
    y_d = []
    #print(stuff4table)
    #print(x_sign)
    #print(y_sign)
    for i in range(0, len(x_sign)):
        if stuff4table[i] != 0: 
            for k in range(0, stuff4table[i]):
                x_d.append(x_sign[i])
                y_d.append(y_sign[i])

    #print(x_d)
    #print(y_d)
    cov = np.cov(x_d, y_d)
    lambda_sq_, v = np.linalg.eig(cov)
    lambda_ = np.sqrt(lambda_sq_)

    avg_x = np.mean(x_d)
    avg_y = np.mean(y_d)
    ## xi and yi will yield always 1, since they're either 1 or -1 squared
    std_x = np.sd(x_d)
    std_y = np.sd(y_d)
    #std_x = sum([pow(i, 2) for i in stuff4table]) / pow(tot,2) - pow(avg_x, 2)
    #std_y = sum([pow(i, 2) for i in stuff4table]) / pow(tot,2) - pow(avg_y, 2)
    
    #print("FROM {}: TOT {} AVG_X {} AVG_Y {} eig_1 {} eig_2 {}".format(stuff4table, tot, avg_x, avg_y, lambda_[0], lambda_[1]))
    return (tot, avg_x, avg_y, lambda_[0], lambda_[1])
                
def main():

    global rounds_, csv_name_full, explored_cases, exp_name_full_, results_
    global problem_name_full_, domain_name_full_, output_name_full_, csv_name_full_

    drink4table = [0 for ii in range(0, num_tables_)]
    hot4table = [0 for ii in range(0, num_tables_)]
    table = 0
    last_table = num_tables_
    
    
    identif = (max_drinks_, tot_drinks, waiter_number_, run_time)
    
    #drink4table = [0, 1, 2, 1]
    #identif = ("permTest_", drink4table)
    
    problem_name_full_ = uniq_str(problem_name_full_, identif)
    output_name_full_ = uniq_str(output_name_full_, identif)
    csv_name_full_ = uniq_str(csv_name_full_, identif)
    exp_name_full_ = uniq_str(exp_name_full_, identif)
    
    ## load already explored drinks configurations
    try:
        with open(exp_name_full_, 'rb') as f:
            explored_cases = pickle.load(f)
    except FileNotFoundError:
        pass #in this case do nothing, explored_cases is already an empty list
        
    print(explored_cases)
    ### PERFORM TEST RUN   
    rec_gen(table, last_table, drink4table, hot4table, 0)
    
    set_test(4)
    
    try:
        with open(csv_name_full_, 'r', newline='') as csvfile:
            newfile = False
    except FileNotFoundError:
        newfile = True
        
    with open(csv_name_full_, 'a', newline='') as csvfile:
        fieldnames = ['tot','avg_x', 'avg_y', 'eig_1', 'eig_2',
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
    main()
