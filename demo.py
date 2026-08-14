from bpmn_py import Diagram, BPMNExporter, BPMNParser, XMLCreator

# 1. Automatically create bpmn in python from xml file then export to pddl or xml

diagram_name = "order_pizza"
file_path = f"examples/{diagram_name}.bpmn"

parser = BPMNParser(file_path)
diagram = parser.parse()

exporter = BPMNExporter(diagram)
exporter.create_pddl()

exporter = XMLCreator(diagram)
exporter.create_xml()

# 2. "Manually" create bpmn in python then export to xml or pddl

from bpmn_py import userTask, startEvent, endEvent, parallelGateway, exclusiveGateway, inclusiveGateway

diagram = Diagram("Dispatch of Goods")
pool = diagram.add_pool("Computer Hardware Shop")

logistics = pool.add_swimlane("Logistics")
secretary = pool.add_swimlane("Secretary")
warehouse = pool.add_swimlane("Warehouse")

insure_parcel = logistics.add_task("Insure Parcel", userTask)

ship_goods = secretary.add_event("Ship Goods", startEvent)
parallel_split = secretary.add_gateway(None, parallelGateway)
clarify = secretary.add_task("Clarify shipment method", userTask)
special_sandling_split = secretary.add_gateway("Special sandling?", exclusiveGateway)
if_insurance_split = secretary.add_gateway("If insurance necessary", inclusiveGateway)
write_label = secretary.add_task("Write package label", userTask)
if_insurance_join = secretary.add_gateway(None, inclusiveGateway)
get_offers = secretary.add_task("Get 3 offers from logistic companies", userTask)
select_company = secretary.add_task("Select logistic company and place order", userTask)
special_sandling_join = secretary.add_gateway(None, exclusiveGateway)

package_goods = warehouse.add_task("Package Goods", userTask)
parallel_join = warehouse.add_gateway(None, parallelGateway)
prepare = warehouse.add_task("Prepare for picking up goods", userTask)
shipment_prepared = warehouse.add_event("Shipment prepared", endEvent)

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

exporter = BPMNExporter(diagram)
exporter.create_pddl()

exporter = XMLCreator(diagram)
exporter.create_xml()

# 3. Automatically create bpmn in python from xml file then manually edit it before exporting to pddl or xml