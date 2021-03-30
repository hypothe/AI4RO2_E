(define (problem ai4ro2_E_problem)   
    (:domain ai4ro2_E)
    (:objects bar table1 table2 table3 table4 - place 
        drinkA drinkB - drink
        w - waiter 
	)
    
    (:init
        ;(free-barista)
		(= (fl-hot drinkA) 1)
		(= (fl-hot drinkB) 0)
		(= (time-barista) 0)
		(= (time-waiter w) 0)
		(= (time-drink-ready drinkA) -1)
		(= (time-drink-ready drinkB) -1)
    )
        
    (:goal (and (order-ready drinkA) (order-ready drinkB)))
    (:metric minimize (time-barista))
)