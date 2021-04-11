(define (problem ai4ro2_E_problem)
    (:domain ai4ro2_E)
    (:objects
		bar - Bar
		table1 table2 table3 table4 - place
        drinkA drinkB drinkC drinkD  - drink
        w1 w2 w3 w4  - waiter
	)

(:init

        ;Time Initialization
        (= (time-barista) 0)
        (= (time-waiter w1) 0) 
(= (time-waiter w2) 0) 
(= (time-waiter w3) 0) 
(= (time-waiter w4) 0) 


		;Hand free condition for each waiter
		(hand-free w1) 
(hand-free w2) 
(hand-free w3) 
(hand-free w4) 


		;Drink not-ready initialization
		(= (time-drink-ready drinkA) -1) 
(= (time-drink-ready drinkB) -1) 
(= (time-drink-ready drinkC) -1) 
(= (time-drink-ready drinkD) -1) 


		;Identity condition for each drink
		(equals drinkA drinkA)(equals drinkB drinkB)(equals drinkC drinkC)(equals drinkD drinkD)

        ;Table time initialization
        (= (fl-time-empty table1) -1) (= (fl-last-delivered table1) - 4) 
(= (fl-time-empty table2) 0) (= (fl-last-delivered table1) - 4)
(= (fl-time-empty table3) 0) (= (fl-last-delivered table1) - 4)
(= (fl-time-empty table4) 0) (= (fl-last-delivered table1) - 4)


        ;Customers per table
        (=(fl-customers table1) 4)
(=(fl-customers table2) 0)
(=(fl-customers table3) 0)
(=(fl-customers table4) 0)


        ;Hot drink ready time
        (= (fl-hot drinkA) 1)
(= (fl-hot drinkB) 1)
(= (fl-hot drinkC) 0)
(= (fl-hot drinkD) 0)


		;Position of each waiter
		(at-waiter w1 bar)
(at-waiter w2 table1)
(at-waiter w3 table2)
(at-waiter w4 table3)


        ;Ordered condition
        (ordered drinkA table1 ) 
(ordered drinkB table1 ) 
(ordered drinkC table1 ) 
(ordered drinkD table1 ) 


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

		;FIXED: Tray empty
		(tray-empty)

    )
(:goal (and
    (order-delivered drinkA) (order-delivered drinkB) (order-delivered drinkC) (order-delivered drinkD) 
	(clean table1)(clean table2)(clean table3)(clean table4)
	(at-waiter w1 bar)
(at-waiter w2 table1)
(at-waiter w3 table2)
(at-waiter w4 table3)

	(not(tray-taken))
			)
	)
(:metric minimize (time-waiter w1))
    )