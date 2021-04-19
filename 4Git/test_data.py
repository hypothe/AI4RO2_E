#!/usr/bin/env python3

import build
import run
import parse
from sklearn.decomposition import PCA
import numpy as np
import csv

max_drinks_ = 2 # 4
num_tables_ = 4
tot_drinks = 4 # 8
rounds_ = 0
waiter_number_ = 1 # 2
problem_name_full_ = "../domains/dom_APE/problem_temp.pddl"
g_values = [1, 5]
h_values = [1, 5]
## g_values = [1, 3, 7, 10]
## h_values = [1, 3, 7, 10]
engine_path_ = run.engine_path
domain_name_full_ = run.Pddl_domain_
output_name_full_ = "../output/temp_output.txt"
run_time = 60 # 300
csv_name_full_ = "../graphs/hg_val.csv"
writer_ = None

def rec(table, last_table, drink4table, hot4table, placed_drinks):
    if table < last_table and placed_drinks <= tot_drinks:
    
        for drink in range(0,min(max_drinks_+1, tot_drinks - placed_drinks+1)):
            drink4table[table] = drink
            
            for hot in range(0, drink+1):
                hot4table[table] = hot
                
                rec(table+1, last_table, drink4table, hot4table, placed_drinks + drink)
                
    elif placed_drinks > 0:
        global rounds_, output_name_full, domain_name_full_, problem_name_full_
        global g_values, h_values, run_time
        rounds_ = rounds_ + 1
        
        ## BUILD the problem file
        build.edit(waiter_number_, drink4table, hot4table, problem_name_full_)
        print("Problem {} with\n\td4t: {}\n\th4t: {}".format(rounds_, drink4table, hot4table))
        
        ## RUN the problem file for all couples of h, g
        with open(output_name_full_, "w") as run_output_file:
            for g_value in g_values:
                for h_value in h_values:
                    if h_value == g_value != 1:
                        continue
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
            ### notice the csv is opened in the main, so that won't be overwritten between problems
            print_to_csv(hg_val, drink4table, hot4table)
            
def print_to_csv(hg_val, drink4table, hot4table):
    global writer_
    writer = writer_
    row = {}
    row['tot'], row['avg_x'], row['avg_y'], row['std_x'], row['std_y'] = avg_drink_pos(drink4table)
    row['hot_tot'], row['hot_avg_x'], row['hot_avg_y'], row['hot_std_x'], row['hot_std_y'] = avg_drink_pos(hot4table)
    
    for hg_key in hg_val:
        row['hw'] = hg_key[0]
        row['gw'] = hg_key[1]
        for par_key, v in hg_val[hg_key].items():
            row[par_key] = v
        writer.writerow(row)

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
    print(stuff4table)
    print(x_sign)
    print(y_sign)
    for i in range(0, len(x_sign)):
        if stuff4table[i] != 0: 
            for k in range(0, stuff4table[i]):
                x_d.append(x_sign[i])
                y_d.append(y_sign[i])

    print(x_d)
    print(y_d)
    cov = np.cov(x_d, y_d)
    lambda_sq_, v = np.linalg.eig(cov)
    lambda_ = np.sqrt(lambda_sq_)
    print('lambda')
    print(lambda_)
    print('v')
    print(v)
    #avg_x = sum([i*j for i, j in zip(stuff4table, x_sign)])/tot
    #avg_y = sum([i*j for i, j in zip(stuff4table, y_sign)])/tot
    avg_x = np.mean(x_d)
    avg_y = np.mean(y_d)
    ## xi and yi will yield always 1, since they're either 1 or -1 squared
    std_x = sum([pow(i, 2) for i in stuff4table]) / pow(tot,2) - pow(avg_x, 2)
    std_y = sum([pow(i, 2) for i in stuff4table]) / pow(tot,2) - pow(avg_y, 2)
    
    print("FROM {}: TOT {} AVG_X {} AVG_Y {} STD_X {} STD_Y {}".format(stuff4table, tot, avg_x, avg_y, std_x, std_y))
    return ('%.3f'%(tot), '%.3f'%(avg_x), '%.3f'%(avg_y), '%.3f'%(std_x), '%.3f'%(std_y))
                
def main():

    global rounds_, csv_name_full, writer_
    #drink4table = [0 for ii in range(0, num_tables_)]
    #hot4table = [0 for ii in range(0, num_tables_)]
    drink4table = [0, 0, 0, 2]
    hot4table = [0,0,0,0]
    table = 0
    last_table = num_tables_
    
    with open(csv_name_full_, 'w', newline='') as csvfile:
        fieldnames = ['tot','avg_x', 'avg_y', 'std_x', 'std_y',
                    'hot_tot', 'hot_avg_x', 'hot_avg_y', 'hot_std_x', 'hot_std_y',
                    'hw', 'gw']
        for key in run.output_keywords:
            fieldnames.append(key)
    
        ## print(fieldnames)   
            
        writer_ = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel')
        writer_.writeheader()
        rec(table, last_table, drink4table, hot4table, 0)
        
    print(rounds_)

if __name__ == '__main__':
    main()
