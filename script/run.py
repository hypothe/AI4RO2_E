#!/usr/bin/env python3

import sys, getopt

import signal
import os
import re
import subprocess

import data_util
import pickle
import parse
import math
from correlation import delog_predict

Pddl_problem_ = "../domains/dom_APE/Custom.pddl"    # (str) Default problem name, extension needed
regr_name_full_ = data_util.regr_name_full_

run_wd = data_util.domains_wd			# (str) Working directory
out_wd = data_util.out_wd

engine_path = data_util.engine_path


Plan_Engine = 'enhsp'      			# (str) Define the planning engine to be use, choose between 'ff' or 'enhsp'
Pddl_domain_ = data_util.domain_name_full_    # (str) Name of pddl domain file
delta = data_util.delta_val

output_keywords = data_util.output_keywords # list of (str): keywords for relevant outputs
                       
cwd = os.getcwd()

def run(domain_full, problem_full, g_val, h_val, run_output_file, run_time=None, show_output=False):
    """
    Function that calls enhsp-20 to plan over a (domain,problem)
    
    Some parameters are passed to the run, in order to tweak
    its behaviour. The results obtained, in terms of the
    metrics presented in 'output_keywords', are saved in a
    text file.
    
    Args:
        domain_full (str):  path/to/domain_file
        problem_full (str): path/to/problem_file
        g_val (float):      weight of g() function in A*
        h_val (float):      weight of h() function in A*
        run_output_file (file):
                            open file to write trimmed
                            results on
        run_time (int):     timeout for the planner execution.
                            The planner will be stopped if no
                            sulution is found in time.
                            (default None -> no timeout)
        show_output (bool): whether to display the enhsp full
                            output on console or not at the
                            end of the run.
                            (default False)
                        
    Returns:
        flag (int):         codes the success of the run
    """

    hw_flag = data_util.hw_flag
    gw_flag = data_util.gw_flag
    delta_val_flag = data_util.delta_val_flag
    delta_exec_flag = data_util.delta_exec_flag
    frm_result = ""
    flag = 0
    gh_str = "H_VALUE: " + str(h_val) + "\nG_VALUE: " + str(g_val) + "\n"
    run_output_file.write(gh_str)
    
    print("Running " + problem_full + " gw: " +str(g_val) + " hw: " + str(h_val))
    with subprocess.Popen([engine_path, "-o", domain_full, "-f", problem_full,
                                hw_flag, str(h_val), gw_flag, str(g_val),
                                delta_val_flag, str(delta), delta_exec_flag, str(delta)
                            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, preexec_fn=os.setsid) as result:
        try:
            res, err = result.communicate(timeout=run_time)
            if result.returncode:
                raise subprocess.CalledProcessError(cmd=result.args, returncode=result.returncode)
            
        except (subprocess.TimeoutExpired):
            ### A group of processes is generated in order to kill the java subprocesses
            ### spawned in turn by enhsp (they'd remain zombies and eat computational resources
            ### otherwise in case of a run interrupted by timeout
            group_pid = os.getpgid(result.pid)
            os.killpg(group_pid, signal.SIGINT)
            ###
            fail_str = 'Solution not found for ' + problem_full + 'in  ' + str(run_time) + ' seconds'
            print(fail_str)
            
        except (subprocess.CalledProcessError):
            fail_str = 'Error found during the solution of ' + problem_full
            print(fail_str)
            print(err.replace('\\n', '\n'))
            
        else:
            flag = 1
            frm_result = res.replace('\\n','\n')
            frm_result = res.replace(data_util.duration_alias, 'Duration')
            frm_result = trim_output(frm_result)
            
    if show_output:
        print(res.replace('\\n','\n'))
                        
    run_output_file.write("SUCCESS: " + str(flag) + "\n")
    run_output_file.write(frm_result)
    
    run_output_file.write("\n\n### ------------------ ###\n\n")
    return flag
    
def trim_output(tot_out):
    """
    This functions keeps only the metrics we are interested in
    from the enhsp output log
    
    Args:
        tot_out (str):  enhsp whole log of a succesful run
    
    Returns:
        trim_out (str): trimmed log presenting only the metrics
                        of interested (those in 'output_keywords')
    """
    
    trim_out = ""
    
    for k in output_keywords:
        start = tot_out.rfind(k)
        # rfind simply retrieves the last time the string appeared
        # necessary since States Evaluated appears more than once
        # in different contextes
        end = tot_out.find("\n", start, -1) + 1
        trim_out = trim_out + tot_out[start:end]
        
    return trim_out
    
def get_best_hg(regr_dict, problem_filename):
    """
    This functions retrieves the best wg and wh based on
    a problem configuration
    
    Information such as number of waiters and drink
    distribution were used to train a sequence of
    LinearRegression models on two solution parameters,
    'Duration' and 'Search Time', in order to predict
    the quality of the solution expected for each of
    the (hw,gw) couples the training was performed on.
    The (hw,gw) couple yielding the best expected
    performance (the lower weighted sum of the two predictd
    metrics) is selected.
    *   Notice that the predicted values are actually the
        log() of those two solution parameters.
    
    Args:
        regr_dict (dict):
                        collection of all LinearRegression
                        models trained, indexed as
                        (hw,gw)x(goal_metric)
        problem_filename (str):
                        path/to/problem_file to run
    
    Returns:
        [hw] (list(float)):
                        optimal predicted h weight (returned as
                        a singleton list for compatibility)
        [gw] (list(float)):
                        optimal predicted g weight (returned as
                        a singleton list for compatibility)
    """
    
    best_out = float('inf')
    ## Parse problem file
    n_waiters, drink4table, hot4table = parse.parse_problem(problem_filename)
    
    tot, avg_x, avg_y, _, _ = data_util.avg_drink_pos(drink4table)
    hot_tot, hot_avg_x, hot_avg_y, _, _ = data_util.avg_drink_pos(hot4table)
    
    params = [n_waiters, tot, avg_x, avg_y, hot_tot, hot_avg_x, hot_avg_y]
    ## Apply linear regression coefficien to estimate the Y function for all (h,g) values
    
    ## load already explored drinks configurations
    goals = data_util.regr_goals_
    Q_weights = data_util.Q_weights_
      
    pred_goals = {}
    
    for hg_key, regr_list in regr_dict.items():
        exp_out = list()
        for goal, regr in regr_list.items():
            prediction = regr.predict([params])
            pred_goals[goal] = round(math.exp(prediction))
            exp_out.append(Q_weights[goal]*prediction)
            ## Log scale chosen
            # exp_out.append(Q_weights[goal]*pred_goals[goal])
            
        Q_fact = sum(exp_out)/sum(Q_weights.values())
        print("[H: {:6}\tG: {:6}]\t->Q: {}\t{}".format(hg_key[0], hg_key[1], Q_fact, pred_goals))
        
        if Q_fact < best_out:
            best_out = Q_fact
            h_val = hg_key[0]
            g_val = hg_key[1]
        
    print("Chosen [H: {}\tG: {}]".format(h_val, g_val))
    return [h_val], [g_val]

def main(argv):
    """
    Script to run a (domain, problem) file using enhsp solver.
    
    It's possible to run them using the couple of (hw,gw)
    autonomously predicted to have the better results
    (among a finite list of such couples) thanks to a small
    machine learning model.
    """
    
    usage = ("usage: pyhton3 " + argv[0] + "\n" +
             "(default values will be used in case options are not provided)\n" +
             "\t-f, --problem <arg>\tPDDL problem file\n" +
             "\t-n, --output-path <arg>\tpath and name of the output file\n" +
             "\t-o, --domain <arg>\tPDDL domain file\n" +
             "\t-p, --path <arg>\tpath to directory of PDDL files\n" +
             "\t-t, --time <arg>\tmaximum run time of each instance, in seconds\n" +
             "\t-s, --silence\don't print output of each run on the terminal\n" +
             "\t-M, --machine-learning \t\tautomatically find close-to-optimal [hw,gw]\n"+
             "\t\t\t\t\t values with trained Linear Regression model\n" +
             "\t--gw <arg>\t\tthe list of gw values as [gw1,gw2,gw3,...] (list<float>)\n" +
             "\t--hw <arg>\t\tthe list of hw values as [hw1,hw2,hw3,...] (list<float>)\n" +
             "\t-h, --help\t\tdisplay this help\n"
            )
    usr_wd = ""
    Pddl_domain = Pddl_domain_
    Pddl_problem = Pddl_problem_
    output_string = ""
    run_time = None ## None won't trigger a timeout
    ML = False
    show_output = True
    g_values = [1.0]
    h_values = [1.0]
    
    try:
        opts, args = getopt.getopt(argv[1:], "hf:o:p:n:t:Ms",
                        ["help", "problem=", "domain=", "path=", "output-path=", "time=",
                        "gw=", "hw=", "machine-learning", "silence"])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)
    
    
    if ("-M", '') in opts or ("--machine-learning", '') in opts:
        ML = True
                 
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        elif opt in ("-f", "--problem"):
            Pddl_problem = arg
        elif opt in ("-o", "--domain"):
            Pddl_domain = arg
        elif opt in ("-p", "--path"):
            usr_wd = arg+"/"
        elif opt in ("-n", "--output-path"):
            output_string = arg
        elif opt in ("-t", "--time"):
            run_time = int(arg)
        elif opt in ("-s", "--silence"):
            show_output = False
        elif not ML and opt in ("--gw") and arg[0] == '[' and arg[-1] == ']':
            gw = re.findall("\d+\.?\d*", arg)
            g_values = list()
            try:
                for gg in gw:
                    g_values.append(float(gg))
            except ValueError:
                print("g values should be float")
                sys.exit()
        elif not ML and opt in ("--hw") and arg[0] == '[' and arg[-1] == ']':
            hw = re.findall("\d+\.?\d*", arg)
            h_values = list()
            try:
                for hh in hw:
                    h_values.append(float(hh))
            except ValueError:
                print("h values should be float")
                sys.exit()
       
    domain_string = usr_wd  + Pddl_domain
    problem_string = usr_wd + Pddl_problem
    
    problem_trim_name = Pddl_problem[Pddl_problem.rfind("/")+1:Pddl_problem.rfind(".pddl")]
    
    if not output_string:
        output_string = "output_" + problem_trim_name + ".txt"
        
               
    if ML:
            ## load saved Linear Regression
        try:
            with open(regr_name_full_, 'rb') as f:
                regr_dict = pickle.load(f)
                h_values, g_values = get_best_hg(regr_dict, problem_string)
                input("Press Enter to launch the solver with those values...")
                
        except FileNotFoundError:
            #pass #in this case do nothing, explored_cases is already an empty list
            print("No regression model found at {}, default hw and gw will be used".format(regr_name_full))
            print("To generate it run first\n" +
                "\tpython3 correlation.py -c <csv_filename>\n")
        
            h_values = [1.0]
            g_values = [1.0]         
        
    with open(cwd + "/" + out_wd + "/"+ output_string, "w") as run_output_file:
        for g_value in g_values:
            for h_value in h_values:
                if h_value == g_value != 1:
                    continue
                run_script = run(domain_string,  problem_string, g_value, h_value,
                                run_output_file, run_time=run_time, show_output = show_output)
                res_run_str = problem_trim_name + " with hw = " + str(h_value) + " gw = " + str(g_value)
                if run_script:
                    print("Succesful run " + res_run_str)
                else:
                    print("Unsuccesful run " + res_run_str)
          

if __name__ == '__main__':
    main(sys.argv)
