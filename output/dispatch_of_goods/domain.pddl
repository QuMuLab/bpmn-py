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
        task event gateway - element
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
		(parallel_split ?g - parallelGateway)
		(parallel_join ?g - parallelGateway)
		(parallel_join_branch ?g - parallelGateway ?branch - element)
		(parallel_branch_started ?split - parallelGateway ?branch - element)
		(at_least_one_branch ?g - inclusiveGateway)
		(inclusive_branch_started ?g - inclusiveGateway ?e - element)
		(paired_inclusive ?split - inclusiveGateway ?join - inclusiveGateway)
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

	(:action advance_task
	    :parameters (?from - task ?to - element)

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

	(:action advance_event
	    :parameters (?from - event ?to - element)

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

	(:action exclusive_gateway_fire_ExclusiveGateway_1mpgzhg
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

	(:action inclusive_gateway_fire_InclusiveGateway_0p2e5vq
	    :parameters ()

	    :precondition (and
			(active InclusiveGateway_0p2e5vq)
	    )

	    :effect (and
			(not (active InclusiveGateway_0p2e5vq))
			(completed InclusiveGateway_0p2e5vq)
			(at_least_one_branch InclusiveGateway_0p2e5vq)
			(oneof
				(and
					(inclusive_branch_started InclusiveGateway_0p2e5vq Task_12j0pib)
					(active Task_12j0pib)
				)
				(and
					(inclusive_branch_started InclusiveGateway_0p2e5vq Task_0jsoxba)
					(active Task_0jsoxba)
				)
				(and
					(inclusive_branch_started InclusiveGateway_0p2e5vq Task_12j0pib)
					(active Task_12j0pib)
					(inclusive_branch_started InclusiveGateway_0p2e5vq Task_0jsoxba)
					(active Task_0jsoxba)
				)
			)
	    )
	)

	(:action inclusive_gateway_join
	    :parameters (?split - inclusiveGateway ?join - inclusiveGateway ?to - element)

	    :precondition (and
			(paired_inclusive ?split ?join)
			(active ?join)
			(connected ?join ?to)
			(at_least_one_branch ?split)
			(forall (?branch - element) (or (not (inclusive_branch_started ?split ?branch)) (completed ?branch)))
	    )

	    :effect (and
			(not (active ?join))
			(completed ?join)
			(active ?to)
			(not (at_least_one_branch ?split))
			(forall (?branch - element) (when (inclusive_branch_started ?split ?branch) (not (inclusive_branch_started ?split ?branch))))
	    )
	)

	(:action event_based_gateway_choose
	    :parameters (?g - eventBasedGateway ?to - element)

	    :precondition (and
			(active ?g)
			(connected ?g ?to)
	    )

	    :effect (and
			(not (active ?g))
			(active ?to)
			(completed ?g)
	    )
	)

	(:action parallel_gateway_split
	    :parameters (?g - parallelGateway)

	    :precondition (and
			(active ?g)
			(parallel_split ?g)
	    )

	    :effect (and
			(not (active ?g))
			(forall (?to - element) (when (connected ?g ?to) (and (active ?to) (parallel_branch_started ?g ?to))))
			(completed ?g)
	    )
	)

	(:action parallel_gateway_join
	    :parameters (?g - parallelGateway ?to - element)

	    :precondition (and
			(active ?g)
			(parallel_join ?g)
			(connected ?g ?to)
			(forall (?branch - element) (or (not (parallel_join_branch ?g ?branch)) (completed ?branch)))
	    )

	    :effect (and
			(not (active ?g))
			(completed ?g)
			(active ?to)
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