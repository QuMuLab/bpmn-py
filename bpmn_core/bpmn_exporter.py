from bpmn_core import bpmn_diagram, bpmn_elements, pddl_classes
from itertools import combinations
from textwrap import indent, dedent
import os

# TODO:
# Message flows
# Boundary events & intermediate throw events
# Export to xml (xml to graph)

# Problem files - start events
# Customizable event based
# Finished inclusive and exclusive join actions
# Add generate parallel conditions and effects functions

# Model phd pathway -> mermaid

class BPMNExporter:

    def __init__(self, diagram: bpmn_diagram.Diagram):
        self.diagram = diagram
    
    def create_pddl(self):
        pddl_domain, start_events = self.generate_pddl_domain()
        pddl_problems = self.generate_pddl_problems(pddl_domain, start_events)

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
        start_events = [event for event in self.diagram.events if event.type == "startEvent"]

        domain = pddl_classes.Domain(self.diagram, predicates = [
            "begun",
            "finished",

            "active ?e - element",
            "completed ?e - element",
            "connected ?from - element ?to - element"
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

        domain.create_action(
            name = "start_process",
            parameters = ["?e - startEvent"],
            preconditions = ["not (begun)", "not (active ?e)"],
            effects = ["begun", "active ?e"]
        )

        domain.create_action(
            name = "advance_from_task_or_event",
            parameters = ["?from - task_or_event", "?to - element"],
            preconditions = ["active ?from", "connected ?from ?to"],
            effects = [
                "not (active ?from)", 
                "completed ?from", 
                "active ?to"
            ]
        )

        for gateway in self.diagram.gateways:
            incomings = self.get_incoming(gateway.element_id)
            outgoings = self.get_outgoing(gateway.element_id)

            n_incoming = len(incomings)
            n_outgoing = len(outgoings)
        
            if gateway.type == "exclusiveGateway":

                if n_incoming == 1 and n_outgoing > 1:
                    domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = [f"active {gateway.element_id}"],
                        effects = [
                            f"not (active {gateway.element_id})",
                            f"completed {gateway.element_id}",
                            self.generate_exclusive_gateway_effects(gateway.element_id)
                        ]
                    )

                elif n_incoming > 1 and n_outgoing == 1: # 
                     domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = [f"active {gateway.element_id}"], # need to track which branch is triggered in the split and check if its done, or maybe not? shouldnt be possible for a non chosen branch to be active 
                        effects = [
                            f"not (active {gateway.element_id})",
                            f"completed {gateway.element_id}",
                            f"active {self.get_outgoing(gateway.element_id)[0]}"
                        ]
                    )                   

            elif gateway.type == "inclusiveGateway":

                if n_incoming == 1 and n_outgoing > 1:
                    domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = [f"active {gateway.element_id}"],
                        effects = [
                            f"not (active {gateway.element_id})",
                            f"completed {gateway.element_id}",
                            self.generate_inclusive_gateway_effects(gateway.element_id)
                        ]
                    )

                elif n_incoming > 1 and n_outgoing == 1: # 
                    domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = [f"active {gateway.element_id}"], # need to track which branches are trigged in the split
                        effects = [
                            f"not (active {gateway.element_id})",
                            f"completed {gateway.element_id}",
                            f"active {self.get_outgoing(gateway.element_id)[0]}"
                        ]
                    )     

            elif gateway.type == "parallelGateway":

                if n_incoming == 1 and n_outgoing > 1:
                    domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = [f"active {gateway.element_id}", f"completed {incomings[0]}"],
                        effects = [
                            f"not (active {gateway.element_id})",
                            f"completed {gateway.element_id}",
                        ] + [f"active {outgoing}" for outgoing in outgoings] # fix
                    )

                elif n_incoming > 1 and n_outgoing == 1:
                    preconditions = [f"active {gateway.element_id}"] + [f"completed {incoming}" for incoming in incomings]

                    domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = preconditions,
                        effects = [
                            f"not (active {gateway.element_id})",
                            f"completed {gateway.element_id}",
                            f"active {outgoings[0]}"
                        ] 
                    )

            elif gateway.type == "eventBasedGateway":
                domain.create_action(
                    name = f"advance_from_{gateway.element_id}",
                    parameters = ["?g - eventBasedGateway", "?to - element"],
                    preconditions = ["active ?g", "connected ?g ?to"],
                    effects = [
                        "not (active ?g)", 
                        "active ?to", 
                        "completed ?g"
                    ]
                )

        domain.create_action(
            name = "end_process",
            parameters = ["?e - endEvent"],
            preconditions = ["active ?e"],
            effects = ["finished"]
        )

        return domain, start_events

    def generate_pddl_problems(self, domain: pddl_classes.Domain, start_events: list[bpmn_elements.Event]) -> list[pddl_classes.Problem]:
        problems = []

        for count, start_event in enumerate(start_events):
            objects = [
                f"{element.element_id} - {element.type}" 
                for element in self.diagram.events + self.diagram.tasks + self.diagram.gateways
            ]
            goals = ["finished"]
            connections = [f"connected {seq_flow.startRef} {seq_flow.endRef}" for seq_flow in self.diagram.seq_flows ]

            problem = pddl_classes.Problem(
                domain,
                start_event,
                count,
                objects,
                goals, 
                connections
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
    
    def generate_exclusive_gateway_effects(self, gateway_id: str) -> str:
        outgoing = self.get_outgoing(gateway_id)
        choices = []

        for target_id in outgoing:
            choices.append(f"\t(active {target_id})")

        return "oneof\n" + "\n".join(choices) + "\n"
    
    def generate_inclusive_gateway_effects(self, gateway_id: str) -> str:
        outgoing = self.get_outgoing(gateway_id)
        subset_choices = []

        for r in range(1, len(outgoing) + 1):
            for subset in combinations(outgoing, r):
                effects = []

                for target_id in subset:
                    effects.append(f"(active {target_id})")

                subset_choices.append("\t(and\n\t\t" + "\n\t\t".join(effects) + "\n\t)")

        return "oneof\n" + "\n".join(subset_choices) + "\n"