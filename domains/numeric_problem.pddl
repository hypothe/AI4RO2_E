(define (problem ai4ro2_E_problem)   
    (:domain ai4ro2_E)
    (:objects 
		bar table1 table2 table3 table4 - place 
        drinkA drinkB - drink
        w1 - waiter 
	)
    
    (:init
		(is-bar bar)
		(hand-free w1)
		(at-waiter w1 bar)
		
		;(empty table1)
		(= (fl-time-empty table1) 0)
		(= (fl-last-delivered table1) -4)
		
		(= (fl-time-empty table2) -1)
		(= (fl-last-delivered table2) -4)
		;(empty table3)
		(= (fl-time-empty table3) 0)
		(= (fl-last-delivered table3) -4)
		;(empty table4)
		(= (fl-time-empty table4) 0)
		(= (fl-last-delivered table4) -4)
		
		(tray-empty)
		
		(= (fl-hot drinkA) 0)
		(= (fl-hot drinkB) 0)
		(= (time-barista) 0)
		(= (time-waiter w1) 0)
		
		(= (time-drink-ready drinkA) -1)
		(= (time-drink-ready drinkB) -1)
		
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
		
        (ordered drinkA table2)
        (ordered drinkB table2)
		
        (=(fl-customers table1) 0)
        (=(fl-customers table2) 2)
        (=(fl-customers table3) 0)
        (=(fl-customers table4) 0)
        
        (equals drinkA drinkA)(equals drinkB drinkB)
    )
        
	(:goal (and (order-delivered drinkA) (order-delivered drinkB) 
				(clean table1)(clean table2)(clean table3)(clean table4)
				(at-waiter w1 bar)
				(not(tray-taken))
			)
	)
    (:metric minimize (time-waiter w1))
)
