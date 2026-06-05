from bpmn_core import bpmn_diagram
import xml.etree.ElementTree as ET
import os


class XMLCreator:
    BPMN = "http://www.omg.org/spec/BPMN/20100524/MODEL"
    BPMNDI = "http://www.omg.org/spec/BPMN/20100524/DI"
    DC = "http://www.omg.org/spec/DD/20100524/DC"
    DI = "http://www.omg.org/spec/DD/20100524/DI"

    def __init__(self, diagram: bpmn_diagram.Diagram):
        self.diagram = diagram
        self.incoming = {}
        self.outgoing = {}
        self.positions = {}

        ET.register_namespace("bpmn", self.BPMN)
        ET.register_namespace("bpmndi", self.BPMNDI)
        ET.register_namespace("dc", self.DC)
        ET.register_namespace("di", self.DI)

    def qname(self, namespace, tag) -> str:
        return f"{{{namespace}}}{tag}"

    def ref_id(self, ref):
        return ref.element_id if hasattr(ref, "element_id") else ref

    def all_flow_nodes(self):
        return (
            getattr(self.diagram, "tasks", [])
            + getattr(self.diagram, "events", [])
            + getattr(self.diagram, "gateways", [])
        )

    def ref_obj(self, ref):
        if hasattr(ref, "element_id"):
            return ref

        lookup = {element.element_id: element for element in self.all_flow_nodes()}
        return lookup[ref]

    def get_outgoing(self, element_id: str) -> list:
        return self.outgoing.get(element_id, [])

    def get_incoming(self, element_id: str) -> list:
        return self.incoming.get(element_id, [])

    def create_xml(self):
        output_folder = os.path.join(os.getcwd(), f"output/{self.diagram.name}")
        os.makedirs(output_folder, exist_ok=True)

        file_path = os.path.join(output_folder, f"{self.diagram.name}.bpmn")
        with open(file_path, "wb") as file:
            file.write(self.generate_xml_file())

    def generate_xml_file(self):

        root = ET.Element(
            self.qname(self.BPMN, "definitions"),
            {
                "id": "Definitions_1",
                "targetNamespace": "http://bpmn.io/schema/bpmn",
            },
        )

        ET.indent(root, space = "  ", level = 0)
        return ET.tostring(root, encoding = "UTF-8", xml_declaration = True)

    def add_process(self, root, process_id, process_name=None):
        attributes = {
            "id": process_id,
            "isExecutable": "true",
        }

        if process_name is not None:
            attributes["name"] = process_name

        return ET.SubElement(root, self.qname(self.BPMN, "process"), attributes)

    def add_participant(self, collaboration, pool):
        attributes = {
            "id": pool.element_id,
            "processRef": pool.process_id,
        }

        if getattr(pool, "label", None) is not None:
            attributes["name"] = pool.label

        ET.SubElement(
            collaboration,
            self.qname(self.BPMN, "participant"),
            attributes,
        )

    def add_lane_set(self, process, swimlanes):
        if not swimlanes:
            return

        lane_set = ET.SubElement(
            process,
            self.qname(self.BPMN, "laneSet"),
            {"id": self.diagram.generate_unique_id("LaneSet")},
        )

        for swimlane in swimlanes:
            attributes = {"id": swimlane.element_id}

            if getattr(swimlane, "label", None) is not None:
                attributes["name"] = swimlane.label

            lane = ET.SubElement(
                lane_set,
                self.qname(self.BPMN, "lane"),
                attributes,
            )

            for element in getattr(swimlane, "lane_elements", []) or []:
                flow_node_ref = ET.SubElement(lane, self.qname(self.BPMN, "flowNodeRef"))
                flow_node_ref.text = element.element_id

    def add_bpmn_element(self, process, element, tag):
        attributes = {"id": element.element_id}

        if getattr(element, "label", None) is not None:
            attributes["name"] = element.label

        if element.is_event() and element.type in [
            "messageCatchEvent",
            "timerCatchEvent",
            "conditionalCatchEvent",
        ]:
            tag = "intermediateCatchEvent"

        xml_element = ET.SubElement(process, self.qname(self.BPMN, tag), attributes)

        for incoming in self.get_incoming(element.element_id):
            incoming_element = ET.SubElement(xml_element, self.qname(self.BPMN, "incoming"))
            incoming_element.text = incoming.element_id

        for outgoing in self.get_outgoing(element.element_id):
            outgoing_element = ET.SubElement(xml_element, self.qname(self.BPMN, "outgoing"))
            outgoing_element.text = outgoing.element_id

        if not element.is_event():
            return

        if element.type == "messageCatchEvent":
            ET.SubElement(
                xml_element,
                self.qname(self.BPMN, "messageEventDefinition"),
                {"id": self.diagram.generate_unique_id("MessageEventDefinition")},
            )
        elif element.type == "timerCatchEvent":
            ET.SubElement(
                xml_element,
                self.qname(self.BPMN, "timerEventDefinition"),
                {"id": self.diagram.generate_unique_id("TimerEventDefinition")},
            )
        elif element.type == "conditionalCatchEvent":
            ET.SubElement(
                xml_element,
                self.qname(self.BPMN, "conditionalEventDefinition"),
                {"id": self.diagram.generate_unique_id("ConditionalEventDefinition")},
            )

    def add_sequence_flow(self, process, flow):
        attributes = {
            "id": flow.element_id,
            "sourceRef": self.ref_id(flow.startRef),
            "targetRef": self.ref_id(flow.endRef),
        }

        if getattr(flow, "label", None):
            attributes["name"] = flow.label

        ET.SubElement(process, self.qname(self.BPMN, "sequenceFlow"), attributes)

    def add_message_flow(self, collaboration, flow):
        attributes = {
            "id": flow.element_id,
            "sourceRef": self.ref_id(flow.startRef),
            "targetRef": self.ref_id(flow.endRef),
        }

        if getattr(flow, "label", None) is not None:
            attributes["name"] = flow.label

        ET.SubElement(collaboration, self.qname(self.BPMN, "messageFlow"), attributes)

    def create_diagram_layout(self, root, plane_element_id=None):
        diagram = ET.SubElement(
            root,
            self.qname(self.BPMNDI, "BPMNDiagram"),
            {"id": "BPMNDiagram_1"},
        )

        plane = ET.SubElement(
            diagram,
            self.qname(self.BPMNDI, "BPMNPlane"),
            {
                "id": "BPMNPlane_1",
                "bpmnElement": plane_element_id or self.diagram.id,
            },
        )