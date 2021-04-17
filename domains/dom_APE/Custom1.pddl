(define (problem ai4ro2_E_problem)
    (:domain ai4ro2_E)
    (:objects
		bar - Bar
		table1 table2 table3 table4 - Table
        drinkA drinkB drinkC drinkD  - Drink
		
        biscuitA biscuitB biscuitC  - Biscuit
        w1 w2  - waiter
	)

(:init
        ;FIXED free barista
        (free-barista)
        
		;FIXED: Tray empty
		(tray-empty)
        
        ;Free waiter condition of each waiter
        (free-waiter w1)
		(free-waiter w2)
		
        
		;Hand free condition for each waiter
		(hand-free w1)
		(hand-free w2)
		

        ;Tray not carried by waiters
        (= (fl-tray-carried w1) 0)
		(= (fl-tray-carried w2) 0)
		

		;Identity condition for each drink
		(equals drinkA drinkA)(equals drinkB drinkB)
		(equals drinkC drinkC)(equals drinkD drinkD)
		
		
		;Identity condition for each biscuit
		(equals biscuitA biscuitA)(equals biscuitB biscuitB)
		(equals biscuitC biscuitC)

        ;Customers per table
        (=(fl-customers table1) 2)
		(=(fl-customers table2) 2)
		(=(fl-customers table3) 0)
		(=(fl-customers table4) 0)
		

        ;Hot drink flag
        (= (fl-hot drinkA) 0)
		(= (fl-hot drinkB) 0)
		(= (fl-hot drinkC) 1)
		(= (fl-hot drinkD) 0)
		
        
        ;Biscuit - Drink relation
        (drink-for-biscuit drinkA biscuitA)
		(drink-for-biscuit drinkB biscuitB)
		(drink-for-biscuit drinkD biscuitC)
		

		;Position of each waiter
		(at-waiter w1 bar)
		(at-waiter w2 table1)
		

        ;Ordered condition
        (ordered drinkA table1 )
		(ordered drinkB table1 )
		(ordered drinkC table2 )
		(ordered drinkD table2 )
		
        (ordered biscuitA table1 )
		(ordered biscuitB table1 )
		(ordered biscuitC table2 )
		

        ;FIXED :Table distances
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


        ;FIXED: Tables size
		(= (fl-table-size table1) 1)
		(= (fl-table-size table2) 1)
		(= (fl-table-size table3) 2)
		(= (fl-table-size table4) 1)
		
		;Places free at start
		(place-free table2)
		(place-free table3)
		(place-free table4)
		


    )

(:goal (and
        (order-delivered drinkA) (order-delivered drinkB) (order-delivered drinkC) (order-delivered drinkD) 
		
        (order-delivered biscuitA) (order-delivered biscuitB) (order-delivered biscuitC) 
	    (clean table1)(clean table2)(clean table3)(clean table4)
	    (at-waiter w1 bar)
		(at-waiter w2 table1)
		
	    (not(tray-taken))
	    )
	)

(:metric minimize #t)
    )
