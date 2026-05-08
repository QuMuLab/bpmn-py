from bpmn_core import bpmn_diagram, bpmn_exporter

diagram = bpmn_diagram.BPMNDiagram()

swimlane = diagram.add_swimlane()
task = diagram.add_task()
event = diagram.add_event()

diagram.connect(task, event)

exporter = bpmn_exporter.BPMNExporter(diagram)
exporter.create_bpmn_xml()
exporter.create_pddl()

from xml_parser import bpmn_2_pddl

file_path = 'path/to/xml'
parser = bpmn_2_pddl.BPMNParser(file_path)

parser.parse()