import random
import string
from enum import Enum

# TODO:
# type capalization (inconsistent)

unique_ids = [None]
super_type_map = {
    "Pool" : "Participant",
    "Swimlane" : "Lane",
    "startEvent" : "StartEvent",
    "endEvent" : "EndEvent",
    "intermediateCatchEvent" : "IntermediateCatchEvent",
    "inclusiveGateway" : "InclusiveGateway",
    "exclusiveGateway" : "ExclusiveGateway",
    "parallelGateway" : "ParallelGateway",
    "eventBasedGateway" : "EventBasedGateway"
}

class event_type(Enum):
    startEvent = "startEvent"
    endEvent = "endEvent"
    intermediateCatchEvent = "intermediateCatchEvent"

class gateway_type(Enum):
    inclusiveGateway = "inclusiveGateway"
    exclusiveGateway = "exclusiveGateway"
    parallelGateway = "parallelGateway"
    eventBasedGateway = "eventBasedGateway"

class task_type(Enum):
    task = "task"
    userTask = "userTask"
    serviceTask = "serviceTask"
    manualTask = "manualTask"
    scriptTask = "scriptTask"
    sendTask = "sendTask"
    recieveTask = "recieveTask"
    businessRuleTask = "businessRuleTask"

class Element:

    def __init__(self, label: str, element_id: str = None, element_type: str = None):
        self.label = label

        super_type = super_type_map.get(element_type, type(self).__name__)

        if element_id is None or element_id in unique_ids:
            element_id = self.generate_unique_id(super_type)

        self.element_id = element_id
        unique_ids.append(element_id)

    def generate_unique_id(self, prefix: str):
        element_id = f"{prefix}_" + "".join(
            random.choices(string.ascii_letters + string.digits, k=7)
        )

        while element_id in unique_ids:
            element_id = f"{prefix}_" + "".join(
                random.choices(string.ascii_letters + string.digits, k=7)
            )

        return element_id

    def __str__(self):
        return f'{self.element_id} : {self.label}'
    
    def is_task(self):
        return isinstance(self, Task)
    
    def is_event(self):
        return isinstance(self, Event)
    
    def is_gateway(self):
        return isinstance(self, Gateway)
    
    def is_sequence_flow(self):
        return isinstance(self, SequenceFlow)

class Pool(Element):
    def __init__(self, label: str, element_id: str = None, diagram = None):
        super().__init__(label, element_id)
        self.swimlanes = []
        self.diagram = diagram

    def add_swimlane(self, label: str, element_id: str = None):
        swimlane = Swimlane(label, element_id, self.diagram)
        self.swimlanes.append(swimlane)

        return swimlane

class Swimlane(Element):

    def __init__(self, label: str, element_id: str = None, diagram = None):
        super().__init__(label, element_id)
        self.diagram = diagram

    def add_task(self, label: str, type: str, element_id: str = None):
        task = Task(label, element_id, type)
        self.diagram.tasks.append(task)

        return task

    def add_event(self, label: str, type: str, element_id: str = None):
        event = Event(label, element_id, type)
        self.diagram.events.append(event)

        return event

    def add_gateway(self, label: str, type: str, element_id: str = None):
        gateway = Gateway(label, element_id, type)
        self.diagram.gateways.append(gateway)

        return gateway

    def add_sequence_flow(self, startRef: str, endRef: str, label: str = None, element_id: str = None):
        seq_flow = SequenceFlow(label, element_id, startRef, endRef)
        self.diagram.seq_flows.append(seq_flow)

        return seq_flow

    def add_message_flow(self, startRef: str, endRef: str, label: str = None, element_id: str = None):
        msg_flow = MessageFlow(label, element_id, startRef, endRef)
        self.diagram.msg_flows.append(msg_flow)

        return msg_flow 

class Task(Element):

    def __init__(self, label: str, element_id: str, type: task_type):
        self.type = type.value
        super().__init__(label, element_id, self.type)

class Event(Element):

    def __init__(self, label: str, element_id: str, type: event_type):
        self.type = type.value
        super().__init__(label, element_id, self.type)

class Gateway(Element):

    def __init__(self, label: str, element_id: str, type: gateway_type):
        self.type = type.value
        super().__init__(label, element_id, self.type)

class SequenceFlow(Element):

    def __init__(self, label: str, element_id: str, startRef: str, endRef: str):
        super().__init__(label, element_id)
        self.startRef = startRef
        self.endRef = endRef

class MessageFlow(Element):

    def __init__(self, label: str, element_id: str, startRef: str, endRef: str):
        super().__init__(label, element_id)
        self.startRef = startRef
        self.endRef = endRef