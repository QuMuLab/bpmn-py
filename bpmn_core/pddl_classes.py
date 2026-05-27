from bpmn_core import bpmn_elements, bpmn_diagram
from textwrap import indent, dedent
from re import sub

class Domain:
    
    def __init__(self, diagram: bpmn_diagram.Diagram, predicates: list[str]):
        self.name = diagram.name
        self.objects = [element for element in diagram.events + diagram.tasks + diagram.gateways]
        self.predicates = predicates
        self.action_strs = []

    def create_action(self, name: str, parameters: list[str], preconditions: list[str], effects: list[str]):
        action = Action(name, parameters, preconditions, effects)
        self.action_strs.append(action.create_string())

    def generate_file(self):
        actions = "\n\n".join(self.action_strs)
        predicates = "\n".join([f"({predicate})" for predicate in self.predicates])

        if actions:
            actions = indent(actions, "\t")

        if predicates:
            predicates = indent(predicates, "\t\t")

        template = """
        (define (domain {name})

            (:requirements
                :typing
                :negative-preconditions
                :conditional-effects
                :equality
                :adl
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
        {predicates}
            )

        {actions}

        )
        """

        return dedent(template).strip().format(
            name = self.name,
            predicates = predicates,
            actions = actions
        )
    
class Action:
    def __init__(self, name: str, parameters: list[str], preconditions: list[str], effects: list[str]):
        self.name = self.clean_name(name)
        self.parameters = parameters
        self.preconditions = preconditions
        self.effects = effects

    def clean_name(self, name: str) -> str:
        return sub(r"[^a-zA-Z0-9_]", "_", name)

    def create_string(self):
        preconditions_str = "\n".join(f"({precondition})" for precondition in self.preconditions)
        effects_str = "\n".join(f"({effect})" for effect in self.effects)

        if preconditions_str:
            preconditions_str = indent(preconditions_str, "\t\t")

        if effects_str:
            effects_str = indent(effects_str, "\t\t")
    
        template = """
        (:action {name}
            :parameters ({parameters})
            
            :precondition (and
        {preconditions}
            )

            :effect (and
        {effects}
            )
        )
        """

        return dedent(template).strip().format(
            name = self.name,
            parameters = ' '.join(self.parameters),
            preconditions = preconditions_str,
            effects = effects_str
        )

class Problem:
    def __init__(self, domain: Domain, start_event: bpmn_elements.Event, problem_num: int, objects: list[str], goals: list[str], initials: list[str]):
        self.domain = domain
        self.start_event = start_event
        self.problem_num = f"p{problem_num:02d}" if problem_num != 0 else "p0"
        self.objects = objects
        self.goals = goals
        self.initials = initials

    def generate_file(self):
        objects = "\n".join(f"{object}" for object in self.objects)
        initials = "\n".join(f"({initial})" for initial in self.initials)
        goals = "\n".join(f"({goal})" for goal in self.goals)

        if objects:
            objects = indent(objects, "\t\t")

        if initials:
            initials = indent(initials, "\t\t")

        if goals:
            goals = indent(goals, "\t\t")

        template = """
        (define (problem {problem_num})
            (:domain {domain_name})

            (:objects
        {objects}
            )

            (:init
        {initials}
            )

            (:goal
        {goals}
            )
        )
        """

        return dedent(template).strip().format(
            problem_num = self.problem_num,
            domain_name = self.domain.name,
            objects = objects,
            initials = initials,
            goals = goals
        )