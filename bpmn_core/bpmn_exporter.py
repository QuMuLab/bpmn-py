from bpmn_core import bpmn_diagram, bpmn_elements, pddl_classes
from itertools import combinations
import os

class BPMNExporter:
    """
    Exports a BPMN Diagram object to pddl.

    Args:
        diagram: The diagram object you wish to export.
    """
    def __init__(self, diagram: bpmn_diagram.Diagram):
        self.diagram = diagram
    
    def create_pddl(self):
        """
        Create the corresponding pddl for the diagram.
        """
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

    def generate_pddl_domain(self) -> tuple[pddl_classes.Domain, list[bpmn_elements.Event], dict[str, str]]:
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
            "connected ?from - element ?to - element",
        ])
    
        for msg_flow in self.diagram.msg_flows:
            source = msg_flow.startRef
            target = msg_flow.endRef

            if self.is_valid_message_flow(source, target):
                seq_flow = self.diagram.add_sequence_flow(
                    label = "Synthetic Sequence Flow",
                    element_id = msg_flow.element_id + "_from_msg_flow",
                    startRef = msg_flow.startRef,
                    endRef = msg_flow.endRef
                )

                self.elements_by_id[seq_flow.element_id] = seq_flow

        for flow in self.diagram.seq_flows:
            source = flow.startRef.element_id
            target = flow.endRef.element_id

            self.outgoing.setdefault(source, []).append(target)
            self.incoming.setdefault(target, []).append(source)

        inclusive_pairs = self.map_inclusive_gateway_pairs(start_events)
        max_incoming = 0

        for gateway in inclusive_pairs.values():
            n_incoming = len(self.get_incoming(gateway))
            if n_incoming > max_incoming:
                max_incoming = n_incoming

        for n in range(1, max_incoming + 1):
            domain.predicates.append(f"inclusive_branch_{n} ?split - inclusiveGateway ?join - inclusiveGateway")

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
                            self.get_exclusive_split_effects(gateway.element_id)
                        ]
                    )

                elif n_incoming > 1 and n_outgoing == 1:
                     domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = [f"active {gateway.element_id}"],
                        effects = [
                            f"not (active {gateway.element_id})",
                            f"active {outgoings[0]}",
                            f"completed {gateway.element_id}"
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
                            self.get_inclusive_split_effects(gateway.element_id, inclusive_pairs)
                        ]
                    )

                elif n_incoming > 1 and n_outgoing == 1:
                    domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = [
                            f"active {gateway.element_id}",
                            self.get_inclusive_join_preconditions(gateway.element_id, inclusive_pairs)
                        ],
                        effects = [
                            f"not (active {gateway.element_id})",
                            f"active {outgoings[0]}",
                            f"completed {gateway.element_id}"
                        ]
                    )     

            elif gateway.type == "parallelGateway":

                if n_incoming == 1 and n_outgoing > 1:
                    domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = [f"active {gateway.element_id}", f"completed {incomings[0]}"],
                        effects = self.get_parallel_split_effects(gateway.element_id)
                    )

                elif n_incoming > 1 and n_outgoing == 1:
                    domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = self.get_parallel_join_preconditions(gateway.element_id),
                        effects = [
                            f"not (active {gateway.element_id})",
                            f"active {outgoings[0]}",
                            f"completed {gateway.element_id}"
                        ] 
                    )

            elif gateway.type == "eventBasedGateway":
                
                if n_incoming == 1 and n_outgoing > 1:
                    domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = [f"active {gateway.element_id}"],
                        effects = [
                            f"not (active {gateway.element_id})", 
                            f"completed {gateway.element_id}",
                            self.get_event_based_split_effects(gateway.element_id)
                        ]
                    )
                
                elif n_incoming > 1 and n_outgoing == 1:
                    domain.create_action(
                        name = f"advance_from_{gateway.element_id}",
                        parameters = [],
                        preconditions = [f"active {gateway.element_id}"],
                        effects = [
                            f"not (active {gateway.element_id})", 
                            f"active {outgoings[0]}", 
                            f"completed {gateway.element_id}"
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

        for count, start_event in enumerate([None] + start_events):
            objects = [
                f"{element.element_id} - {element.type}" 
                for element in self.diagram.events + self.diagram.tasks + self.diagram.gateways
            ]
            goals = ["finished"]
            initials = [f"connected {seq_flow.startRef.element_id} {seq_flow.endRef.element_id}" for seq_flow in self.diagram.seq_flows]
            
            if start_event:
                initials.append(f"active {start_event.element_id}")

            problem = pddl_classes.Problem(
                domain = domain,
                start_event = start_event,
                problem_num = count,
                objects = objects,
                goals = goals, 
                initials = initials
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
                            result[join_id] = split_id

                for target_id in self.get_outgoing(cur_id):
                    if target_id not in visited:
                        queue.append(target_id)

        return result

    def get_exclusive_split_effects(self, gateway_id: str) -> str:
        outgoing = self.get_outgoing(gateway_id)
        choices = []

        for target_id in outgoing:
            choices.append(f"\t(active {target_id})")

        return "oneof\n" + "\n".join(choices) + "\n"
    
    def get_inclusive_split_effects(self, gateway_id: str, inclusive_pairs: dict[str, str]) -> str:
        outgoing = self.get_outgoing(gateway_id)
        subset_choices = []
        outgoing_counter_pairs = {}

        for counter, element_id in enumerate(outgoing):
            outgoing_counter_pairs[element_id] = f"(inclusive_branch_{counter + 1} {gateway_id} {inclusive_pairs[gateway_id]})"

        for r in range(1, len(outgoing) + 1):
            for subset in combinations(outgoing, r):
                counter_effects = [outgoing_counter_pairs[target_id] for target_id in subset]
                active_effects = [f"(active {target_id})" for target_id in subset]

                subset_choices.append("\t(and\n\t\t" + "\n\t\t".join(counter_effects + active_effects) + "\n\t)")

        return "oneof\n" + "\n".join(subset_choices) + "\n"
    
    def get_inclusive_join_preconditions(self, gateway_id: str, inclusive_pairs: dict[str, str]) -> str:
        split_gateway = inclusive_pairs[gateway_id]
        split_outgoing = self.get_outgoing(split_gateway)
        join_incoming = self.get_incoming(gateway_id)
        subset_choices = []
        branch_order = {}

        for counter, element_id in enumerate(split_outgoing):
            branch_order[element_id] = f"(inclusive_branch_{counter + 1} {split_gateway} {gateway_id})"

        join_incoming = sorted(
            join_incoming,
            key = lambda incoming_id: branch_order[
                self.find_split_branch(split_gateway, gateway_id, incoming_id)
            ]
        )

        for r in range(1, len(join_incoming) + 1):
            for subset in combinations(join_incoming, r):
                counter_conditions = []
                active_conditions = [f"(active {target_id})" for target_id in subset]

                for incoming_id in join_incoming:
                    branch_start = self.find_split_branch(split_gateway, gateway_id, incoming_id)

                    if branch_start:
                        branch_predicate = branch_order[branch_start]

                        if incoming_id in subset:
                            counter_conditions.append(branch_predicate)

                        else:
                            counter_conditions.append(f"(not {branch_predicate})")

                subset_choices.append("\t(and\n\t\t" + "\n\t\t".join(counter_conditions + active_conditions) + "\n\t)")

        return  "or\n" + "\n".join(subset_choices) + "\n"

    def find_split_branch(self, split_gateway: str, join_gateway: str, incoming_id: str) -> str:
        for branch_start in self.get_outgoing(split_gateway):
            queue = [branch_start]
            visited = set()

            while queue:
                cur_id = queue.pop(0)

                if cur_id in visited:
                    continue

                visited.add(cur_id)

                if cur_id == incoming_id:
                    return branch_start

                if cur_id != join_gateway:
                    queue.extend(self.get_outgoing(cur_id))

        return None

    def get_parallel_split_effects(self, gateway_id: str) -> str:
        outgoing = self.get_outgoing(gateway_id)
        
        base_effects = [
            f"not (active {gateway_id})",
            f"completed {gateway_id}",
        ]
        
        return base_effects + [f"active {target_id}" for target_id in outgoing]

    def get_parallel_join_preconditions(self, gateway_id: str) -> str:

        return [f"active {gateway_id}"] + [f"completed {target_id}" for target_id in self.get_incoming(gateway_id)]

    def get_event_based_split_effects(self, gateway_id: str) -> str:
        outgoing = self.get_outgoing(gateway_id)
        choices = []

        for target_id in outgoing:
            choices.append(f"\t(active {target_id})")

        return "oneof\n" + "\n".join(choices) + "\n"