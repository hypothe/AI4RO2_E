#!/usr/bin/env python3

# Import dependencies
import sys, getopt
import PySimpleGUI as sg 	# disabled for multiple run on docker
import os
import subprocess
import re
import data_util


#Set global variables

GUI_Input = False               # (Bool) Activate the GUI for the setting of the problem conditions
problem_name = "Custom.pddl"    # (str) Problem name, extension needed
wd = data_util.domains_wd			# (str) Working directory

# Input default variables if no gui active
waiter_number_global = 1            # (int) Number of waiters
drink4table_global = [0, 2, 0, 0]   # list of (int) Drinks ordered for each table
hot4table_global = [0, 0, 0, 0]     # list of (int) Hot drinks for table
table_number_global = 4             # number of tables present

#Paramenters
cwd = os.getcwd()
template_wd = data_util.template_wd

def gui():
    """
    Simple text GUI to insert problem data
    
    Returns:
        waiters (int):  number of waiters inserted
        drink4table (list(int)):
                        number of drinks for each table
                        inserted
        hot4table (list(int)):
                        number of hot drinks for each
                        table inserted
        prb_name (string):
                        path/to/problem_file inserted            
    """
    
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
        [sg.Text('')],
        [sg.Text('Problem Name:', size=(15, 1)), sg.InputText(problem_name)],
        [sg.Submit(), sg.Cancel()]
    ]
    # ----- Full layout -----
    layout = [[sg.Column(images_col, element_justification='c'), sg.VSeperator(),
               sg.Column(layout_input, element_justification='l')]]

    window = sg.Window('AI for Robotics II', layout)
    event, values = window.read()
    window.close()
    
    #Extract input from GUI
    waiters = int(values[2])
    drink4table = [int(values[3]), int(values[5]), int(values[7]), int(values[9])]
    hot4table = [int(values[4]), int(values[6]), int(values[8]), int(values[10])]
    prb_name = str(values[11])

    # domain file check
    if prb_name[-5:] != ".pddl":
        print("Err: Invalid pddl domain file format.")
        sys.exit()

    return waiters, drink4table, hot4table, prb_name


def headgoal_edit(wait_num, drink_num, hot_num):
    """
    Generate headgoal text from template and
    arguments
    
    Args:
        wait_num (int):     number of waiters
        drink_num (int):    total number of drinks
        hot_num (int):      total number of hot drinks
    Returns:
        new_header (str):   edited header
        new_goal (str):   edited goal
    """

    header_name = "Domain_Header.txt"
    goal_name = "Domain_Goal.txt"
    header_file = open(cwd + "/" + template_wd + "/" + header_name, "r")
    goal_file = open(cwd + "/" + template_wd  + "/" + goal_name, "r")
    header_txt = header_file.read()
    goal_txt = goal_file.read()

    ### Look for placeholder 'drink'
    drinks = drink_num
    waiters = wait_num
    
    biscuits = drinks-hot_num

    # Creates the drink and waiter string
    drinks_head_string = ""
    drinks_goal_string = ""
    biscuits_head_string = ""
    biscuits_goal_string = ""
    wait_head_string = ""
    waiter_final_pos = ""
    
    drink_id = 0
    biscuit_id = 0

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
    """
    Generate init text from template and
    arguments
    
    Args:
        wait_num (int):     number of waiters
        d4t (list(int)):    total number of drinks for
                            each table
        h4t (int):          total number of hot drinks
                            for each table
    Returns:
        init_txt (str):     edited init
    """

    init_name = "Domain_Init.txt"
    init_file = open(cwd + "/" + template_wd + "/" + init_name, "r")
    init_txt = init_file.read()

    "Number of drinks and waiters required"
    waiters = wait_num
    "Drinks for tables"
    drink_4_table = d4t
    hot_4_table = h4t

    # Creates the required new strings for the init block
    ## waiter strings
    waiter_free_init = ""
    hand_free_init = ""
    waiter_init_pos = ""
    ## Drink strings
    drink_identity = ""
    
    ordered_by = ""
    hot_drink_string = ""
    ## Customers per table
    customers = ""
    ## place initially free
    place_free_init = ""
    ## tray initially not carried by any waiter
    tray_carried_init = ""
    ## A biscuit for each cold drink
    drink4biscuit_init = ""
    ## 
    biscuit_identity = ""
    ordered_biscuit = ""

    #Waiter predicates
    for wait_id in range(1, waiters+1):
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
    ## waiter hand-free condition
    init_txt = init_txt.replace(';HAND_FREE', hand_free_init)
    ## waiter free condition
    init_txt = init_txt.replace(';WAITER_FREE', waiter_free_init)
    ## tray not carried fluent
    init_txt = init_txt.replace(';TRAY_NOT_CARRIED', tray_carried_init)
    ## drink identity
    init_txt = init_txt.replace(';DRINK_IDENTITY_PH', drink_identity)
    ## biscuit identity
    init_txt = init_txt.replace(';BISCUIT_IDENTITY_PH', biscuit_identity)
    ## places free at start
    init_txt = init_txt.replace(';PLACE_FREE', place_free_init)
    ## customers per table
    init_txt = init_txt.replace(';CUSTOMERS_PER_TABLE', customers)
    ## ordered by
    init_txt = init_txt.replace(';ORDERED_BY_PH', ordered_by)
    ## ordered by
    init_txt = init_txt.replace(';ORDERED_BISCUIT', ordered_biscuit)
    ## hot drinks
    init_txt = init_txt.replace(';HOT_FLAG', hot_drink_string)
    ## biscuit identity
    init_txt = init_txt.replace(';DRINK_FOR_BISCUIT', drink4biscuit_init)
    #
    return init_txt

