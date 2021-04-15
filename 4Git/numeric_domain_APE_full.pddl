(define (domain ai4ro2_E)
    (:requirements :adl :typing :fluents)
    (:types 
			place order waiter - object
			Bar - place
			Table - place
			Drink - order
			Biscuit - order
			
	)
    (:predicates 
		(at-waiter ?w - waiter ?t  - place)
		(start-moving-to ?w - waiter ?to - place)
		
        (tray-taken)
		(tray-empty)
        ;(tray-carried ?w - waiter)
		(has3 ?w - waiter)(has2 ?w - waiter)(has1 ?w - waiter)
        (hand-free ?w - waiter)
		
        (ordered ?d - Drink ?t - place)
		
		(free-barista)
		(free-waiter ?w - waiter)
		
		(start-order-preparing ?d - Drink)
		(order-prepared ?d - Drink)
		(order-ready ?d - order)
		(order-carried ?d - order ?w - waiter)
		(order-delivered ?d - order)
		
		(drink-cooling ?d - order)
		(drink-consuming ?d - order)
		
        (clean ?t - place)
		(start-cleaning ?w - waiter ?t - place)
		
		(equals ?d1 - order ?d2 - order)
		
		(serving ?w - waiter ?t - place)
		(served ?t - place)
		(place-free ?t - place)
		
		(drink-for-biscuit ?d - Drink ?b - Biscuit)
		;(already-had-biscuit ?d - Drink)
	)
	(:functions 
		(distance ?t1 - place ?t2 - place)
		(fl-table-size ?t - place)
		(fl-hot ?d - Drink)
		(fl-customers ?t - place)
		(fl-tray-carried ?w - waiter)
		
		(fl-drink-cooling ?d - order)
		(fl-drink-consuming-len ?d - Drink)
		(fl-order-len)
		(fl-clean-len ?w - waiter)
	)
	
	;;;;;; BARISTA ORDER PREPARATION ;;;;;;;
	
	(:action 	a-order-start
		:parameters 	(?d - Drink)
		:precondition 	(and 
							(free-barista)
							(not (order-prepared ?d)) 
							(not (start-order-preparing ?d))
						)
        :effect 		(and
							(not (free-barista))
							(start-order-preparing ?d)
							(assign (fl-order-len) 0)
						)
	)   
	(:process 	p-order-preparing
		:parameters		(?d - Drink)
		:precondition	(start-order-preparing ?d)
		:effect			(increase (fl-order-len) #t)
	)
	(:event		e-order-end
		:parameters		(?d - Drink)
		:precondition	(and
							(start-order-preparing ?d)
							(>= (fl-order-len) (+ 3 (* 2 (fl-hot ?d))))
						)
		:effect			(and
							(not (start-order-preparing ?d))
							(order-prepared ?d)
							(order-ready ?d)
							(assign (fl-drink-cooling ?d) 4)
							(free-barista)
						)
	)
		
	(:process 	p-drink-cooling
		:parameters		(?d - Drink)
		:precondition	(and
							(order-prepared ?d) (not (order-delivered ?d))
							(> (fl-hot ?d) 0)
						)
		:effect			(decrease (fl-drink-cooling) #t)
	)	;notice it will be stopped by the drink being delivered
	
	;;;;;;;;;;;;;;;;;;;;;;;;;;
	
	;;;;;	SERVING	;;;;;;
	
	(:action serve-table    
        :parameters  (?w - waiter ?t - Table )
        :precondition 	(and
							(not (served ?t))
						)
        :effect 		(and  
							(served ?t)
							(serving ?w ?t)
						)
	)
	
	;;;;;;;;;;;;;;;;;;;;;;;;;;
	
	;;;;;	DELIVERY	;;;;;;
	
	(:action pick-up-order    
        :parameters  (?t - Bar ?w - waiter ?d - order)
        :precondition 	(and
							;(not (tray-carried ?w))
							(= (fl-tray-carried ?w) 0)
							(at-waiter ?w ?t)
							(order-ready ?d)
							(hand-free ?w)
							
						)
        :effect 		(and  
							(not(order-ready ?d))(not (hand-free ?w))
							(order-carried ?d ?w)
						)
	)
	(:action put-down-order    
        :parameters  (?t - place ?w - waiter ?d - order)
        :precondition 	(and 
							(ordered ?d ?t)
							;(not (tray-carried ?w))
							(= (fl-tray-carried ?w) 0)
							(at-waiter ?w ?t)
							(order-carried ?d ?w)
							(serving ?w ?t)
							(>= (fl-drink-cooling ?d) 0)
						)
        :effect 		(and
							(not (order-carried ?d ?w))
							(order-delivered ?d)
							(hand-free ?w)
							(drink-consuming ?d)
							(assign (fl-drink-consuming-len ?d) 4)
						)
	)
	
	;;;;;;;;;;;;;;;;;;;;;;;;;;
	
	;;;;;	MOVE WAITER	;;;;;
	
	(:action a-start-move   
        :parameters  (?from - place ?to - place ?w - waiter)
        :precondition	(and 
							(free-waiter ?w)
							(at-waiter ?w ?from) 
							;(not (tray-carried ?w))
						)
        :effect 		(and
							(place-free ?from)
							(not (free-waiter ?w))
							(not(at-waiter ?w ?from)) 
							(start-moving-to ?w ?to)
							(assign (fl-dist-from-goal ?w) (distance ?from ?to))
						)
	)
	(:process 	p-moving
		:parameters		(?w - waiter ?to - place)
		:precondition	(start-moving-to ?w ?to)
		:effect			(decrease (fl-dist-from-goal ?w) (* (- 2 (fl-tray-carried ?w)) #t))
	)
	(:event		e-end-move
		:parameters		(?w - waiter ?to - place)
		:precondition	(and
							(place-free ?to)
							(start-moving-to ?w ?to)
							(<= (fl-dist-from-goal ?w) 0)
						)
		:effect			(and
							(not (place-free ?to))
							(not (start-moving-to ?w ?to))
							(at-waiter ?w ?to)
							(free-waiter ?w)
						)
	)
	;;;;;;;;;;;;;;;;;;;;;;;;;
	
	;;;;;	CLEAN TABLE	;;;;;
	
	(:action a-start-clean-table   
        :parameters		(?t - place ?w - waiter)
        :precondition	(and
							(free-waiter ?w)
							;(empty ?t) ;empty is not necessary if we check for fl-customers
							(not (clean ?t))
							(at-waiter ?w ?t) (hand-free ?w)
							(= (fl-customers ?t) 0)
							;(not (tray-carried ?w)) ;implicit from hand-free
						)
        :effect 	(and
						(start-cleaning ?w ?t)
						(assign (fl-clean-len ?w) (* 2 (fl-table-size ?t)))
						(not (free-waiter ?w))
					)
	)
	(:process 	p-cleaning-table
		:parameters		(?t - place ?w - waiter)
		:precondition	(start-cleaning ?w ?t)
		:effect			(decrease (fl-clean-len ?w) #t)
	)
	(:event		e-end-clean-table
		:parameters		(?t - place ?w - waiter)
		:precondition	(and
							(start-cleaning ?w ?t)
							(<= (fl-clean-len ?w) 0)
						)
		:effect			(and
							(not (start-cleaning ?w ?t))
							(clean ?t)
							(free-waiter ?w)
						)
	)
	;;;;;;;;;;;;;;;;;;;;;;;;;
	
	;;;;;	DRINKING	;;;;;
	
	(:process 	p-drinking
		:parameters		(?d - Drink)
		:precondition	(drink-consuming ?d)
		:effect			(decrease (fl-drink-consuming-len ?d) #t)
	)
	(:event		e-end-drinking
		:parameters		(?d - Drink ?t - place)
		:precondition	(and
							(ordered ?d ?t)
							(drink-consuming ?d)
							(<= (fl-drink-consuming-len ?d) 0)
						)
		:effect			(and
							(not (drink-consuming ?d))
							(decrease (fl-customers ?t) 1)
						)
	)
	
	;;;;;;;;;;;;;;;;;;;;;;;;;
	
	;;;;;;;	BISCUIT	;;;;;;;;;
	
	(:event		e-biscuit-demanded
		:parameters		(?d - Drink ?b - Biscuit)
		:precondition	(and
							(drink-consuming ?d)
							(drink-for-biscuit ?d ?b)
							(not(order-prepared ?b))
							;(= (fl-hot ?d) 0)
						)
		:effect			(and
							(order-ready ?b)
							(order-prepared ?b)
							(assign (fl-drink-cooling ?b) 4)
						)
	)
	(:process 	p-biscuit-update
		:parameters		(?b - Biscuit ?d - Drink)
		:precondition	(and
							(order-prepared ?b)
							(drink-for-biscuit ?d ?b)
						)
		:effect			(decrease (fl-drink-cooling ?b) #t)
						;(assign (fl-drink-cooling ?b) (* 1 (fl-drink-consuming-len ?d)))
	)
	
	;;;;;;;;;;;;;;;;;;;;;;;;;
	
	;;;;;;;	TRAY	;;;;;;;;;
	
	(:action pick-2-tray   
        :parameters		(?t - Bar ?w - waiter ?d1 - order ?d2 - order)
        :precondition	(and 
							(at-waiter ?w ?t)
                            (not (equals ?d1 ?d2))
							(hand-free ?w)(not (tray-taken))(tray-empty)
							(order-ready ?d1)(order-ready ?d2)
						)
        :effect (and  (not(order-ready ?d1))(not(order-ready ?d2))
						(not (hand-free ?w))(tray-taken)(not (tray-empty))
						(assign (fl-tray-carried ?w) 1)
						(order-carried ?d1 ?w) (order-carried ?d2 ?w)
						(has2 ?w)
				)
	)
	(:action pick-3-tray   
        :parameters		(?t - Bar ?w - waiter ?d3 - order)
        :precondition	(and 
							(has2 ?w)
							(at-waiter ?w ?t)
							(order-ready ?d3)
						)
        :effect (and  (not(order-ready ?d3))
						(order-carried ?d3 ?w)
						(not (has2 ?w)) (has3 ?w)
				)
	)
	
	(:action put-down-3-drink   
        :parameters		(?t - place ?w - waiter ?d3 - order)
        :precondition	(and (has3 ?w)(at-waiter ?w ?t)
							(serving ?w ?t)
							(ordered ?d3 ?t)
							(order-carried ?d3 ?w)
							(>= (fl-drink-cooling ?d3) 0)
						)
        :effect (and  (not (order-carried ?d3 ?w))
						(order-delivered ?d3)
						(not (has3 ?w)) (has2 ?w)
						(drink-consuming ?d3)
						(assign (fl-drink-consuming-len ?d3) 4)
				)
	)
	
	(:action put-down-2-drink   
        :parameters		(?t - place ?w - waiter ?d2 - order)
        :precondition	(and (has2 ?w)(at-waiter ?w ?t)
							(serving ?w ?t)
							(ordered ?d2 ?t)
							(order-carried ?d2 ?w)
							(>= (fl-drink-cooling ?d2) 0)
						)
        :effect (and  (not (order-carried ?d2 ?w))
						(order-delivered ?d2)
						(not (has2 ?w)) (has1 ?w)
						(drink-consuming ?d2)
						(assign (fl-drink-consuming-len ?d2) 4)
				)
	)
	(:action put-down-1-drink   
        :parameters		(?t - place ?w - waiter ?d1 - order)
        :precondition	(and (has1 ?w)(at-waiter ?w ?t)
							(serving ?w ?t)
							(ordered ?d1 ?t)
							(order-carried ?d1 ?w)
							(>= (fl-drink-cooling ?d1) 0)
						)
        :effect (and  (not (order-carried ?d1 ?w))
						(order-delivered ?d1)
						(not (has1 ?w))
						(tray-empty)
						(drink-consuming ?d1)
						(assign (fl-drink-consuming-len ?d1) 4)
				)
	)
	(:action drop-tray   
        :parameters		(?t - Bar ?w - waiter)
        :precondition	(and 
							;(tray-carried ?w)
							(= (fl-tray-carried ?w) 1)
							(tray-empty)(at-waiter ?w ?t)
						)
        :effect 		(and
							;(not (tray-carried ?w))
							(assign (fl-tray-carried ?w) 0)
							(not (tray-taken))
							(hand-free ?w)
						)
	)
	
	;;;;;;;;;;;;;;;;;;;;;;;;;
)
       
