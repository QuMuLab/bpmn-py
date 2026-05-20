(define (domain Dungeon)

    (:requirements
        :typing
        :negative-preconditions
        :conditional-effects
        :equality
    )

    ; Do not modify the types
    (:types
        location colour key corridor
    )

    ; Do not modify the constants
    (:constants
        red yellow green purple rainbow - colour
    )

    (:predicates
        (hero-at ?loc - location)
        (hero-has-key ?k - key)
        (hands-free)
        
        (room-is-messy ?loc - location)
        
        (corridor-is-locked ?cor - corridor)
        (corridor-locked-with ?cor - corridor ?col - colour)
        (corridor-is-risky ?cor - corridor)
        (cor-connected-to-loc ?loc - location ?cor - corridor)
        (cor-is-collapsed ?cor - corridor)
        
        (key-at ?k - key ?loc - location)
        (key-is-colour ?k - key ?col - colour)
        (key-multi-uses ?k - key)
        (key-two-uses ?k - key)
        (key-one-use ?k - key)
        (key-no-uses ?k - key)
    )

    ; IMPORTANT: You should not change/add/remove the action names or parameters

    ;Hero can move if the
    ;    - hero is at current location ?from,
    ;    - hero will move to location ?to,
    ;    - corridor ?cor exists between the ?from and ?to locations
    ;    - there isn't a locked door in corridor ?cor
    ;Effects move the hero, and collapse the corridor if it's "risky" (also causing a mess in the ?to location)
    (:action move
      :parameters (?from ?to - location ?cor - corridor)
    
      :precondition (and
        (hero-at ?from)
        (cor-connected-to-loc ?from ?cor)
        (cor-connected-to-loc ?to ?cor)
        (not (corridor-is-locked ?cor))
        (not (cor-is-collapsed ?cor))
        (not (= ?from ?to))
      )
    
      :effect (and
        (when (corridor-is-risky ?cor)
          (and
            (cor-is-collapsed ?cor)
            (room-is-messy ?to)
          )
        )
        (not (hero-at ?from))
        (hero-at ?to)
      )
    )

    ;Hero can pick up a key if the
    ;    - hero is at current location ?loc,
    ;    - there is a key ?k at location ?loc,
    ;    - the hero's arm is free,
    ;    - the location is not messy
    ;Effect will have the hero holding the key and their arm no longer being free
    (:action pick-up

        :parameters (?loc - location ?k - key)

        :precondition (and
            (hero-at ?loc)
            (key-at ?k ?loc)
            (not (room-is-messy ?loc))
            (hands-free)
        )

        :effect (and
            (not (key-at ?k ?loc))
            (hero-has-key ?k)
            (not (hands-free))
        )
    )

    ;Hero can drop a key if the
    ;    - hero is holding a key ?k,
    ;    - the hero is at location ?loc
    ;Effect will be that the hero is no longer holding the key
    (:action drop

        :parameters (?loc - location ?k - key)

        :precondition (and
            (hero-at ?loc)
            (hero-has-key ?k)
            (not (key-at ?k ?loc))
        )

        :effect (and
            (not (hero-has-key ?k))
            (key-at ?k ?loc)
            (hands-free)
        )
    )

    ;Hero can use a key for a corridor if
    ;    - the hero is holding a key ?k,
    ;    - the key still has some uses left,
    ;    - the corridor ?cor is locked with colour ?col,
    ;    - the key ?k is if the right colour ?col,
    ;    - the hero is at location ?loc
    ;    - the corridor is connected to the location ?loc
    ;Effect will be that the corridor is unlocked and the key usage will be updated if necessary
    (:action unlock

        :parameters (?loc - location ?cor - corridor ?col - colour ?k - key)

        :precondition (and
            (hero-at ?loc)
            (hero-has-key ?k)
            (cor-connected-to-loc ?loc ?cor)
            (key-is-colour ?k ?col)
            (not (key-no-uses ?k))
            (corridor-is-locked ?cor)
            (corridor-locked-with ?cor ?col)
        )

        :effect (and
            (not (corridor-is-locked ?cor))
            (when (key-two-uses ?k) 
                (and
                    (not (key-two-uses ?k))
                    (key-one-use ?k)
                )
            )
            (when (key-one-use ?k) 
                (and
                    (not (key-one-use ?k))
                    (key-no-uses ?k)
                )
            )
        )
    )

    ;Hero can clean a location if
    ;    - the hero is at location ?loc,
    ;    - the location is messy
    ;Effect will be that the location is no longer messy
    (:action clean

        :parameters (?loc - location)

        :precondition (and
            (hero-at ?loc)
            (room-is-messy ?loc)
        )

        :effect (and
            (not (room-is-messy ?loc))
        )
    )

)