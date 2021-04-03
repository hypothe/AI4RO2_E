(define (problem ai4ro2_E_problem)   
    (:domain ai4ro2_E)
    (:objects bar table1 table2 - place 
        drinkA drinkB - drink
        w - waiter 
	)
    
    (:init
		(is-bar bar)
		(hand-free w)
		(at-waiter w bar)
		
		;(empty table1)
		;(= (fl-time-empty table1) 0)
		
		(tray-empty)
		
		(= (fl-hot drinkA) 1)
		(= (fl-hot drinkB) 0)
		(= (time-barista) 0)
		(= (time-waiter w) 0)
		
		(= (time-drink-ready drinkA) -1)
		(= (time-drink-ready drinkB) -1)
		
		(= (distance bar table1) 2) 	(= (distance table1 bar) 2)
		(= (distance bar table2) 2) 	(= (distance table2 bar) 2)
		(= (distance table1 table2) 1)	(= (distance table2 table1) 1)
		
		
		(= (fl-table-size table1) 1)
		(= (fl-table-size table2) 1)
		
        (ordered drinkA table1)
        (ordered drinkB table2)
        (=(fl-customers table1) 1)
        (=(fl-customers table2) 1)
        (equals drinkA drinkA)(equals drinkB drinkB)
    )
        
	(:goal (and 
	        ;(order-delivered drinkA)
			(clean table1)(clean table2)
			)
	)
    (:metric minimize (time-waiter w))
)
