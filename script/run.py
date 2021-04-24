#!/usr/bin/env python3

import sys, getopt
import signal
import os
import re
import subprocess
import data_util
import pickle

Pddl_problem_ = "../domains/dom_APE/AAA.pddl"    	# (str) Problem name, extension needed
regr_name_full_ = data_util.regr_name_full_

run_wd = "../domains/dom_APE"				# (str) Working directory
out_wd = "../output"

engine_path = data_util.engine_path


Plan_Engine = 'enhsp'      				# (str) Define the planning engine to be use, choose between 'ff' or 'enhsp'
Pddl_domain_ = data_util.domain_name_full_    		# (str) Name of pddl domain file
Optimizer = False        				# (Bool) Set to active for optimization process
delta = 0.5
#g_values_ = [1, 2, 7, 10]    				# list of (int) g values to be run (active only if Optimizer == True)
#h_values_ = [1, 2, 7, 10]    				# list of (int) h values to be run (active only if Optimizer == True)

max_run_time = 120					# (int) maximum running time in seconds before stopping the run of the planning engine
output_keywords = ('Duration', 'Planning Time', 'Heuristic Time',
                    'Search Time', 'Expanded Nodes', 'States Evaluated')# list of (str): keywords for relevant outputs
                       
cwd = os.getcwd()

def run(domain_full, problem_full, Optimizer, g_val, h_val, run_output_file, run_time=None, show_output=False):	
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
            #extract output and error and put them in formatted form
            
        except (subprocess.TimeoutExpired):
            ###
            group_pid = os.getpgid(result.pid)
            os.killpg(group_pid, signal.SIGINT)
            ###
            #run_output_file.write("SUCCESS: " + str(flag) + "\n")
            fail_str = 'Solution not found for ' + problem_full + 'in  ' + str(run_time) + ' seconds'
            print(fail_str)
            
        except (subprocess.CalledProcessError):
            #run_output_file.write("SUCCESS: " + str(flag) + "\n")
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

    #print(regr_dict)
    #input()

    best_out = float('inf')
    ## Parse problem file
    n_waiters, drink4table, hot4table = parse.parse_problem(problem_filename)
    print(drink4table)
    
    tot, avg_x, avg_y, _, _ = data_util.avg_drink_pos(drink4table)
    hot_tot, hot_avg_x, hot_avg_y, _, _ = data_util.avg_drink_pos(hot4table)
    
    params = [n_waiters, tot, avg_x, avg_y, hot_tot, hot_avg_x, hot_avg_y]
    ## Apply linear regression coefficien to estimate the Y function for all (h,g) values
    
    ## load already explored drinks configurations
    
      
    exp_out = list()
    for hg_key, regr_list in regr_dict.items():
        for regr in regr_list:
            exp_out.append(sum([a_i*par_i for par_i, a_i in zip(params, regr.coef_)]) + regr.intercept_)
            
        Q_fact = sum(exp_out)/len(exp_out)
        print("[H: {:6}\tG: {:6}]\t->Q: {}".format(hg_key[0], hg_key[1], Q_fact))   
        
        if Q_fact < best_out:
            best_out = Q_fact
            h_val = hg_key[0]
            g_val = hg_key[1]
        
    print("Chosen [H: {}\tG: {}]".format(h_val, g_val))
    return [h_val], [g_val]

def main(argv):

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
    run_time = None #max_run_time ## None won't trigger a timeout
    #g_values = g_values_
    #h_values = h_values_
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
      
    #if not usr_wd:
    #    usr_wd = run_wd
    
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
                
        except FileNotFoundError:
            #pass #in this case do nothing, explored_cases is already an empty list
            print("No regression model found at {}, default hw and gw will be used".format(regr_name_full))
            print("To generate it run first\n" +
                "\tpython3 correlation.py -c <csv_filename>\n")
        
            h_values = [1.0]
            g_values = [1.0]         
        
    print(output_string)
    print("TRIM")
    with open(cwd + "/" + out_wd + "/"+ output_string, "w") as run_output_file:
        for g_value in g_values:
            for h_value in h_values:
                if h_value == g_value != 1:
                    continue
                run_script = run(domain_string,  problem_string, 
                                Optimizer, g_value, h_value,
                                run_output_file, run_time=run_time, show_output = show_output)
                res_run_str = problem_trim_name + " with hw = " + str(h_value) + " gw = " + str(g_value)
                if run_script:
                    print("Succesful run " + res_run_str)
                else:
                    print("Unsuccesful run " + res_run_str)
          

if __name__ == '__main__':
    main(sys.argv)
