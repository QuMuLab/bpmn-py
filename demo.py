# 1. "Manually" create bpmn in python then export to xml or pddl

from bpmn_core import bpmn_diagram, bpmn_exporter

# diagram = bpmn_diagram.Diagram("Example Diagram")

# swimlane = diagram.add_swimlane("test")
# task = diagram.add_task("placeholder")
# event = diagram.add_event("end")

# diagram.connect(task, event)

# exporter = bpmn_exporter.BPMNExporter(diagram)
# exporter.create_bpmn_xml()
# exporter.create_pddl()

# 2. Automatically create bpmn in python from xml file then export to pddl

from bpmn_xml_parser import bpmn_parser

file_path = "bpmn_diagrams/dispatch_of_goods.bpmn"

parser = bpmn_parser.BPMNParser(file_path)
diagram2 = parser.parse()

exporter2 = bpmn_exporter.BPMNExporter(diagram2)
exporter2.create_pddl()

# Test Area
# diagram2.print_elements()