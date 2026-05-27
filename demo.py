# 1. Automatically create bpmn in python from xml file then export to pddl

from bpmn_core import bpmn_diagram, bpmn_exporter
from bpmn_xml_parser import bpmn_parser

file_path = "bpmn_diagrams/dispatch_of_goods.bpmn"

parser = bpmn_parser.BPMNParser(file_path)
diagram = parser.parse()

exporter = bpmn_exporter.BPMNExporter(diagram)
exporter.create_pddl()

#diagram.print_elements()

# 2. "Manually" create bpmn in python then export to xml or pddl

from bpmn_xml_parser import xml_creator
from bpmn_core.bpmn_elements import event_type, gateway_type, task_type

#diagram = bpmn_diagram.Diagram("Example Order Pizza")

pool = diagram.add_pool(None)
swimlane = pool.add_swimlane(None)

pizza_wanted = swimlane.add_event("Pizza Wanted", event_type.startEvent)
order_pizza = swimlane.add_task("Order Pizza", task_type.userTask)
event_gateway_1 = swimlane.add_gateway(None, gateway_type.eventBasedGateway)

pizza_recieved = swimlane.add_event("Pizza Recieved", event_type.intermediateCatchEvent)
eat_pizza = swimlane.add_task("Eat Pizza", task_type.userTask)
pizza_eaten = swimlane.add_event("Pizza Eaten", event_type.endEvent)

thirty_mins = swimlane.add_event("30 Minutes", event_type.intermediateCatchEvent)
complain = swimlane.add_task("Complain to Delivery Service", task_type.userTask)
event_gateway_2 = swimlane.add_gateway(None, gateway_type.eventBasedGateway)

pizza_recieved_2 = swimlane.add_event("Pizza Recieved", event_type.intermediateCatchEvent)

twenty_mins = swimlane.add_event("20 Minutes", event_type.intermediateCatchEvent)
cancel_order = swimlane.add_task("Cancel Pizza", task_type.userTask)
order_cancelled = swimlane.add_event("Order Cancelled", event_type.endEvent)

swimlane.add_sequence_flow(pizza_wanted, order_pizza)
swimlane.add_sequence_flow(order_pizza, event_gateway_1)
swimlane.add_sequence_flow(event_gateway_1, pizza_recieved)
swimlane.add_sequence_flow(pizza_recieved, eat_pizza)
swimlane.add_sequence_flow(eat_pizza, pizza_eaten)
swimlane.add_sequence_flow(event_gateway_1, thirty_mins)
swimlane.add_sequence_flow(thirty_mins, complain)
swimlane.add_sequence_flow(complain, event_gateway_2)
swimlane.add_sequence_flow(event_gateway_2, pizza_recieved_2)
swimlane.add_sequence_flow(pizza_recieved_2, eat_pizza)
swimlane.add_sequence_flow(event_gateway_2, twenty_mins)
swimlane.add_sequence_flow(twenty_mins, cancel_order)
swimlane.add_sequence_flow(cancel_order, order_cancelled)

#diagram.print_elements()

exporter = bpmn_exporter.BPMNExporter(diagram)
#exporter.create_pddl()

exporter = xml_creator.XMLCreator(diagram)
#exporter.create_xml()