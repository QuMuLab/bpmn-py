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

	(:action advance_start_event
	    :parameters (?from - startEvent ?to - element)

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

	(:action advance_intermediate_event
	    :parameters (?from - intermediateCatchEvent ?to - element)

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
	    )

	    :effect (and
			(not (active ?g))
			(forall (?to - element) (when (connected ?g ?to) (active ?to)))
			(completed ?g)
	    )
	)

	(:action parallel_gateway_join
	    :parameters (?g - parallelGateway ?to - element)

	    :precondition (and
			(connected ?g ?to)
			(forall (?from - element) (imply (connected ?from ?g) (active ?from)))
	    )

	    :effect (and
			(active ?to)
			(completed ?g)
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
			(forall (?branch - element) (imply (branch_started ?split ?branch) (completed ?branch)))
	    )

	    :effect (and
			(not (active ?join))
			(completed ?g)
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