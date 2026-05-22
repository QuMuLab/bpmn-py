(define (domain dispatch_of_goods)

    (:requirements
        :typing
        :negative-preconditions
        :conditional-effects
        :equality
    )

    (:types
        element
        task event gateway - element
        startEvent endEvent intermediateCatchEvent - event
        eventBasedGateway exclusiveGateway parallelGateway inclusiveGateway - gateway
    )

    (:predicates
		(begun)
		(StartEvent_1)
		(EndEvent_1fx9yp3)
		(finished)
    )

	(:action start_Ship_goods
	    :parameters ()

	    :precondition (and
			(not (begun))
			(not (StartEvent_1))
	    )

	    :effect (and
			(begun)
			(StartEvent_1)
	    )
	)

	(:action goal_Shipment_prepared
	    :parameters ()

	    :precondition (and
			(EndEvent_1fx9yp3)
	    )

	    :effect (and
			(finished)
	    )
	)

)