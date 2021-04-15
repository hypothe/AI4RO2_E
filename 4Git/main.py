#!/usr/bin/env python3
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Import dependencies
import PySimpleGUI as sg 	# disabled for multiple run on docker
import os
import subprocess
#import plotly.express as px
#import pandas as pd


#Set global variables

GUI_Input = False               # (Bool) Activate the GUI for the setting of the problem conditions
RUN = True                      # (Bool) Active if you want to run the code after having generated it
PARSE = False			# (Bool) Active if you want to get the plot of the plan
problem_name = "Custom.pddl"    # (str) Problem name, extension needed
wd = "run"			# (str) Working directory

# Input variables if no gui active
waiter_number_global = 1            # (int) Number of waiters
drink4table_global = [0, 2, 0, 0]   # list of (int) Drinks ordered for each table
hot4table_global = [0, 0, 0, 0]     # list of (int) Hot drinks for table
table_number_global = 4             # number of tables present

# Input variables for running the planning engine automatically
#engine_path = "/root/AI4RO_II/ENHSP-public/enhsp"
engine_path = "/root/ENHSP-Public/enhsp"
Plan_Engine = 'enhsp'      			# (str) Define the planning engine to be use, choose between 'ff' or 'enhsp'
Pddl_domain = 'numeric_domain_APE_full.pddl'    # (str) Name of pddl domain file
Optimizer = False        			# (Bool) Set to active for optimization process
g_values = [1,2]    			# list of (int) g values to be run (active only if Optimizer == True)
h_values = [1,2]    			# list of (int) h values to be run (active only if Optimizer == True)
opt_alg = ['dff', 'fgf']    			# list of (str) optimization algorithm to be tested (active only if Optimizer == True)
max_run_time = 120			# (int) maximum running time in seconds before stopping the run of the planning engine
output_keywords = ('Duration', 'Planning Time', 'Heuristic Time',
                    'Search Time', 'Expanded Nodes', 'States Evaluated')# list of (str): keywords for relevant outputs
#Paramenters
cwd = os.getcwd()

def gui():

    #GUI theme
    sg.theme('Topanga')  # Add some color to the window

    # Table GUI
    images_col = [[sg.Image(cwd+"/GUI_image.png")]]
    layout_input = [
        [sg.Text('Restaurant status:')],
        [sg.Text('Active waiters', size=(15, 1)), sg.InputText('1')],
        [sg.Text('')],
        [sg.Text('Please enter the number of customers per table and the required hot drinks:')],
        [sg.Text('Table 1:', size=(15, 1)), sg.InputText('0'),sg.Text('Hot drinks:', size=(8, 1)), sg.InputText('0')],
        [sg.Text('Table 2:', size=(15, 1)), sg.InputText('0'),sg.Text('Hot drinks:', size=(8, 1)), sg.InputText('0')],
        [sg.Text('Table 3:', size=(15, 1)), sg.InputText('0'),sg.Text('Hot drinks:', size=(8, 1)), sg.InputText('0')],
        [sg.Text('Table 4:', size=(15, 1)), sg.InputText('0'),sg.Text('Hot drinks:', size=(8, 1)), sg.InputText('0')],
        [sg.Submit(), sg.Cancel()]
    ]

    # ----- Full layout -----
    layout = [[sg.Column(images_col, element_justification='c'), sg.VSeperator(),
               sg.Column(layout_input, element_justification='l')]]

    window = sg.Window('AI for Robotics II', layout)
    event, values = window.read()
    window.close()
    print(values)
    #Extract input from GUI
    waiters = int(values[2])
    drink4table = [int(values[3]), int(values[5]), int(values[7]), int(values[9])]
    hot4table = [min(int(values[3]), int(values[4])), min(int(values[5]), int(values[6])), 
                min(int(values[7]),int(values[8])), min(int(values[9]),int(values[10]))]

    return(waiters, drink4table, hot4table)


