(define (domain ai4ro2_E)
    (:requirements :adl :typing :fluents)
    (:types place drink waiter)
    (:predicates 
		(at-waiter ?w - waiter ?t  - place)
        (tray-taken)
		(tray-empty)
        (tray-carried ?w - waiter)
        (hand-free ?w - waiter)
        (clean ?t - place)
        (ordered ?d - drink ?t - place)
		(has3)(has2)(has1)
		;(table-empty) ;not useful in the main part
		
		(order-ready ?d - drink)
		(order-delivered ?d - drink)
		(order-carried ?d - drink ?w - waiter)
		
		;(hot ?d - drink)
		;(free-barista)
	)
	(:functions 
		(distance ?t1 - place ?t2 - place)
		(fl-hot ?d - drink)
		(fl-tray-taken ?w - waiter)
		(time-barista)
		(time-waiter ?w - waiter)
		(time-drink-ready ?d - drink)
	)
        
	(:action prepare
		:parameters (?d - drink)
		:precondition (not (order-ready ?d))
        :effect (and
					(increase (time-barista) (+  3   (* 2 (fl-hot ?d ))  ) )
					(assign (time-drink-ready ?d) (+ (+  3   (* 2 (fl-hot ?d ))  )(time-barista)))
					(order-ready ?d)
				)
	)       
	
;	(:durative-action prepare-cold
;		:parameters (?d - drink)
;		:duration (3)
;		:precondition (and (over all (not(hot ?d))) (at start(free-barista)))
;        :effect (and  (at end(order-ready ?d)) 
;							(at start(not(free-barista))) (at end(free-barista))  )
;	)
; 

;    (:durative-action move_no_tray     
;        :parameters  (?from - place ?to - place)
;		:duration (= ?duration (distance ?from ?to))
;        :precondition (and (at-robby ?from ) (connected ?from ?to))      
;        :effect (and  (at-robby ?to )(not (at-robby ?from ))))
 
)
       