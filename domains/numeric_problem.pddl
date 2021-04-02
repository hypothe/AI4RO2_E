(define (problem ai4ro2_E_problem)   
    (:domain ai4ro2_E)
    (:objects bar table1 table2 table3 table4 - place 
        drinkA drinkB - drink
        w - waiter 
	)
    
    (:init
		(is-bar bar)
		(hand-free w)
		(at-waiter w bar)
		
		(empty table3)
		(empty table4)
		
		(= (fl-hot drinkA) 1)
		(= (fl-hot drinkB) 0)
		(= (time-barista) 0)
		(= (time-waiter w) 0)
		
		;(= (fl-tray-taken w) 0)
		
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
    )
        
	(:goal (and (order-delivered drinkA) (order-delivered drinkB) 
			(clean table3) (clean table4))
	)
    (:metric minimize (time-waiter w))
)