def headgoal_edit(wait_num, drink_num):
    """ This function reads the header and the goal templates and it fills it with the
        required information received from the GUI"""

    "Open the header and the goal txt file"
    header_name = "Domain_Header.txt"
    goal_name = "Domain_Goal.txt"
    header_file = open(cwd + "/" + header_name, "r")
    goal_file = open(cwd + "/" + goal_name, "r")
    header_txt = header_file.read()
    goal_txt = goal_file.read()

    "Look for placeholder 'drink'"

    "Number of drinks and waiters required"
    drinks = drink_num
    waiters = wait_num
    
    biscuits = drinks-sum(hot4table)

    # Creates the drink and waiter string
    drinks_head_string = ""
    drinks_goal_string = ""
    biscuits_head_string = ""
    biscuits_goal_string = ""
    wait_head_string = ""
    waiter_final_pos = ""

    for drink_id in range(1, drinks+1):
        drinks_head_string = drinks_head_string + "drink" + chr(64 + drink_id) + " "
        drinks_goal_string = drinks_goal_string + "(order-delivered drink" + chr(64 + drink_id) + ") "
        if not drink_id % 4:
            drinks_head_string = drinks_head_string + " - Drink\n\t\t"
            drinks_goal_string = drinks_goal_string + "\n\t\t"
    if drink_id % 4:
        drinks_head_string = drinks_head_string + " - Drink"
            
    for biscuit_id in range(1, biscuits+1):
        biscuits_head_string = biscuits_head_string + "biscuit" + chr(64 + biscuit_id) + " "
        biscuits_goal_string = biscuits_goal_string + "(order-delivered biscuit" + chr(64 + biscuit_id) + ") "
        if not biscuit_id % 4:
            biscuits_head_string = biscuits_head_string + " - Biscuit\n\t\t"
            biscuits_goal_string = biscuits_goal_string + "\n\t\t"
    if biscuit_id % 4:
        biscuits_head_string = biscuits_head_string + " - Biscuit"
    
    for wait_id in range(1, waiters+1):
        wait_head_string = wait_head_string + "w" + str(wait_id) + " "
        # waiter initial position
        if wait_id == 1:
            waiter_final_pos = waiter_final_pos + "(at-waiter w1 bar)\n\t\t"
        else:
            waiter_final_pos = waiter_final_pos + "(at-waiter w" + str(wait_id) + " table" + str(wait_id - 1) + ")\n\t\t"

    # Find the DRINK_PH sting in the templates and replace it with the generated string for the drinks and the waiters
    new_header_drinks = header_txt.replace(';DRINK_PH', drinks_head_string)
    new_header = new_header_drinks.replace(';WAIT_PH', wait_head_string)
    new_header = new_header.replace(';BISCUIT_PH', biscuits_head_string)
    
    new_goal = goal_txt.replace(';DRINK_PH', drinks_goal_string)
    new_goal = new_goal.replace(';WAIT_PH', waiter_final_pos)
    new_goal = new_goal.replace(';BISCUIT_PH', biscuits_goal_string)

    return(new_header, new_goal)

