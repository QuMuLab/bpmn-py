from bpmn_core import bpmn_diagram, bpmn_elements
import os

from . import pddl_classes

# TODO:
# Test
# Message flows
# Boundary events & intermediate throw events
# Export to xml (xml to graph)

class BPMNExporter:

    def __init__(self, diagram: bpmn_diagram.Diagram):
        self.diagram = diagram
    
    def create_pddl(self):
        pddl_domain, start_events, inclusive_pairs = self.generate_pddl_domain()
        pddl_problems = self.generate_pddl_problems(pddl_domain, start_events, inclusive_pairs)

        output_folder = os.path.join(os.getcwd(), f"output/{self.diagram.name}")
        os.makedirs(output_folder, exist_ok = True)

        domain_file_path = os.path.join(output_folder, "domain.pddl")
        with open(domain_file_path, "w") as file:
            file.write(pddl_domain.generate_file())

        for pddl_problem in pddl_problems:
            problem_file_path = os.path.join(output_folder, f"{pddl_problem.problem_num}.pddl")

            with open(problem_file_path, "w") as file:
                file.write(pddl_problem.generate_file())

    def generate_pddl_domain(self) -> tuple[pddl_classes.Domain, list[bpmn_elements.Event]]:
        elements = self.diagram.get_elements()
        self.elements_by_id = {element.element_id: element for element in elements}
        self.outgoing = {}
        self.incoming = {}
        start_events = [event for event in self.diagram.events if event.type == 'startEvent']

        domain = pddl_classes.Domain(self.diagram, predicates = [
            "begun",
            "finished",

            "active ?e - element",
            "completed ?e - element",
            "connected ?from - element ?to - element",

            "at_least_one_branch ?g - inclusiveGateway",
            "branch_started ?g - inclusiveGateway ?e - element",
            "paired_inclusive ?split - inclusiveGateway ?join - inclusiveGateway",
        ])
    
        for msg_flow in self.diagram.msg_flows:
            source = self.elements_by_id[msg_flow.startRef]
            target = self.elements_by_id[msg_flow.endRef]

            if self.is_valid_message_flow(source, target):
                seq_flow = self.diagram.add_sequence_flow(
                    label = "Synthetic Sequence Flow",
                    element_id = msg_flow.element_id + "_from_msg_flow",
                    startRef = msg_flow.startRef,
                    endRef = msg_flow.endRef
                )

                self.elements_by_id[seq_flow.element_id] = seq_flow

        for flow in self.diagram.seq_flows:
            source = flow.startRef
            target = flow.endRef

            self.outgoing.setdefault(source, []).append(target)
            self.incoming.setdefault(target, []).append(source)

        inclusive_pairs = self.map_inclusive_gateway_pairs(start_events)

        domain.create_action(
            name = "start_process",
            parameters = ["?e - startEvent"],
            preconditions = ["not (begun)", "not (active ?e)"],
            effects = ["begun", "active ?e"]
        )

        domain.create_action(
            name = "advance_task",
            parameters = ["?from - task", "?to - element"],
            preconditions = ["active ?from", "connected ?from ?to"],
            effects = [
                "not (active ?from)", 
                "completed ?from", 
                "active ?to"
            ]
        )

        domain.create_action(
            name = "advance_start_event",
            parameters = ["?from - startEvent", "?to - element"],
            preconditions = ["active ?from", "connected ?from ?to"],
            effects = [
                "not (active ?from)",
                "completed ?from",
                "active ?to"
            ]
        )

        domain.create_action(
            name = "advance_intermediate_event",
            parameters = ["?from - intermediateCatchEvent", "?to - element"],
            preconditions = ["active ?from", "connected ?from ?to"],
            effects = [
                "not (active ?from)",
                "completed ?from",
                "active ?to"
            ]
        )

        domain.create_action(
            name = "exclusive_gateway_choose",
            parameters = ["?g - exclusiveGateway", "?to - element"],
            preconditions = ["active ?g", "connected ?g ?to"],
            effects = ["not (active ?g)", "active ?to", "completed ?g"]
        )

        domain.create_action(
            name = "event_based_gateway_choose",
            parameters = ["?g - eventBasedGateway", "?to - element"],
            preconditions = ["active ?g", "connected ?g ?to"],
            effects = ["not (active ?g)", "active ?to", "completed ?g"]
        )

        domain.create_action(
            name = "parallel_gateway_split",
            parameters = ["?g - parallelGateway"],
            preconditions = ["active ?g"],
            effects = [
                "not (active ?g)",
                "forall (?to - element) (when (connected ?g ?to) (active ?to))",
                "completed ?g"
            ]
        )

        domain.create_action(
            name = "parallel_gateway_join",
            parameters = ["?g - parallelGateway", "?to - element"],
            preconditions = [
                "connected ?g ?to",
                "forall (?from - element) (imply (connected ?from ?g) (active ?from))"
            ],
            effects = [
                "active ?to",
                "completed ?g"
            ]
        )

        domain.create_action(
            name = "inclusive_gateway_choose_branch",
            parameters = ["?g - inclusiveGateway", "?to - element"],
            preconditions = [
                "active ?g",
                "connected ?g ?to",
                "not (branch_started ?g ?to)"
            ],
            effects = [
                "active ?to",
                "branch_started ?g ?to",
                "at_least_one_branch ?g"
            ]
        )

        domain.create_action(
            name = "inclusive_gateway_finish_choices",
            parameters = ["?g - inclusiveGateway"],
            preconditions = ["active ?g", "at_least_one_branch ?g"],
            effects = ["not (active ?g)", "completed ?g",]
        )

        domain.create_action(
            name = "inclusive_gateway_join",
            parameters = [
                "?split - inclusiveGateway",
                "?join - inclusiveGateway",
                "?to - element"
            ],
            preconditions = [
                "paired_inclusive ?split ?join",
                "active ?join",
                "connected ?join ?to",
                "at_least_one_branch ?split",
                "forall (?branch - element) (imply (branch_started ?split ?branch) (completed ?branch))"
            ],
            effects = [
                "not (active ?join)",
                "completed ?g",
                "active ?to",
                "not (at_least_one_branch ?split)",
                "forall (?branch - element) (when (branch_started ?split ?branch) (not (branch_started ?split ?branch)))"
            ]
        )

        domain.create_action(
            name = "end_process",
            parameters = ["?e - endEvent"],
            preconditions = ["active ?e"],
            effects = ["finished"]
        )

        return domain, start_events, inclusive_pairs

    def generate_pddl_problems(self, domain: pddl_classes.Domain, start_events: list[bpmn_elements.Event], inclusive_pairs: dict[str, str]) -> list[pddl_classes.Problem]:
        problems = []

        for count, start_event in enumerate(start_events):
            objects = [
                f"{element.element_id} - {element.type}" 
                for element in self.diagram.events + self.diagram.tasks + self.diagram.gateways
            ]
            goals = ["finished"]
            connections = [f"connected {seq_flow.startRef} {seq_flow.endRef}" for seq_flow in self.diagram.seq_flows ]
            inclusive_pairs = [f"paired_inclusive {split_id} {join_id}" for split_id, join_id in inclusive_pairs.items()]

            problem = pddl_classes.Problem(
                domain, 
                start_event, 
                count, 
                objects, 
                goals, 
                connections + inclusive_pairs
            )

            problems.append(problem)

        return problems
    
    def is_valid_message_flow(self, source: bpmn_elements.Element, target: bpmn_elements.Element):
        if not source or not target:
            return False
        
        return (source.is_task() and target.is_event()) or (source.is_event() and target.is_task())
    
    def get_outgoing(self, element_id: str) -> list:
        return self.outgoing.get(element_id, [])
    
    def get_incoming(self, element_id: str) -> list:
        return self.incoming.get(element_id, [])
    
    def map_inclusive_gateway_pairs(self, start_events: list[bpmn_elements.Event]) -> dict[str, str]:
        result = {}

        for start_event in start_events:
            visited = set()
            stack = []
            queue = [start_event.element_id]

            while queue:
                cur_id = queue.pop(0)
                cur_element = self.elements_by_id.get(cur_id)

                if cur_id in visited or not cur_element:
                    continue

                visited.add(cur_id)

                if cur_element.type == "inclusiveGateway":
                    n_incoming = len(self.get_incoming(cur_id))
                    n_outgoing = len(self.get_outgoing(cur_id))

                    if n_incoming == 1 and n_outgoing > 1:
                        stack.append(cur_id)

                    elif n_incoming > 1 and n_outgoing == 1:
                        if stack:
                            split_id = stack.pop()
                            join_id = cur_id
                            result[split_id] = join_id

                for target_id in self.get_outgoing(cur_id):
                    if target_id not in visited:
                        queue.append(target_id)

        return result