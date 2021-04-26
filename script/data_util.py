import numpy as np

#engine_path = "/root/ENHSP-Public/enhsp"
#engine_path = "/root/AI4RO_II/ENHSP-public/enhsp"
engine_path = "/root/ENHSP-20/enhsp"

graphs_wd = "../graphs"

domain_name_full_ = "../domains/dom_APE/numeric_domain_APE_full.pddl"
problem_name_full_ = "../domains/dom_APE/problem_temp.pddl"
output_name_full_ = "../output/temp_output.txt"

csv_name_full_ = "../lib/hg_val_20.csv" ## the data gathered using enhsp-20
exp_name_full_ = "../lib/drinks_explored_20.pkl" ## the data gathered using enhsp-20

regr_name_full_ = "../lib/regr_model.pkl"

duration_alias = "Elapsed Time"
hw_flag = "-wh"
gw_flag = "-wg"
delta_val_flag = "-dv"
delta_exec_flag = "-de"

regr_goal1_ = 'dur'
regr_goal2_ = 'search'

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
    std_x = np.std(x_d)
    std_y = np.std(y_d)
    #std_x = sum([pow(i, 2) for i in stuff4table]) / pow(tot,2) - pow(avg_x, 2)
    #std_y = sum([pow(i, 2) for i in stuff4table]) / pow(tot,2) - pow(avg_y, 2)
    
    #print("FROM {}: TOT {} AVG_X {} AVG_Y {} eig_1 {} eig_2 {}".format(stuff4table, tot, avg_x, avg_y, lambda_[0], lambda_[1]))
    return (tot, avg_x, avg_y, lambda_[0], lambda_[1])
         
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
 
 
