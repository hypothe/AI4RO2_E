#!/usr/bin/env python3

import sys, getopt

import os
import re
import subprocess

Pddl_problem_ = "../domains/dom_APE/Custom.pddl"    # (str) Problem name, extension needed

run_wd = "../domains/dom_APE"			# (str) Working directory
out_wd = "../output"

engine_path = "/root/ENHSP-Public/enhsp"
Plan_Engine = 'enhsp'      			# (str) Define the planning engine to be use, choose between 'ff' or 'enhsp'
Pddl_domain_ = '../domains/dom_APE/numeric_domain_APE_full.pddl'    # (str) Name of pddl domain file
Optimizer = False        			# (Bool) Set to active for optimization process
delta = 0.5
g_values_ = [1, 2, 7, 10]    			# list of (int) g values to be run (active only if Optimizer == True)
h_values_ = [1, 2, 7, 10]    			# list of (int) h values to be run (active only if Optimizer == True)

max_run_time = 120			# (int) maximum running time in seconds before stopping the run of the planning engine
output_keywords = ('Duration', 'Planning Time', 'Heuristic Time',
                    'Search Time', 'Expanded Nodes', 'States Evaluated')# list of (str): keywords for relevant outputs
                       
cwd = os.getcwd()

def run(domain_full, problem_full, Optimizer, g_val, h_val, run_output_file, run_time):	

    # try torun the planning engine
    flag = 0
    gh_str = "H_VALUE: " + str(h_val) + "\nG_VALUE: " + str(g_val) + "\n"
    run_output_file.write(gh_str)
    
    try:
        print("Running " + problem_full + " gw: " +str(g_val) + " hw: " + str(h_val))
        result = subprocess.run([engine_path, "-o", domain_full, "-f", problem_full,
                                "-hw", str(h_val), "-gw", str(g_val),
                                "-delta_val", str(delta), "-delta_exec", str(delta)
                                ],
                                check=True, timeout=max_run_time, capture_output=True)
        #extract output and error and put them in formatted form
        
    except (subprocess.TimeoutExpired):
        run_output_file.write("SUCCESS: " + str(flag) + "\n")
        fail_str = 'Solution not found for ' + problem_full + 'in  ' + str(run_time) + ' seconds'
        print(fail_str)
        
    except (subprocess.CalledProcessError):
        run_output_file.write("SUCCESS: " + str(flag) + "\n")
        fail_str = 'Error found during the solution of ' + problem_full
        print(fail_str)
        
    else:
        flag = 1
        res = str(result.stdout)      
        frm_result = res.replace('\\n','\n')
        frm_result = trim_output(frm_result)
        
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

def main(argv):

    usage = ("usage: pyhton3 " + argv[0] + "\n" +
             "(default values will be used in case options are not provided)\n" +
             "\t-f, --problem <arg>\tPDDL problem file\n" +
             "\t-n, --output-path <arg>\tpath and name of the output file\n" +
             "\t-o, --domain <arg>\tPDDL domain file\n" +
             "\t-p, --path <arg>\tpath to PDDL files\n" +
             "\t-t, --time <arg>\tmaximum run time of each instance, in seconds\n" +
             "\t--gw <arg>\t\tthe list of gw values as [gw1,gw2,gw3,...] (list<float>)\n" +
             "\t--hw <arg>\t\tthe list of hw values as [hw1,hw2,hw3,...] (list<float>)\n" +
             "\t-h, --help\t\tdisplay this help\n"
            )
    usr_wd = ""
    Pddl_domain = Pddl_domain_
    Pddl_problem = Pddl_problem_
    output_string = ""
    run_time = max_run_time
    g_values = g_values_
    h_values = h_values_
    
    try:
        opts, args = getopt.getopt(argv[1:], "hf:o:p:n:t:",
                        ["help", "problem=", "domain=", "path=", "output-path=", "time=",
                        "gw=", "hw="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)
        
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
        elif opt in ("--gw") and arg[0] == '[' and arg[-1] == ']':
            gw = re.findall("\d\.?\d*", arg)
            g_values = list()
            try:
                for gg in gw:
                    g_values.append(float(gg))
            except ValueError:
                print("g values should be float")
                sys.exit()
        elif opt in ("--hw") and arg[0] == '[' and arg[-1] == ']':
            hw = re.findall("\d", arg)
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
        
    with open(cwd + "/" + out_wd + "/"+ output_string, "w") as run_output_file:
        for g_value in g_values:
            for h_value in h_values:
                if h_value == g_value != 1:
                    continue
                run_script = run(domain_string,  problem_string, 
                                Optimizer, g_value, h_value,
                                run_output_file, run_time)
                res_run_str = problem_trim_name + " with hw = " + str(h_value) + " gw = " + str(g_value)
                if run_script:
                    print("Succesful run " + res_run_str)
                else:
                    print("Unsuccesful run " + res_run_str)
          

if __name__ == '__main__':
    main(sys.argv)
