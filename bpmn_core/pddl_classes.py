from bpmn_core import bpmn_elements, bpmn_diagram
from textwrap import dedent
from re import sub

class Domain:
    def __init__(self, diagram: bpmn_diagram.Diagram):
        self.name = diagram.name
        self.predicates = []
        self.action_strings = []

    def create_action(self, name: str, parameters: str, preconditions: str, effects: str):
        action = Action(name, parameters, preconditions, effects)
        self.action_strings.append(action.create_string())

    def generate_file(self):
        file_str = f"""
        (define (domain {self.name})
        
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
        """

        return dedent(file_str).strip()
    
class Action:
    def __init__(self, name: str, parameters: str, preconditions: str, effects: str):
        self.name = self.clean_name(name)
        self.parameters = parameters
        self.preconditions = preconditions
        self.effects = effects

    def clean_name(self, name: str) -> str:
        return sub(r"[^a-zA-Z0-9_]", "_", name)

    def create_string(self):
        action_str = f"""
        (:action {self.name}
            :parameters ({' '.join(self.parameters)})
            
            :precondition (and
            )

            :effect (and
            )
        )
        """

        return dedent(action_str).strip()

class Problem:
    def __init__(self, domain: Domain, start_event: bpmn_elements.Event, problem_num: int):
        self.domain = domain
        self.start_event = start_event
        self.problem_num = f"p{problem_num:02d}" if problem_num != 0 else "p0"
        self.objects = []
        self.goal = []
        self.init = []

    def add_object(self, object: str):
        pass

    def add_initial_predicate(self, predicate: str):
        pass

    def add_goal(self, goal: str):
        pass

    def generate_file(self):
        file_str = f"""
        (define (problem {self.problem_num})
            (:domain {self.domain.name})

            (:objects
            )

            (:init
            )

            (:goal
                finished
            )
        )
        """

        return dedent(file_str).strip()