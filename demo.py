# 1. Automatically create bpmn in python from xml file then export to pddl or xml

from bpmn_core import bpmn_diagram, bpmn_exporter
from bpmn_xml_parser import bpmn_parser, xml_creator

diagram_name = "order_pizza"
file_path = f"bpmn_diagrams/{diagram_name}.bpmn"

parser = bpmn_parser.BPMNParser(file_path)
diagram = parser.parse()

exporter = bpmn_exporter.BPMNExporter(diagram)
exporter.create_pddl()

exporter = xml_creator.XMLCreator(diagram)
exporter.create_xml()

# 2. "Manually" create bpmn in python then export to xml or pddl

from bpmn_core.bpmn_elements import event_type, gateway_type, task_type

diagram = bpmn_diagram.Diagram("Dispatch of Goods")
pool = diagram.add_pool("Computer Hardware Shop")

logistics = pool.add_swimlane("Logistics")
secretary = pool.add_swimlane("Secretary")
warehouse = pool.add_swimlane("Warehouse")

insure_parcel = logistics.add_task("Insure Parcel", task_type.userTask)

ship_goods = secretary.add_event("Ship Goods", event_type.startEvent)
parallel_split = secretary.add_gateway(None, gateway_type.parallelGateway)
clarify = secretary.add_task("Clarify shipment method", task_type.userTask)
special_sandling_split = secretary.add_gateway("Special sandling?", gateway_type.exclusiveGateway)
if_insurance_split = secretary.add_gateway("If insurance necessary", gateway_type.inclusiveGateway)
write_label = secretary.add_task("Write package label", task_type.userTask)
if_insurance_join = secretary.add_gateway(None, gateway_type.inclusiveGateway)
get_offers = secretary.add_task("Get 3 offers from logistic companies", task_type.userTask)
select_company = secretary.add_task("Select logistic company and place order", task_type.userTask)
special_sandling_join = secretary.add_gateway(None, gateway_type.exclusiveGateway)

package_goods = warehouse.add_task("Package Goods", task_type.userTask)
parallel_join = warehouse.add_gateway(None, gateway_type.parallelGateway)
prepare = warehouse.add_task("Prepare for picking up goods", task_type.userTask)
shipment_prepared = warehouse.add_event("Shipment prepared", event_type.endEvent)

diagram.add_sequence_flow(if_insurance_split, insure_parcel)
diagram.add_sequence_flow(insure_parcel, if_insurance_join)

diagram.add_sequence_flow(ship_goods, parallel_split)
diagram.add_sequence_flow(parallel_split, clarify)
diagram.add_sequence_flow(clarify, special_sandling_split)
diagram.add_sequence_flow(special_sandling_split, if_insurance_split)
diagram.add_sequence_flow(if_insurance_split, write_label)
diagram.add_sequence_flow(write_label, if_insurance_join)
diagram.add_sequence_flow(if_insurance_join, special_sandling_join)
diagram.add_sequence_flow(special_sandling_split, get_offers)
diagram.add_sequence_flow(get_offers, select_company)
diagram.add_sequence_flow(select_company, special_sandling_join)
diagram.add_sequence_flow(special_sandling_join, parallel_join)

diagram.add_sequence_flow(parallel_split, package_goods)
diagram.add_sequence_flow(package_goods, parallel_join)
diagram.add_sequence_flow(parallel_join, prepare)
diagram.add_sequence_flow(prepare, shipment_prepared)

diagram.print_elements()

exporter = bpmn_exporter.BPMNExporter(diagram)
exporter.create_pddl()

exporter = xml_creator.XMLCreator(diagram)
exporter.create_xml()