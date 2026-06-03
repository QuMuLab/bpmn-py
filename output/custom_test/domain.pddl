(define (domain custom_test)

    (:requirements
        :typing
        :negative-preconditions
        :conditional-effects
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
		(inclusive_branch_1 ?split - inclusiveGateway ?join - inclusiveGateway)
		(inclusive_branch_2 ?split - inclusiveGateway ?join - inclusiveGateway)
		(inclusive_branch_3 ?split - inclusiveGateway ?join - inclusiveGateway)
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

	(:action advance_from_Gateway_0dlrg8q
	    :parameters ()

	    :precondition (and
			(active Gateway_0dlrg8q)
	    )

	    :effect (and
			(not (active Gateway_0dlrg8q))
			(completed Gateway_0dlrg8q)
			(oneof
				(and
					(inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_0vfcr05)
				)
				(and
					(inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_08fozpt)
				)
				(and
					(inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_0jnhyvv)
				)
				(and
					(inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8)
					(inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_0vfcr05)
					(active Activity_08fozpt)
				)
				(and
					(inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8)
					(inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_0vfcr05)
					(active Activity_0jnhyvv)
				)
				(and
					(inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8)
					(inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_08fozpt)
					(active Activity_0jnhyvv)
				)
				(and
					(inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8)
					(inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8)
					(inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_0vfcr05)
					(active Activity_08fozpt)
					(active Activity_0jnhyvv)
				)
			)
	    )
	)

	(:action advance_from_Gateway_0i9jge8
	    :parameters ()

	    :precondition (and
			(active Gateway_0i9jge8)
			(or
				(and
					(inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8)
					(not (inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8))
					(not (inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8))
					(active Activity_0ag5qrv)
				)
				(and
					(not (inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8))
					(inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8)
					(not (inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8))
					(active Activity_1xsveje)
				)
				(and
					(not (inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8))
					(not (inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8))
					(inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_0pjbpmt)
				)
				(and
					(inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8)
					(inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8)
					(not (inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8))
					(active Activity_0ag5qrv)
					(active Activity_1xsveje)
				)
				(and
					(inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8)
					(not (inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8))
					(inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_0ag5qrv)
					(active Activity_0pjbpmt)
				)
				(and
					(not (inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8))
					(inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8)
					(inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_1xsveje)
					(active Activity_0pjbpmt)
				)
				(and
					(inclusive_branch_1 Gateway_0dlrg8q Gateway_0i9jge8)
					(inclusive_branch_2 Gateway_0dlrg8q Gateway_0i9jge8)
					(inclusive_branch_3 Gateway_0dlrg8q Gateway_0i9jge8)
					(active Activity_0ag5qrv)
					(active Activity_1xsveje)
					(active Activity_0pjbpmt)
				)
			)
	    )

	    :effect (and
			(not (active Gateway_0i9jge8))
			(active Event_0qjodak)
			(completed Gateway_0i9jge8)
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