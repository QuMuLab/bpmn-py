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
        (begun)
        (finished)
    )

)