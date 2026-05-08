# Create bpmn python objects 'manually' with a BPMN Diagram object
# From the python objects create pddl files or bpmn xml files

from bpmn_core import bpmn_elements
# enums or literals for type parameters?

class BPMNDiagram:
    
    def __init__(self, name: str):
        self.name = name
        self.swimlanes = []
        self.tasks = []
        self.events = []
        self.gateways = []
        self.sequences = []

    def add_swimlane(self, label: str = None):
        swimlane = bpmn_elements.Swimlane(label)
        self.swimlanes.append(swimlane)

    def add_task(self, type, label: str = None):
        task = bpmn_elements.Task(type, label)
        self.tasks.append(task)

    def add_event(self, type, label: str = None):
        event = bpmn_elements.Event(type, label)
        self.events.append(event)

    def add_gateway(self, type, label: str = None):
        gateway = bpmn_elements.Gateway(type, label)
        self.gateways.append(gateway)

    def connect(self, start: bpmn_elements.BPMNElement, end: bpmn_elements.BPMNElement, label: str = None):
        sequence = bpmn_elements.Sequence(start, end, label)
        self.sequences.append(sequence)