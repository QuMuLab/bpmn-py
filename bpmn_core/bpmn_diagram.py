# Create bpmn python objects 'manually'
# From the python objects create pddl files or bpmn xml files

import bpmn_elements

class BPMNDiagram:
    
    def __init__(self, name):
        self.name = name
        self.swimlanes = []
        self.tasks = []
        self.events = []
        self.gateways = []
        self.sequences = []

    def add_swimlane(self, name):
        pass

    def add_task(self, name):
        pass

    def add_event(self, name):
        pass

    def add_gateway(self, name):
        pass

    def connect(self, start, end, label = None):
        pass