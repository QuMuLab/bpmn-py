(define (domain order_pizza)

    (:requirements
        :typing
        :negative-preconditions
        :conditional-effects
        :equality
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
		(parallel_join_pair ?g - parallelGateway ?a - element ?b - element)
		(at_least_one_branch ?g - inclusiveGateway)
		(branch_started ?g - inclusiveGateway ?e - element)
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

	(:action exclusive_gateway_choose
	    :parameters (?g - exclusiveGateway ?to - element)

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
			(forall (?to - element) (when (connected ?g ?to) (active ?to)))
			(completed ?g)
	    )
	)

	(:action parallel_gateway_join
	    :parameters (?g - parallelGateway ?a - element ?b - element ?to - element)

	    :precondition (and
			(active ?g)
			(parallel_join ?g)
			(parallel_join_pair ?g ?a ?b)
			(connected ?g ?to)
			(completed ?a)
			(completed ?b)
	    )

	    :effect (and
			(not (active ?g))
			(completed ?g)
			(active ?to)
	    )
	)

	(:action inclusive_gateway_choose_branch
	    :parameters (?g - inclusiveGateway ?to - element)

	    :precondition (and
			(active ?g)
			(connected ?g ?to)
			(not (branch_started ?g ?to))
	    )

	    :effect (and
			(active ?to)
			(branch_started ?g ?to)
			(at_least_one_branch ?g)
	    )
	)

	(:action inclusive_gateway_finish_choices
	    :parameters (?g - inclusiveGateway)

	    :precondition (and
			(active ?g)
			(at_least_one_branch ?g)
	    )

	    :effect (and
			(not (active ?g))
			(completed ?g)
	    )
	)

	(:action inclusive_gateway_join
	    :parameters (?split - inclusiveGateway ?join - inclusiveGateway ?to - element)

	    :precondition (and
			(paired_inclusive ?split ?join)
			(active ?join)
			(connected ?join ?to)
			(at_least_one_branch ?split)
			(forall (?branch - element) (or (not (branch_started ?split ?branch)) (completed ?branch)))
	    )

	    :effect (and
			(not (active ?join))
			(completed ?join)
			(active ?to)
			(not (at_least_one_branch ?split))
			(forall (?branch - element) (when (branch_started ?split ?branch) (not (branch_started ?split ?branch))))
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