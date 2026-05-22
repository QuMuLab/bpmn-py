(define (problem p0)
    (:domain dispatch_of_goods)

    (:objects
		StartEvent_1 - startEvent
		EndEvent_1fx9yp3 - endEvent
		Task_12j0pib - task
		Task_0jsoxba - task
		Task_0vaxgaa - task
		Task_0e6hvnj - task
		Task_0s79ile - task
		Task_05ftug5 - task
		Task_0sl26uo - task
		ExclusiveGateway_1mpgzhg - exclusiveGateway
		ExclusiveGateway_1ouv9kf - exclusiveGateway
		ParallelGateway_02fgrfq - parallelGateway
		ExclusiveGateway_0z5sib0 - parallelGateway
		InclusiveGateway_0p2e5vq - inclusiveGateway
		InclusiveGateway_1dgb4sg - inclusiveGateway
    )

    (:init
		(connected ExclusiveGateway_1mpgzhg InclusiveGateway_0p2e5vq)
		(connected InclusiveGateway_0p2e5vq Task_12j0pib)
		(connected InclusiveGateway_0p2e5vq Task_0jsoxba)
		(connected Task_12j0pib InclusiveGateway_1dgb4sg)
		(connected Task_0jsoxba InclusiveGateway_1dgb4sg)
		(connected InclusiveGateway_1dgb4sg ExclusiveGateway_1ouv9kf)
		(connected StartEvent_1 ParallelGateway_02fgrfq)
		(connected ParallelGateway_02fgrfq Task_0vaxgaa)
		(connected ParallelGateway_02fgrfq Task_05ftug5)
		(connected Task_0vaxgaa ExclusiveGateway_1mpgzhg)
		(connected ExclusiveGateway_1mpgzhg Task_0e6hvnj)
		(connected Task_0e6hvnj Task_0s79ile)
		(connected Task_0s79ile ExclusiveGateway_1ouv9kf)
		(connected ExclusiveGateway_1ouv9kf ExclusiveGateway_0z5sib0)
		(connected Task_05ftug5 ExclusiveGateway_0z5sib0)
		(connected ExclusiveGateway_0z5sib0 Task_0sl26uo)
		(connected Task_0sl26uo EndEvent_1fx9yp3)
		(paired_inclusive InclusiveGateway_0p2e5vq InclusiveGateway_1dgb4sg)
    )

    (:goal
		(finished)
    )
)