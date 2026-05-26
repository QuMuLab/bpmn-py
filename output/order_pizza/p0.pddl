(define (problem p0)
    (:domain order_pizza)

    (:objects
		StartEvent_oIkUEqJ - startEvent
		EndEvent_afBR8ff - endEvent
		EndEvent_CM1NbCp - endEvent
		IntermediateCatchEvent_UcCQAUy - intermediateCatchEvent
		IntermediateCatchEvent_KkTd3NM - intermediateCatchEvent
		IntermediateCatchEvent_TuX3Kku - intermediateCatchEvent
		IntermediateCatchEvent_Nmh2veQ - intermediateCatchEvent
		Activity_0078ezj - task
		Activity_0b3tky9 - task
		Activity_13tgdd7 - task
		Activity_1k7bzjg - task
		EventBasedGateway_rMypxmz - eventBasedGateway
		EventBasedGateway_2h0VmTg - eventBasedGateway
    )

    (:init
		(connected StartEvent_1 Activity_0078ezj)
		(connected Activity_0078ezj Gateway_00a8n5n)
		(connected Gateway_00a8n5n Event_1n3fu60)
		(connected Event_1n3fu60 Activity_0b3tky9)
		(connected Activity_0b3tky9 Gateway_1ushrpr)
		(connected Gateway_1ushrpr Event_18vc2ep)
		(connected Gateway_1ushrpr Event_1ylp3d5)
		(connected Event_0p3pi5l Activity_13tgdd7)
		(connected Activity_13tgdd7 Event_1o7q4l5)
		(connected Event_1ylp3d5 Activity_1k7bzjg)
		(connected Activity_1k7bzjg Event_07029z3)
		(connected Gateway_00a8n5n Event_0p3pi5l)
		(connected Event_18vc2ep Activity_13tgdd7)
    )

    (:goal
		(finished)
    )
)