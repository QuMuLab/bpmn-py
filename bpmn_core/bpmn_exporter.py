from bpmn_core import bpmn_diagram, bpmn_elements, pddl_classes
import os

class BPMNExporter:

    def __init__(self, diagram: bpmn_diagram.Diagram):
        self.diagram = diagram
    
    def is_valid_message_flow(self, source: bpmn_elements.Element, target: bpmn_elements.Element):
        if not source or not target:
            return False
        
        return (source.is_task() and target.is_event()) or (source.is_event() and target.is_task())
    
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
        elements_by_id = {element.element_id: element for element in elements}
        outgoing = {}
        incoming = {}
        start_events = []
        domain = pddl_classes.Domain(self.diagram)

        def get_outgoing(element_id: str) -> list:
            return outgoing.get(element_id, [])
    
        def get_incoming(element_id: str) -> list:
            return incoming.get(element_id, [])
    
        for msg_flow in self.diagram.msg_flows:
            source = elements_by_id[msg_flow.startRef]
            target = elements_by_id[msg_flow.endRef]

            if self.is_valid_message_flow(source, target):
                seq_flow = self.diagram.add_sequence_flow(
                    label = "Synthetic Sequence Flow",
                    element_id = msg_flow.element_id + "_from_msg_flow",
                    startRef = msg_flow.startRef,
                    endRef = msg_flow.endRef
                )

                elements_by_id[seq_flow.element_id] = seq_flow

        for flow in self.diagram.seq_flows:
            src = flow.startRef
            trgt = flow.endRef

            outgoing.setdefault(src, []).append(trgt)
            incoming.setdefault(trgt, []).append(src)

        for element in self.diagram.events + self.diagram.tasks + self.diagram.gateways:
            pass

        start_events = [event for event in self.diagram.events if event.type == 'startEvent']

        if len(start_events) == 1:
            pass

        elif len(start_events) > 1:
            pass

        for gateway in self.diagram.gateways:
            pass

        for task in self.diagram.tasks:
            pass

        for event in [event for event in self.diagram.events if event.type == 'endEvent']:
            pass

        return domain, start_events

    def generate_pddl_problems(self, domain: pddl_classes.Domain, start_events: list[bpmn_elements.Event]) -> list[pddl_classes.Problem]:
        problems = []

        for count, start_event in enumerate(start_events):
            problems.append(pddl_classes.Problem(domain, start_event, count))

        return problems