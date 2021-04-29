import numpy as np

engine_path = "/root/ENHSP-Public/enhsp"

domains_wd = "../domains/dom_APE"
out_wd = "../output"
graphs_wd = "../graphs"
template_wd = "templates"

domain_name_full_ = "../domains/dom_APE/numeric_domain_APE_full.pddl"
problem_name_full_ = "../domains/dom_APE/problem_temp.pddl"
output_name_full_ = "../output/temp_output.txt"

csv_name_full_ = "../lib/hg_val_20.csv" ## the data gathered using enhsp-20
exp_name_full_ = "../lib/drinks_explored_20.pkl" ## the data gathered using enhsp-20
regr_name_full_ = "../lib/regr_model.pkl"

pars = ('waiter','tot', 'avg_x', 'avg_y', "eig_1", "eig_2", 'hot_tot', 'hot_avg_x', 'hot_avg_y', "hot_eig_1", "hot_eig_2") # input features
output_keywords = ('Duration', 'Planning Time', 'Heuristic Time',
                    'Search Time', 'Expanded Nodes', 'States Evaluated')	# list of (str): keywords for relevant outputs
duration_alias = "Elapsed Time" # the parameter 'Duration' name changes with the enshp version

hw_flag = "-wh"
gw_flag = "-wg"
delta_val_flag = "-dv"
delta_exec_flag = "-de"
delta_val = 0.5

regr_goals_ = ('dur', 'search')
### Coeffs found by trial and error
Q_weights_ = {'dur':5.0, 'search':1.0} #for log scale

def avg_drink_pos(stuff4table):
    """
    Return the avg position of (hot) drinks
    distributed over the four tables.
    
    The four tables are imagined to be positoned
    as:
    table1(-1,1)   table2(1,1)
    table3(-1,-1)  table4(1,-1)
    
    Args:
        stuff4table (list(int)):
                            (hot) drink per table
                            
    Returns:
        tot (int):          total number of drinks
        avg_x (float):      average x position
        avg_y (float):      average y position
        lambda_ (list(float()):
                            eigenvalues of the
                            covariance matrix
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
    for i in range(0, len(x_sign)):
        if stuff4table[i] != 0: 
            for k in range(0, stuff4table[i]):
                x_d.append(x_sign[i])
                y_d.append(y_sign[i])

    cov = np.cov(x_d, y_d)
    lambda_sq_, v = np.linalg.eig(cov)
    lambda_ = np.sqrt(lambda_sq_)

    avg_x = np.mean(x_d)
    avg_y = np.mean(y_d)
    ## xi and yi will yield always 1, since they're either 1 or -1 squared
    std_x = np.std(x_d)
    std_y = np.std(y_d)
    
    return (tot, avg_x, avg_y, lambda_[0], lambda_[1])
         
def round_dec(val, dec):
    """
    Round decimal numbers to given precision
    
    Args:
        val (float):    original value
        dec (int):      number of positions
                        after the comma
    """
    
    res = val
    try:
         res = round(val * 10**dec)/(10**dec)
    except ValueError:
        pass
    return res
    
def uniq_str(file_name, prop):
    """
    Add a unique identifier to a name
    
    Args:
        file_name (str):    file name to modify
        prop (str):         list of suffixes to add
        
    Returns:
        ss (str):           complete filename
    """
    
    l = file_name.rfind(".")
    ss = file_name[0:l] + '_'
    for ii in prop:
        try:
            for jj in ii: # if it's iterable
                ss = ss + str(jj)
        except  TypeError:
            ss = ss + str(ii)
            
    ss = ss + file_name[l:]
    return ss
 
 
