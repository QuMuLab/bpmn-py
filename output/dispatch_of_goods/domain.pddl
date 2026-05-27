(define (domain dispatch_of_goods)

    (:requirements
        :typing
        :negative-preconditions
        :conditional-effects
        :equality
        :adl
    )

    (:types
        element
        task_or_event gateway - element
        task event - task_or_event
        userTask serviceTask manualTask scriptTask sendTask recieveTask businessRuleTask - task
        startEvent endEvent intermediateCatchEvent - event
        eventBasedGateway exclusiveGateway parallelGateway inclusiveGateway - gateway
    )

    (:predicates
		(begun)
		(finished)
		(active ?e - element)
		(completed ?e - element)
		(connected ?from - element ?to - element)
    )

	(:action start_process
	    :parameters (?e - startEvent)

	    :precondition (and
			(not (begun))
			(not (active ?e))
	    )

	    :effect (and
			(begun)
			(active ?e)
	    )
	)

	(:action advance_from_task_or_event
	    :parameters (?from - task_or_event ?to - element)

	    :precondition (and
			(active ?from)
			(connected ?from ?to)
	    )

	    :effect (and
			(not (active ?from))
			(completed ?from)
			(active ?to)
	    )
	)

	(:action advance_from_ExclusiveGateway_1mpgzhg
	    :parameters ()

	    :precondition (and
			(active ExclusiveGateway_1mpgzhg)
	    )

	    :effect (and
			(not (active ExclusiveGateway_1mpgzhg))
			(completed ExclusiveGateway_1mpgzhg)
			(oneof
				(active InclusiveGateway_0p2e5vq)
				(active Task_0e6hvnj)
			)
	    )
	)

	(:action advance_from_ExclusiveGateway_1ouv9kf
	    :parameters ()

	    :precondition (and
			(active ExclusiveGateway_1ouv9kf)
	    )

	    :effect (and
			(not (active ExclusiveGateway_1ouv9kf))
			(completed ExclusiveGateway_1ouv9kf)
			(active ParallelGateway_0z5sib0)
	    )
	)

	(:action advance_from_ParallelGateway_02fgrfq
	    :parameters ()

	    :precondition (and
			(active ParallelGateway_02fgrfq)
			(completed StartEvent_1)
	    )

	    :effect (and
			(not (active ParallelGateway_02fgrfq))
			(completed ParallelGateway_02fgrfq)
			(active Task_0vaxgaa)
			(active Task_05ftug5)
	    )
	)

	(:action advance_from_ParallelGateway_0z5sib0
	    :parameters ()

	    :precondition (and
			(active ParallelGateway_0z5sib0)
			(completed ExclusiveGateway_1ouv9kf)
			(completed Task_05ftug5)
	    )

	    :effect (and
			(not (active ParallelGateway_0z5sib0))
			(completed ParallelGateway_0z5sib0)
			(active Task_0sl26uo)
	    )
	)

	(:action advance_from_InclusiveGateway_0p2e5vq
	    :parameters ()

	    :precondition (and
			(active InclusiveGateway_0p2e5vq)
	    )

	    :effect (and
			(not (active InclusiveGateway_0p2e5vq))
			(completed InclusiveGateway_0p2e5vq)
			(oneof
				(and
					(active Task_12j0pib)
				)
				(and
					(active Task_0jsoxba)
				)
				(and
					(active Task_12j0pib)
					(active Task_0jsoxba)
				)
			)
	    )
	)

	(:action advance_from_InclusiveGateway_1dgb4sg
	    :parameters ()

	    :precondition (and
			(active InclusiveGateway_1dgb4sg)
	    )

	    :effect (and
			(not (active InclusiveGateway_1dgb4sg))
			(completed InclusiveGateway_1dgb4sg)
			(active ExclusiveGateway_1ouv9kf)
	    )
	)

	(:action end_process
	    :parameters (?e - endEvent)

	    :precondition (and
			(active ?e)
	    )

	    :effect (and
			(finished)
	    )
	)

)