def init_edit(wait_num, d4t, h4t):
    """ This function reads the init templates and it fills it with the
        required information received from the GUI
        """

    "Open the header and the goal txt file"
    init_name = "Domain_Init.txt"
    init_file = open(cwd + "/" + init_name, "r")
    init_txt = init_file.read()

    "Number of drinks and waiters required"
    waiters = wait_num
    "Drinks for tables"
    drink_4_table = d4t
    hot_4_table = h4t

    # Creates the required new strings for the init block
        #waiter strings
    #waiter_time_init = ""
    waiter_free_init = ""
    hand_free_init = ""
    waiter_init_pos = ""
        #Drink strings
    drink_identity = ""
    #drink_delivered = ""
    #drink_notready = ""
    ordered_by = ""
    hot_drink_string = ""
        #Customers per table
    customers = ""
        # place initially free
    place_free_init = ""
        # tray initially not carried by any waiter
    tray_carried_init = ""
        # A biscuit for each cold drink
    drink4biscuit_init = ""
        # 
    biscuit_identity = ""
    ordered_biscuit = ""

    #Waiter predicates
    for wait_id in range(1, waiters+1):
        #waiter time
        #waiter_time_init = waiter_time_init + "(= (time-waiter w" + str(wait_id) + ") 0) \n"
        #waiter hand-free condition
        hand_free_init = hand_free_init + "(hand-free w" + str(wait_id) + ")\n\t\t"
        #waiter free condition
        waiter_free_init = waiter_free_init + "(free-waiter w" + str(wait_id) + ")\n\t\t"
        #tray not carried by waiter fluent
        tray_carried_init = tray_carried_init + "(= (fl-tray-carried w"+ str(wait_id) + ") 0)\n\t\t"
        
        #waiter initial position
        if wait_id == 1:
            waiter_init_pos = waiter_init_pos + "(at-waiter w1 bar)\n\t\t"
        else:
            waiter_init_pos = waiter_init_pos + "(at-waiter w" + str(wait_id) + " table" + str(wait_id-1) + ")\n\t\t"
    #Place-free predicates        
    for free_id in range(waiters, table_number_global+1):
        # free tables
        place_free_init = place_free_init + "(place-free table" + str(free_id) + ")\n\t\t"
    #Table predicates

        # initialize the drinks counter
        drink_id = 0
        biscuit_id  = 0
    for table_id in range(1, len(drink_4_table)+1):

        # Last delivered and empty time
        drinkspertable = drink_4_table[table_id-1]

        if drinkspertable != 0:
            #drink_delivered = (drink_delivered + "(= (fl-time-empty table" + str(table_id)+") -1) " +
            #    "(= (fl-last-delivered table1) - 4) \n")

            # Drinks predicates
            # Flag for hot drinks disabled
            hot_id = 0

            for ii in range(0, drinkspertable):

                #Hot drinks per table
                hot_drinks = hot_4_table[table_id - 1]

                drink_id = drink_id + 1
                # Identity
                drink_identity = drink_identity + "(equals drink" + chr(64 + drink_id) + " drink" + chr(
                    64 + drink_id) + ")"
                if not drink_id % 2:
                    drink_identity = drink_identity + "\n\t\t"
                #drink_notready = drink_notready + "(= (time-drink-ready drink" + chr(64 + drink_id) + ") -1) \n"
                # Ordered by the table
                ordered_by = ordered_by + "(ordered drink"+ chr(64 + drink_id) + " table" + str(table_id)+" )\n\t\t"

                if hot_id < hot_drinks:
                    hot_drink_string = hot_drink_string + "(= (fl-hot drink"+ chr(64 + drink_id) + ") 1)\n\t\t"
                    hot_id = hot_id + 1
                else:
                    biscuit_id = biscuit_id + 1
                    hot_drink_string = hot_drink_string + "(= (fl-hot drink" + chr(64 + drink_id) + ") 0)\n\t\t"
                    # a biscuit is related to each cold drinks
                    drink4biscuit_init = (drink4biscuit_init + 
                                            "(drink-for-biscuit drink"+ chr(64 + drink_id) +
                                            " biscuit" + chr(64 + biscuit_id)+")\n\t\t" )
                    biscuit_identity = biscuit_identity + "(equals biscuit" + chr(64 + biscuit_id) + " biscuit" + chr(
                    64 + biscuit_id) + ")"
                    if not biscuit_id % 2:
                        biscuit_identity = biscuit_identity + "\n\t\t"
                    
                    ordered_biscuit = ordered_biscuit + "(ordered biscuit"+ chr(64 + biscuit_id) + " table" + str(table_id)+" )\n\t\t"

        customers = customers + "(=(fl-customers table" + str(table_id)+") " + str(drinkspertable) + ")\n\t\t"


    # Find the placeholders strings in the templates and replace it with the generated string

    init_txt = init_txt.replace(';WAITER_INITIAL_POS_PH', waiter_init_pos)
        #waiter hand-free condition
    init_txt = init_txt.replace(';HAND_FREE', hand_free_init)
        #waiter free condition
    init_txt = init_txt.replace(';WAITER_FREE', waiter_free_init)
        #tray not carried fluent
    init_txt = init_txt.replace(';TRAY_NOT_CARRIED', tray_carried_init)
        #drink identity
    init_txt = init_txt.replace(';DRINK_IDENTITY_PH', drink_identity)
        #biscuit identity
    init_txt = init_txt.replace(';BISCUIT_IDENTITY_PH', biscuit_identity)
        #places free at start
    init_txt = init_txt.replace(';PLACE_FREE', place_free_init)
        #drink not ready
   # init_txt = init_txt.replace(';DRINK_NOTREADY_INIT_PH', drink_notready)
        #table initialization
   # init_txt = init_txt.replace(';TABLE_TIME_INIT_PH', drink_delivered)
        #customers per table
    init_txt = init_txt.replace(';CUSTOMERS_PER_TABLE', customers)
        #ordered by
    init_txt = init_txt.replace(';ORDERED_BY_PH', ordered_by)
        #ordered by
    init_txt = init_txt.replace(';ORDERED_BISCUIT', ordered_biscuit)
        #hot drinks
    init_txt = init_txt.replace(';HOT_FLAG', hot_drink_string)
        #biscuit identity
    init_txt = init_txt.replace(';DRINK_FOR_BISCUIT', drink4biscuit_init)
        #

    return(init_txt)

