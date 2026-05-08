# Create python bpmn objects from an xml file
# From the python objects create pddl files or bpmn xml files

from bpmn_core import bpmn_diagram

class BPMNParser:
    
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self) -> bpmn_diagram.BPMNDiagram:
        pass