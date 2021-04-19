#!/usr/bin/env python3

import random
import statistics
import numpy as np

max_drinks_ = 4 # 4
num_tables_ = 4
tot_drinks = 8 # 8
rounds1_ = 0
rounds2_ = 0

def rec(table, last_table, drink4table, hot4table, placed_drinks):
    global max_drinks_, tot_drinks_, rounds1_
    rounds1_ = rounds1_ +1
    
    if table < last_table and placed_drinks <= tot_drinks:
    
        for drink in range(0,min(max_drinks_+1, tot_drinks - placed_drinks+1)):
            drink4table[table] = drink
            
            for hot in range(0, drink+1):
                hot4table[table] = hot
                
                rec(table+1, last_table, drink4table, hot4table, placed_drinks + drink)
                               
    elif placed_drinks > 0 and random.random() <=  0.3:
        global state_list
        state_list.append(drink4table + hot4table)

### rec2 seems to be less reliable for some reason I'm too sleepy to comprehend
### we'll have to stick with the first one, nothing dramatic I'd say        
def rec2(table, last_table, drink4table, hot4table, placed_drinks):
    global max_drinks_, tot_drinks_, rounds2_
    rounds2_ = rounds2_ +1
    
    if table < last_table and placed_drinks <= tot_drinks:
        rr1 = [*range(0,min(max_drinks_+1, tot_drinks - placed_drinks+1))]
        #random.sample(rr1, k=len(rr1))
        #print(str(table) + str(rr1))
        #input()
        for drink in random.sample(rr1, k=len(rr1)):
            drink4table[table] = drink
            
            rr2 = [*range(0, drink+1)]
            #print(rr2)
            for hot in random.sample(rr2, k=len(rr2)):
                hot4table[table] = hot
                #print(hot4table)
                if random.random() < 0.74: #0.57
                    rec2(table+1, last_table, drink4table, hot4table, placed_drinks + drink)
                               
    elif placed_drinks > 0:
        global state2_list
        state2_list.append(drink4table + hot4table)
        #print(state2_list)       
        
               
def main():
    global state_list, state2_list
    random.seed()
    drink4table = [0 for ii in range(0, num_tables_)]
    hot4table = [0 for ii in range(0, num_tables_)]
    table = 0
    last_table = num_tables_
    state_list = list()
    state2_list = list()
    
    rec(table, last_table, drink4table, hot4table, 0)
    
    table = 0
    drink4table = [0 for ii in range(0, num_tables_)]
    hot4table = [0 for ii in range(0, num_tables_)]
    rec2(table, last_table, drink4table, hot4table, 0)
    
    ele_found = {"END RAND":len(state_list), "MID RAND":len(state2_list)}
    rounds = {"END RAND":rounds1_, "MID RAND":rounds2_}
    state_rev = np.array(state_list).T.tolist()
    state2_rev = np.array(state2_list).T.tolist()
    states = {"END RAND":state_rev, "MID RAND":state2_rev}
    
    for name, ss in states.items():
        var_state = list()
        avg_state = list()
        
        for drinks_table in ss:
            #print(str(drinks_table) + str(len(drinks_table)))
            #input()
            avg_state.append(statistics.mean(drinks_table))
            var_state.append(statistics.variance(drinks_table))
          
        print("{}:\nTotal found: {}/{}".format(name, ele_found[name], rounds[name]) + 
                   "\n\tAvg Drinks: {}\n\tAvg Hot: {}".format(avg_state[0:4], avg_state[4:]) + 
                   "\n\tVar Drinks: {}\n\tVar Hot: {}".format(var_state[0:4], var_state[4:]))

if __name__ == '__main__':
    main()
