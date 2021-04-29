(define (domain ai4ro2_E)
    (:requirements :adl :typing :fluents)
    (:types 
			place drink waiter - object
			Bar - place
	)
    (:predicates 
		(at-waiter ?w - waiter ?t  - place)
		(start-moving-to ?w - waiter ?to - place)
		
        (tray-taken)
		(tray-empty)
        ;(tray-carried ?w - waiter)
		(has3 ?w - waiter)(has2 ?w - waiter)(has1 ?w - waiter)
        (hand-free ?w - waiter)
		
        (ordered ?d - drink ?t - place)
		
		(free-barista)
		(free-waiter ?w)
		
		(start-order-preparing ?d - drink)
		(order-prepared ?d - drink)
		(order-ready ?d - drink)
		(order-carried ?d - drink ?w - waiter)
		(order-delivered ?d - drink)
		
		(drink-cooling ?d - drink)
		(drink-consuming ?d - drink)
		
        (clean ?t - place)
		(start-cleaning ?w - waiter ?t - place)
		
		(equals ?d1 - drink ?d2 - drink)
	)
	(:functions 
		(distance ?t1 - place ?t2 - place)
		(fl-table-size ?t - place)
		(fl-hot ?d - drink)
		(fl-customers ?t - place)
		(fl-tray-carried ?w - waiter)
		
		(fl-drink-cooling ?d - drink)
		(fl-drink-consuming-len ?d - drink)
		(fl-order-len)
		(fl-clean-len ?w - waiter)
	)
	
	;;;;;; BARISTA ORDER PREPARATION ;;;;;;;
	
	(:action 	a-order-start
		:parameters 	(?d - drink)
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
		:parameters		(?d - drink)
		:precondition	(start-order-preparing ?d)
		:effect			(increase (fl-order-len) #t)
	)
	(:event		e-order-end
		:parameters		(?d - drink)
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
		:parameters		(?d - drink)
		:precondition	(and
							(order-prepared ?d) (not (order-delivered ?d))
							(> (fl-hot ?d) 0)
						)
		:effect			(decrease (fl-drink-cooling) #t)
	)	;notice it will be stopped by the drink being delivered
	
	;;;;;;;;;;;;;;;;;;;;;;;;;;
	
	;;;;;	DELIVERY	;;;;;;
	
	(:action pick-up-drink    
        :parameters  (?t - Bar ?w - waiter ?d - drink)
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
	(:action put-down-drink    
        :parameters  (?t - place ?w - waiter ?d - drink)
        :precondition 	(and 
							(ordered ?d ?t)
							;(not (tray-carried ?w))
							(= (fl-tray-carried ?w) 0)
							(at-waiter ?w ?t)
							(order-carried ?d ?w)
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
							(start-moving-to ?w ?to)
							(<= (fl-dist-from-goal ?w) 0)
						)
		:effect			(and
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
		:parameters		(?d - drink)
		:precondition	(drink-consuming ?d)
		:effect			(decrease (fl-drink-consuming-len ?d) #t)
	)
	(:event		e-end-drinking
		:parameters		(?d - drink ?t - place)
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
	;(:event		e-free-table
	;	:parameters		(?t - place)
	;	:precondition	(and
	;						(not (empty ?t))
	;						(<= (fl-customers ?t) 0)
	;					)
	;	:effect			(and
	;						(empty ?t)
	;					)
	;)
	
	;;;;;;;;;;;;;;;;;;;;;;;;;
	
	;;;;;;;	TRAY	;;;;;;;;;
	
	(:action pick-2-tray   
        :parameters		(?t - Bar ?w - waiter ?d1 - drink ?d2 - drink)
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
        :parameters		(?t - Bar ?w - waiter ?d3 - drink)
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
        :parameters		(?t - place ?w - waiter ?d3 - drink)
        :precondition	(and (has3 ?w)(at-waiter ?w ?t)
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
        :parameters		(?t - place ?w - waiter ?d2 - drink)
        :precondition	(and (has2 ?w)(at-waiter ?w ?t)
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
        :parameters		(?t - place ?w - waiter ?d1 - drink)
        :precondition	(and (has1 ?w)(at-waiter ?w ?t)
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
       
