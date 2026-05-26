from bpmn_core import bpmn_diagram, bpmn_elements
from textwrap import indent, dedent
import os

class XMLCreator:
    
    def __init__(self, diagram: bpmn_diagram.Diagram):
        self.diagram = diagram

    def create_xml(self):
        output_folder = os.path.join(os.getcwd(), f"output/{self.diagram.name}")
        os.makedirs(output_folder, exist_ok = True)

        file_path = os.path.join(output_folder, f"{self.diagram.name}.bpmn")
        with open(file_path, "w") as file:
            file.write(self.generate_xml_file())

    def generate_xml_file(self):
        template = """
        
        """

        return dedent(template).strip().format(

        )