def metric_edit():

    "Read the metric txt file"
    metric_name = "Domain_Metric.txt"
    metric_file = open(cwd + "/" + metric_name, "r")
    metric_txt = metric_file.read()
    return(metric_txt)

def run(Plan_Eng, Pddl_domain, Pddl_problem, Optimizer, g_val, h_val, opt_alg , run_output_file):	

    domain_string = "./" + wd + "/" + Pddl_domain
    problem_string = "./" + wd + "/" + Pddl_problem
    # try torun the planning engine
    flag = 0
    gh_str = "H_VALUE: " + str(h_val) + "\nG_VALUE: " + str(g_val) + "\n"
    run_output_file.write(gh_str)
    
    try:
        result = subprocess.run([engine_path, "-o", domain_string, "-f", problem_string,
                                "-hw", str(h_val), "-gw", str(g_val)
                                ],
                                check=True, timeout=max_run_time, capture_output=True)
        #extract output and error and put them in formatted form
        
    except (subprocess.TimeoutExpired):
        run_output_file.write("SUCCESS: " + str(flag) + "\n")
        fail_str = 'Solution not found for ' + Pddl_problem + 'in  ' + str(max_run_time) + ' seconds'
        print(fail_str)
        
    except (subprocess.CalledProcessError):
        run_output_file.write("SUCCESS: " + str(flag) + "\n")
        fail_str = 'Error found during the solution of ' + Pddl_problem
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
    #key_pos = {key:0 for key in output_keywords}
    #not_end = 1
    
    for k in output_keywords:
        start = tot_out.find(k)
        end = tot_out.find("\n", start ,-1) + 1
        trim_out = trim_out + tot_out[start:end]
        
    return trim_out
    
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    """ This function asks the user to insert the number of
        customers for each table and to specify the number of 
        hot drinks for each of them and it automatically generates
        the problem file for the pddl planning engine
    """
    #Input selector
    if GUI_Input:
        #Graphic user interface
        [waiter_number, drink4table, hot4table] = gui()
    else:
        waiter_number = waiter_number_global
        drink4table = drink4table_global
        hot4table = hot4table_global

    print(waiter_number)
    print(drink4table)
    print(hot4table)

    [header_new, goal_new] = headgoal_edit(waiter_number, sum(drink4table))
    init_new = init_edit(waiter_number, drink4table, hot4table)
    metric_txt = metric_edit()

    #print(header_new)
    #print(goal_new)
    #print(init_new)

    #Sum the text and create the new pddl problem
    Pddl_problem = header_new + '\n' + init_new + '\n' + goal_new + '\n' + metric_txt
    output_file = open(cwd + "/" + wd + "/"+ problem_name, "w")
    output_file.write(Pddl_problem)
    output_file.close()

    if RUN:
        out_name = problem_name[0:-5]
        output_string = "output_" + out_name + ".txt"
        run_output_file = open(cwd + "/" + wd + "/"+ output_string, "w")
	
        # Output status matrix initialization
        status_array = [ 0 for i in range(len(g_values)*len(h_values))]
        output_matrix = [[[0 for  i in range(len(g_values))] for j in range(len(h_values))] for k in range(len(output_keywords))]
        print(output_matrix)
	    
        run_count = 0 
        for g_value in g_values:
            for h_value in h_values:
                run_fail = 0		# Flag to check ouput for this 
                run_script = run(Plan_Engine, Pddl_domain,  problem_name, Optimizer, g_value, h_value, opt_alg, run_output_file)
                res_run_str = problem_name + " with hw = " + str(h_value) + " gw = " + str(g_value)
                if run_script:
                    print("Succesful run " + res_run_str)
                else:
                    print("Unsuccesful run " + res_run_str)
                    run_fail = 1
                status_array[run_count] = run_fail
                run_count += 1       
        run_output_file.close()
        print(output_matrix)
	
        if PARSE:
	    
            #Read the output file to detect the interesting keywords            
            with open(cwd + "/" + wd + "/"+ output_string, "r") as read_run_output:
                for line in read_run_output:
                    key_id = 0
                    for key in output_keywords:
                        run_id = 0
                        if key in line:                        
                            col = run_id %  len(h_values)
                            row = run_id -  col * len(g_values)
                            if status_array[run_id] == 0:
                                
                                output_matrix[key_id][row][col] = line[len(key):-1] 
                            else:
                                 output_matrix[key_id][row][col] = 0
                            run_id += 1
                        key_id += 1
        print(status_array)
        print(output_matrix)
                
    



