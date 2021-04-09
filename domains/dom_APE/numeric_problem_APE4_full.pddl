(define (problem ai4ro2_E_problem)   
    (:domain ai4ro2_E)
    (:objects 
		table1 table2 table3 table4 - Table
		bar - Bar
        drinkA drinkB drinkC drinkD - Drink
        biscuitA biscuitB biscuitC biscuitD - Biscuit
        drinkE drinkF drinkG drinkH - Drink
        w1 w2 - waiter 
	)
    
    (:init
		(hand-free w1)
		(hand-free w2)
		(at-waiter w1 bar)
		(at-waiter w2 table1)
		(free-barista)
		(free-waiter w1)
		(free-waiter w2)
		(tray-empty)
		
		(= (fl-tray-carried w1) 0)
		(= (fl-tray-carried w2) 0)
		
		(= (fl-hot drinkA) 0)(drink-for-biscuit drinkA biscuitA)
		(= (fl-hot drinkB) 0)(drink-for-biscuit drinkB biscuitB)
		(= (fl-hot drinkC) 0)(drink-for-biscuit drinkC biscuitC)
		(= (fl-hot drinkD) 0)(drink-for-biscuit drinkD biscuitD)
		(= (fl-hot drinkE) 1)
		(= (fl-hot drinkF) 1)
		(= (fl-hot drinkG) 1)
		(= (fl-hot drinkH) 1)
		
		(= (distance bar table1) 2) 	(= (distance table1 bar) 2)
		(= (distance bar table2) 2) 	(= (distance table2 bar) 2)
		(= (distance table1 table2) 1)	(= (distance table2 table1) 1)
		
		(= (distance bar table3) 3) 	(= (distance table3 bar) 3)
		(= (distance table1 table3) 1) 	(= (distance table3 table1) 1)
		(= (distance table3 table2) 1)	(= (distance table2 table3) 1)
		
		(= (distance bar table4) 3) 	(= (distance table4 bar) 3)
		(= (distance table1 table4) 1) 	(= (distance table4 table1) 1)
		(= (distance table4 table2) 1)	(= (distance table2 table4) 1)
		(= (distance table4 table3) 1)	(= (distance table3 table4) 1)
		
		(= (fl-table-size table1) 1)
		(= (fl-table-size table2) 1)
		(= (fl-table-size table3) 2)
		(= (fl-table-size table4) 1)
		
        (ordered drinkA table1)(ordered biscuitA table1)
        (ordered drinkB table1)(ordered biscuitB table1)
        (ordered drinkC table4)(ordered biscuitC table4)
        (ordered drinkD table4)(ordered biscuitD table4)
        (ordered drinkE table3)
        (ordered drinkF table3)
        (ordered drinkG table3)
        (ordered drinkH table3)
		
        (=(fl-customers table1) 2)
        (=(fl-customers table2) 0)
        (=(fl-customers table3) 4)
        (=(fl-customers table4) 2)
        
		(place-free table2)(place-free table3)(place-free table4)
		
        (equals drinkA drinkA)(equals drinkB drinkB)
        (equals drinkC drinkC)(equals drinkD drinkD)
        (equals drinkE drinkE)(equals drinkF drinkF)
        (equals drinkG drinkG)(equals drinkH drinkH)
		(equals biscuitA biscuitA)(equals biscuitB biscuitB)
		(equals biscuitC biscuitC)(equals biscuitD biscuitD)
    )
        
	(:goal (and (order-delivered drinkA) (order-delivered drinkB)
				(order-delivered biscuitA)(order-delivered biscuitB)	
				(order-delivered drinkC) (order-delivered drinkD)
				(order-delivered biscuitC)(order-delivered biscuitBD)
				(order-delivered drinkE) (order-delivered drinkF) 
				(order-delivered drinkG) (order-delivered drinkH) 
				(clean table1)(clean table2)(clean table3)(clean table4)
				(at-waiter w1 bar)
				(not(tray-taken))
			)
	)
    (:metric minimize #t)
)