def metric_edit():
    """
    Edit metric
    
    For the moment it simply retrieves the
    template one and returns it
    
    Returns:
        metric_txt (str):   (un) edited metric
    """
    
    metric_name = "Domain_Metric.txt"
    metric_file = open(cwd + "/" + template_wd + "/" + metric_name, "r")
    metric_txt = metric_file.read()
    return metric_txt

def edit(waiter_number, drink4table, hot4table, problem_name_full):
    """
    Wrapper for the various edit functions
    
    Args:
        waiter_number (int):
                            number of waiters
        drink4table (list(int)):
                            total number of drinks for
                            each table
        hot4table (list(int)):
                            total number of hot drinks
                            for each table
        problem_name_full (str):
                            path/to/problem_file to
                            generate
    """

    for ii in range(0, table_number_global):
        hot4table[ii] = min(drink4table[ii], hot4table[ii])

    [header_new, goal_new] = headgoal_edit(waiter_number, sum(drink4table), sum(hot4table))
    init_new = init_edit(waiter_number, drink4table, hot4table)
    metric_txt = metric_edit()

    #Sum the text and create the new pddl problem
    Pddl_problem = header_new + '\n' + init_new + '\n' + goal_new + '\n' + metric_txt
    with open(problem_name_full, "w") as output_file:
        output_file.write(Pddl_problem)
       

# Press the green button in the gutter to run the script.
def main(argv):
    """
    Generate a problem file compliant with our
    domain from few user inputs
    
    Inputs can be passed either by command line
    or GUI
    """
    
    usage = ("usage: pyhton3 " + argv[0] + "\n" +
             "(default values will be used in case options are not provided)\n" +
             "\t-f, --problem <arg>\tthe path and name of the PDDL problem file to generate\n" +
             "\t-w, --waiters <arg>\tthe number of waiters (int)\n" +
             "\t-d, --drinks <arg>\tthe number of total drinks for each table, as [d1,d2,d3,d4] (list<int>)\n" +
             "\t-t, --hot-drinks <arg>\tthe number of hot drinks for each table, as [t1,t2,t3,t4] (list<int>)\n" +
             "\t-g, --gui\t\tenable the GUI (overwrites everything else)\n"
             "\t-h, --help\t\tdisplay this help\n"
            )

    waiter_number = waiter_number_global
    drink4table = drink4table_global
    hot4table = hot4table_global
    
    gui_input = GUI_Input
    problem_name_full = cwd + "/" + wd + "/"+ problem_name
            
    try:
        opts, args = getopt.getopt(argv[1:], "hf:w:d:t:g", ["help", "problem=", "waiters=", "drinks=", "hot-drinks=", "gui"])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        elif opt in ("-f", "--problem"):
            problem_name_full = arg
        elif opt in ("-w", "--waiter"):
            waiter_number = int(arg)
        elif opt in ("-d", "--drinks") and arg[0] == '[' and arg[-1] == ']':
            d4t = re.findall("\d", arg)
            drink4table = list()
            try:
                for ii in range(0, table_number_global):
                    drink4table.append(int(d4t[ii]))
            except IndexError:
                print("ERR: Too few elements in the drinks for table list passed as argument")
                sys.exit()
                
        elif opt in ("-t", "--hot-drinks") and arg[0] == '[' and arg[-1] == ']':
            hot4table = list()
            h4t = re.findall("\d", arg)
            try:
                for ii in range(0, table_number_global):
                    hot4table.append(int(h4t[ii]))
            except IndexError:
                print("ERR: Too few elements in the hot-drinks for table list passed as argument")
                sys.exit()
        elif opt in ("-g", "--gui"):
            gui_input = True
    
    #Input selector
    if gui_input:
        #Graphic user interface
        waiter_number, drink4table, hot4table, new_problem_name = gui()
        problem_name_full = wd + "/"+ new_problem_name
        
    edit(waiter_number, drink4table, hot4table, problem_name_full) 
    
    print("Generated " + problem_name_full + " with:\n" +
            "number_of_waiters:\t" + str(waiter_number) + "\n" +
            "tot_drinks_for_table:\t" + str(drink4table) + "\n" +
            "hot_drinks_for_table:\t" + str(hot4table) + "\n"
        )
        
if __name__ == '__main__':
    main(sys.argv)
