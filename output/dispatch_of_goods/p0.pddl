(define (problem p0)
    (:domain dispatch_of_goods)

    (:objects
		startEvent_z1M3YlR - startEvent
		endEvent_p8AcLZp - endEvent
		task_Tpqs68K - task
		task_BlAsWkw - task
		task_eNLN1Qa - task
		task_mUk0fAo - task
		task_GZUDtgp - task
		task_tK74ZOt - task
		task_DJfv7Na - task
		exclusiveGateway_WkKJIgL - exclusiveGateway
		exclusiveGateway_qji6rCD - exclusiveGateway
		parallelGateway_A2PIquB - parallelGateway
		parallelGateway_iij1lFV - parallelGateway
		inclusiveGateway_nPWwbaI - inclusiveGateway
		inclusiveGateway_oI0DsQF - inclusiveGateway
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
    )

    (:goal
		(finished)
    )
)