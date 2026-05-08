# 'Manually' create bpmn in python then export to xml or pddl

from bpmn_core import bpmn_diagram, bpmn_exporter

diagram = bpmn_diagram.BPMNDiagram("Example Diagram")

swimlane = diagram.add_swimlane("test")
task = diagram.add_task("placeholder")
event = diagram.add_event("end")

diagram.connect(task, event)

exporter = bpmn_exporter.BPMNExporter(diagram)
exporter.create_bpmn_xml()
exporter.create_pddl()

# Automatically create bpmn in python from xml file then export to pddl

from xml_parser import bpmn_2_pddl

file_path = 'path/to/xml'

parser = bpmn_2_pddl.BPMNParser(file_path)
diagram2 = parser.parse()

exporter2 = bpmn_exporter.BPMNExporter(diagram2)
exporter2.create_pddl()