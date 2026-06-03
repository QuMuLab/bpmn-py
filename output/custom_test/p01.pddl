(define (problem p01)
    (:domain custom_test)

    (:objects
		StartEvent_1 - startEvent
		Event_0qjodak - endEvent
		Activity_0vfcr05 - task
		Activity_0ag5qrv - task
		Activity_08fozpt - task
		Activity_0jnhyvv - task
		Activity_1xsveje - task
		Activity_0pjbpmt - task
		Gateway_0dlrg8q - inclusiveGateway
		Gateway_0i9jge8 - inclusiveGateway
    )

    (:init
		(connected StartEvent_1 Gateway_0dlrg8q)
		(connected Gateway_0dlrg8q Activity_0vfcr05)
		(connected Activity_0vfcr05 Activity_0ag5qrv)
		(connected Gateway_0dlrg8q Activity_08fozpt)
		(connected Gateway_0dlrg8q Activity_0jnhyvv)
		(connected Activity_08fozpt Activity_1xsveje)
		(connected Activity_0jnhyvv Activity_0pjbpmt)
		(connected Activity_1xsveje Gateway_0i9jge8)
		(connected Activity_0pjbpmt Gateway_0i9jge8)
		(connected Activity_0ag5qrv Gateway_0i9jge8)
		(connected Gateway_0i9jge8 Event_0qjodak)
		(active StartEvent_1)
    )

    (:goal
		(finished)
    )
)