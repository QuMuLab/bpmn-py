from bpmn_core import bpmn_elements
from re import sub

class Diagram:
    
    def __init__(self, name: str):
        self.name = self.clean_name(name)
        self.pools = []
        self.swimlanes = []
        self.tasks = []
        self.events = []
        self.gateways = []
        self.seq_flows = []
        self.msg_flows = []

    def clean_name(self, name: str) -> str:
        return sub(r"[^a-zA-Z0-9_]", "_", name.lower())

    def get_elements(self) -> list[bpmn_elements.Element]:
        return self.pools + self.swimlanes + self.tasks + self.events + self.gateways + self.seq_flows + self.msg_flows

    def add_pool(self, label: str, element_id: str = None):
        pool = bpmn_elements.Pool(label, element_id, self)
        self.pools.append(pool)

        return pool

    def add_swimlane(self, label: str, element_id: str = None):
        swimlane = bpmn_elements.Swimlane(label, element_id)
        self.swimlanes.append(swimlane)

        return swimlane

    def add_task(self, label: str, type: bpmn_elements.task_type, element_id: str = None):
        task = bpmn_elements.Task(label, element_id, type)
        self.tasks.append(task)

        return task

    def add_event(self, label: str, type: bpmn_elements.event_type, element_id: str = None):
        event = bpmn_elements.Event(label, element_id, type)
        self.events.append(event)

        return event

    def add_gateway(self, label: str, type: bpmn_elements.gateway_type, element_id: str = None):
        gateway = bpmn_elements.Gateway(label, element_id, type)
        self.gateways.append(gateway)

        return gateway

    def add_sequence_flow(self, startRef: str, endRef: str, label: str = None, element_id: str = None):
        seq_flow = bpmn_elements.SequenceFlow(label, element_id, startRef, endRef)
        self.seq_flows.append(seq_flow)

        return seq_flow

    def add_message_flow(self, startRef: str, endRef: str, label: str = None, element_id: str = None):
        msg_flow = bpmn_elements.MessageFlow(label, element_id, startRef, endRef)
        self.msg_flows.append(msg_flow)

        return msg_flow

    def print_elements(self):
        elements = self.get_elements()
        for element in elements:
            print(element)