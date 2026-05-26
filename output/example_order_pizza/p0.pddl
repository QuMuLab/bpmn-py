(define (problem p0)
    (:domain example_order_pizza)

    (:objects
		StartEvent_IGf1Xl3 - startEvent
		IntermediateCatchEvent_KDphyTp - intermediateCatchEvent
		EndEvent_oY2X1XC - endEvent
		IntermediateCatchEvent_Iqnikk3 - intermediateCatchEvent
		IntermediateCatchEvent_mrBqQMg - intermediateCatchEvent
		IntermediateCatchEvent_9F991nB - intermediateCatchEvent
		EndEvent_6Fq8ngT - endEvent
		Task_5lUi66h - userTask
		Task_cPKP1q6 - userTask
		Task_BzAyBJ8 - userTask
		Task_vb7POph - userTask
		EventBasedGateway_0PzWtnZ - eventBasedGateway
		EventBasedGateway_LmIag2v - eventBasedGateway
    )

    (:init
		(connected StartEvent_IGf1Xl3 : Pizza Wanted Task_5lUi66h : Order Pizza)
		(connected Task_5lUi66h : Order Pizza EventBasedGateway_0PzWtnZ : )
		(connected EventBasedGateway_0PzWtnZ :  IntermediateCatchEvent_KDphyTp : Pizza Recieved)
		(connected IntermediateCatchEvent_KDphyTp : Pizza Recieved Task_cPKP1q6 : Eat Pizza)
		(connected Task_cPKP1q6 : Eat Pizza EndEvent_oY2X1XC : Pizza eaten)
		(connected EventBasedGateway_0PzWtnZ :  IntermediateCatchEvent_Iqnikk3 : 30 Minutes)
		(connected IntermediateCatchEvent_Iqnikk3 : 30 Minutes Task_BzAyBJ8 : Complain to Delivery Service)
		(connected Task_BzAyBJ8 : Complain to Delivery Service EventBasedGateway_LmIag2v : )
		(connected EventBasedGateway_LmIag2v :  IntermediateCatchEvent_mrBqQMg : Pizza Recieved)
		(connected IntermediateCatchEvent_mrBqQMg : Pizza Recieved Task_cPKP1q6 : Eat Pizza)
		(connected EventBasedGateway_LmIag2v :  IntermediateCatchEvent_9F991nB : 20 Minutes)
		(connected IntermediateCatchEvent_9F991nB : 20 Minutes Task_vb7POph : Cancel Pizza)
		(connected Task_vb7POph : Cancel Pizza EndEvent_6Fq8ngT : Order Cancelled)
    )

    (:goal
		(finished)
    )
)