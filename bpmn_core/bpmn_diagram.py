# Create bpmn python objects 'manually' with a BPMN Diagram object
# From the python objects create pddl files or bpmn xml files

from bpmn_core import bpmn_elements

class BPMNDiagram:
    
    def __init__(self, name: str):
        self.name = name
        self.pools = []
        self.swimlanes = []
        self.tasks = []
        self.events = []
        self.gateways = []
        self.seq_flows = []
        self.msg_flows = []

    def get_elements(self) -> list[bpmn_elements.BPMNElement]:
        return self.pools + self.swimlanes + self.tasks + self.events + self.gateways + self.seq_flows + self.msg_flows

    def add_pool(self, label: str, element_id: str):
        pool = bpmn_elements.Pool(label, element_id)
        self.pools.append(pool)

    def add_swimlane(self, label: str, element_id: str):
        swimlane = bpmn_elements.Swimlane(label, element_id)
        self.swimlanes.append(swimlane)

    def add_task(self, label: str, element_id: str, type: str):
        task = bpmn_elements.Task(label, element_id, type)
        self.tasks.append(task)

    def add_event(self, label: str, element_id: str, type: str):
        event = bpmn_elements.Event(label, element_id, type)
        self.events.append(event)

    def add_gateway(self, label: str, element_id: str, type: str):
        gateway = bpmn_elements.Gateway(label, element_id, type)
        self.gateways.append(gateway)

    def add_sequence_flow(self, label: str, element_id: str, startRef: str, endRef: str):
        seq_flow = bpmn_elements.SequenceFlow(label, element_id, startRef, endRef)
        self.seq_flows.append(seq_flow)

    def add_message_flow(self, label: str, element_id: str, startRef: str, endRef: str):
        msg_flow = bpmn_elements.MessageFlow(label, element_id, startRef, endRef)
        self.msg_flows.append(msg_flow)

    def print_elements(self):
        elements = self.get_elements()
        for element in elements:
            print(element)