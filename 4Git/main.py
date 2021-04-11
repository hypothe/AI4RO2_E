# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Import dependencies
import PySimpleGUI as sg

#Set global variables
GUI_Input = False

def gui():

    #GUI theme
    sg.theme('Topanga')  # Add some color to the window

    # Table GUI
    images_col = [[sg.Image(".\GUI_image.png")]]
    layout_input = [
        [sg.Text('Restaurant status:')],
        [sg.Text('Active waiters', size=(15, 1)), sg.InputText()],
        [sg.Text('')],
        [sg.Text('Please enter the number of customers per table and the required hot drinks:')],
        [sg.Text('Table 1:', size=(15, 1)), sg.InputText(),sg.Text('Hod drinks:', size=(8, 1)), sg.InputText()],
        [sg.Text('Table 2:', size=(15, 1)), sg.InputText(),sg.Text('Hod drinks:', size=(8, 1)), sg.InputText()],
        [sg.Text('Table 3:', size=(15, 1)), sg.InputText(),sg.Text('Hod drinks:', size=(8, 1)), sg.InputText()],
        [sg.Text('Table 4:', size=(15, 1)), sg.InputText(),sg.Text('Hod drinks:', size=(8, 1)), sg.InputText()],
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
    hot4table = [int(values[4]), int(values[6]), int(values[8]), int(values[10])]

    return(waiters, drink4table, hot4table)


def headgoal_edit(wait_num, drink_num):
    """ This function reads the header and the goal templates and it fills it with the
        required information received from the GUI"""

    "Open the header and the goal txt file"
    header_name = ".\Domain_Header.txt"
    goal_name = ".\Domain_Goal.txt"
    header_file = open(header_name, "r")
    goal_file = open(goal_name, "r")
    header_txt = header_file.read()
    goal_txt = goal_file.read()

    "Look for placeholder 'drink'"

    "Number of drinks and waiters required"
    drinks = drink_num
    waiters = wait_num

    # Creates the drink and waiter string
    drinks_head_string = ""
    drinks_goal_string = ""
    wait_head_string = ""
    waiter_final_pos = ""

    for drink_id in range(1, drinks+1):
        drinks_head_string = drinks_head_string + "drink" + chr(64 + drink_id) + " "
        drinks_goal_string = drinks_goal_string + "(order-delivered drink" + chr(64 + drink_id) + ") "
    for wait_id in range(1, waiters+1):
        wait_head_string = wait_head_string + "w" + str(wait_id) + " "
        # waiter initial position
        if wait_id == 1:
            waiter_final_pos = waiter_final_pos + "(at-waiter w1 bar)\n"
        else:
            waiter_final_pos = waiter_final_pos + "(at-waiter w" + str(wait_id) + " table" + str(wait_id - 1) + ")\n"

    # Find the DRINK_PH sting in the templates and replace it with the generated string for the drinks and the waiters
    new_header_drinks = header_txt.replace(';DRINK_PH', drinks_head_string)
    new_header = new_header_drinks.replace(';WAIT_PH', wait_head_string)
    new_goal = goal_txt.replace(';DRINK_PH', drinks_goal_string)
    new_goal = new_goal.replace(';WAIT_PH', waiter_final_pos)

    return(new_header, new_goal)

def init_edit(wait_num, d4t, h4t):
    """ This function reads the init templates and it fills it with the
        required information received from the GUI
        """

    "Open the header and the goal txt file"
    init_name = ".\Domain_Init.txt"
    init_file = open(init_name, "r")
    init_txt = init_file.read()

    "Number of drinks and waiters required"
    waiters = wait_num
    "Drinks for tables"
    drink_4_table = d4t
    hot_4_table = h4t

    # Creates the required new strings for the init block
        #waiter strings
    waiter_time_init = ""
    hand_free_init = ""
    waiter_init_pos = ""
        #Drink strings
    drink_identity = ""
    drink_delivered = ""
    drink_notready = ""
    ordered_by = ""
    hot_drink_string = ""
        #Customers per table
    customers = ""


    #Waiter predicates
    for wait_id in range(1, waiters+1):
        #waiter time
        waiter_time_init = waiter_time_init + "(= (time-waiter w" + str(wait_id) + ") 0) \n"
        #waiter hand-free condition
        hand_free_init = hand_free_init + "(hand-free w" + str(wait_id) + ") \n"
        #waiter initial position
        if wait_id == 1:
            waiter_init_pos = waiter_init_pos + "(at-waiter w1 bar)\n"
        else:
            waiter_init_pos = waiter_init_pos + "(at-waiter w" + str(wait_id) + " table" + str(wait_id-1) + ")\n"

    #Table predicates

        # initialize the drinks counter
        drink_id = 0
    for table_id in range(1, len(drink_4_table)+1):

        # Last delivered and empty time
        drinkspertable = drink_4_table[table_id-1]

        if drinkspertable != 0:
            drink_delivered = (drink_delivered + "(= (fl-time-empty table" + str(table_id)+") -1) " +
                "(= (fl-last-delivered table1) - 4) \n")

            # Drinks predicates
            # Flag for hot drinks disabled
            hot_id = 0

            for drink_id in range(0, drinkspertable):

                #Hot drinks per table
                hot_drinks = hot_4_table[table_id - 1]

                drink_id = drink_id + 1
                # Identity
                drink_identity = drink_identity + "(equals drink" + chr(64 + drink_id) + " drink" + chr(
                    64 + drink_id) + ")"
                drink_notready = drink_notready + "(= (time-drink-ready drink" + chr(64 + drink_id) + ") -1) \n"
                # Ordered by the table
                ordered_by = ordered_by + "(ordered drink"+ chr(64 + drink_id) + " table" + str(table_id)+" ) \n"

                if hot_id < hot_drinks:
                    hot_drink_string = hot_drink_string + "(= (fl-hot drink"+ chr(64 + drink_id) + ") 1)\n"
                    hot_id = hot_id + 1
                else:
                    hot_drink_string = hot_drink_string + "(= (fl-hot drink" + chr(64 + drink_id) + ") 0)\n"
        else:
            drink_delivered = (drink_delivered + "(= (fl-time-empty table" + str(table_id)+") 0) " +
                "(= (fl-last-delivered table1) - 4)\n")

        customers = customers + "(=(fl-customers table" + str(table_id)+") " + str(drinkspertable) + ")\n"


    # Find the placeholders strings in the templates and replace it with the generated string
    # for the drinks and the waiters
        #waiter time initialization
    init_txt = init_txt.replace(';WAITER_TIME_INIT', waiter_time_init)
        #waiter initial position
    init_txt = init_txt.replace(';WAITER_INITIAL_POS_PH', waiter_init_pos)
        #waiter hand-free condition
    init_txt = init_txt.replace(';HAND_FREE', hand_free_init)
        #drink identity
    init_txt = init_txt.replace(';DRINK_IDENTITY_PH', drink_identity)
        #drink not ready
    init_txt = init_txt.replace(';DRINK_NOTREADY_INIT_PH', drink_notready)
        #table initialization
    init_txt = init_txt.replace(';TABLE_TIME_INIT_PH', drink_delivered)
        #customers per table
    init_txt = init_txt.replace(';CUSTOMERS_PER_TABLE', customers)
        #ordered by
    init_txt = init_txt.replace(';ORDERED_BY_PH', ordered_by)
        #hot drinks
    init_txt = init_txt.replace(';HOT_FLAG', hot_drink_string)


    return(init_txt)

def metric_edit():

    "Read the metric txt file"
    metric_name = ".\Domain_Metric.txt"
    metric_file = open(metric_name, "r")
    metric_txt = metric_file.read()
    return(metric_txt)

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
        waiter_number = 2
        drink4table = [4, 0, 0, 0]
        hot4table = [2, 0, 0, 0]

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
    #print(Pddl_problem)
    output_file = open(".\Custom.pddl", "w")
    output_file.write(Pddl_problem)
    output_file.close()