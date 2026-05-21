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
		(test)
		(begun)
		(StartEvent_1)
    )

	(:action test
	    :parameters (?t - task)

	    :precondition (and
			(test)
	    )

	    :effect (and
			(test)
	    )
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

)