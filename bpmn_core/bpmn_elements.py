import random
import string
from enum import Enum

unique_ids = []
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
    """
    Supported BPMN event types.
    """

    startEvent = "startEvent"
    endEvent = "endEvent"
    intermediateCatchEvent = "intermediateCatchEvent"
    messageCatchEvent = "messageCatchEvent"
    timerCatchEvent = "timerCatchEvent"
    conditionalCatchEvent = "conditionalCatchEvent"

class gateway_type(Enum):
    """
    Supported BPMN gateway types.
    """

    inclusiveGateway = "inclusiveGateway"
    exclusiveGateway = "exclusiveGateway"
    parallelGateway = "parallelGateway"
    eventBasedGateway = "eventBasedGateway"

class task_type(Enum):
    """
    Supported BPMN task types.
    """

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
        super().__init__(label, element_id, "Pool")
        self.diagram = diagram
        self.process_id = diagram.generate_unique_id("Process") if diagram else None
        self.swimlanes = []

    def add_swimlane(self, label: str, element_id: str = None):
        """
        Add a swimlane to the BPMN pool.

        Args:
            label: The name of the swimlane.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created Swimlane object.
        """
        swimlane = Swimlane(label, element_id, self.diagram, self)
        self.swimlanes.append(swimlane)
        self.diagram.swimlanes.append(swimlane)

        return swimlane

class Swimlane(Element):

    def __init__(self, label: str, element_id: str = None, diagram = None, pool = None):
        super().__init__(label, element_id)
        self.diagram = diagram
        self.pool = pool
        self.lane_elements = []

    def add_task(self, label: str, type: str, element_id: str = None):
        """
        Add a task to the BPMN pool.

        Args:
            label: The name of the task.
            type: BPMN task type.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created Task object.
        """
        task = Task(label, element_id, type)
        self.diagram.tasks.append(task)
        self.lane_elements.append(task)

        return task

    def add_event(self, label: str, type: str, element_id: str = None):
        """
        Add an event to the BPMN pool.

        Args:
            label: The name of the event.
            type: BPMN event type.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created Event object.
        """
        event = Event(label, element_id, type)
        self.diagram.events.append(event)
        self.lane_elements.append(event)

        return event

    def add_gateway(self, label: str, type: str, element_id: str = None):
        """
        Add a gateway to the BPMN pool.

        Args:
            label: The name of the gateway.
            type: BPMN gateway type.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created Gateway object.
        """
        gateway = Gateway(label, element_id, type)
        self.diagram.gateways.append(gateway)
        self.lane_elements.append(gateway)

        return gateway

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

    def __init__(self, label: str, element_id: str, startRef: Element, endRef: Element):

        if not isinstance(startRef, Element) or not isinstance(endRef, Element):
            raise TypeError(
                "startRef and endRef must be Element objects, not id strings."
            )

        super().__init__(label, element_id)
        self.startRef = startRef
        self.endRef = endRef

class MessageFlow(Element):

    def __init__(self, label: str, element_id: str, startRef: Element, endRef: Element):

        if not isinstance(startRef, Element) or not isinstance(endRef, Element):
            raise TypeError(
                "startRef and endRef must be Element objects, not id strings."
            )
        
        super().__init__(label, element_id)
        self.startRef = startRef
        self.endRef = endRef