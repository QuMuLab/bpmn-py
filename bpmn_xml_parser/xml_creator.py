from bpmn_core import bpmn_diagram, bpmn_elements
import xml.etree.ElementTree as ET
import os

# TODO:
# Swimlanes / pools / message flows

class XMLCreator:
    
    BPMN = "http://www.omg.org/spec/BPMN/20100524/MODEL"
    BPMNDI = "http://www.omg.org/spec/BPMN/20100524/DI"
    DC = "http://www.omg.org/spec/DD/20100524/DC"
    DI = "http://www.omg.org/spec/DD/20100524/DI"

    def __init__(self, diagram: bpmn_diagram.Diagram):
        self.diagram = diagram

        ET.register_namespace("bpmn", self.BPMN)
        ET.register_namespace("bpmndi", self.BPMNDI)
        ET.register_namespace("dc", self.DC)
        ET.register_namespace("di", self.DI)

    def qname(self, namespace, tag) -> str:
        return f"{{{namespace}}}{tag}"
    
    def get_outgoing(self, element_id: str) -> list:
        return self.outgoing.get(element_id, [])
    
    def get_incoming(self, element_id: str) -> list:
        return self.incoming.get(element_id, [])

    def create_xml(self):
        output_folder = os.path.join(os.getcwd(), f"output/{self.diagram.name}")
        os.makedirs(output_folder, exist_ok = True)

        file_path = os.path.join(output_folder, f"{self.diagram.name}.bpmn")
        with open(file_path, "wb") as file:
            file.write(self.generate_xml_file())

    def generate_xml_file(self):
        self.incoming = {}
        self.outgoing = {}

        for flow in self.diagram.seq_flows:
            source = flow.startRef
            target = flow.endRef

            self.outgoing.setdefault(source.element_id, []).append(flow)
            self.incoming.setdefault(target.element_id, []).append(flow)

        root = ET.Element(
            self.qname(self.BPMN, "definitions"),
            {
                "id": "Definitions_1",
                "targetNamespace": "http://bpmn.io/schema/bpmn"
            }
        )

        process = ET.SubElement(
            root,
            self.qname(self.BPMN, "process"),
            {
                "id": self.diagram.id,
                "name": self.diagram.name,
                "isExecutable": "true"
            }
        )

        for element in self.diagram.tasks + self.diagram.events + self.diagram.gateways:
            self.add_bpmn_element(process, element, element.type)

        for flow in self.diagram.seq_flows:
            self.add_bpmn_flow(process, flow)

        self.create_diagram_layout(root)

        ET.indent(root, space = "  ", level = 0)
        return ET.tostring(
            root,
            encoding = "UTF-8",
            xml_declaration = True,
        )
    
    def add_bpmn_element(self, process, element, tag):
        attributes = {"id": element.element_id}

        if element.label is not None:
            attributes["name"] = element.label

        if element.is_event():
            if element.type == "messageCatchEvent":
                tag = "intermediateCatchEvent"
            elif element.type == "timerCatchEvent":
                tag = "intermediateCatchEvent"
            elif element.type == "conditionalCatchEvent":
                tag = "intermediateCatchEvent"

        xml_element = ET.SubElement(
            process,
            self.qname(self.BPMN, tag),
            attributes
        )

        for incoming in self.get_incoming(element.element_id):
            incoming_element = ET.SubElement(xml_element, self.qname(self.BPMN, "incoming"))
            incoming_element.text = incoming.element_id

        for outgoing in self.get_outgoing(element.element_id):
            outgoing_element = ET.SubElement(xml_element, self.qname(self.BPMN, "outgoing"))
            outgoing_element.text = outgoing.element_id

        if element.is_event():
            if element.type == "messageCatchEvent":
                ET.SubElement(
                    xml_element,
                    self.qname(self.BPMN, "messageEventDefinition"),
                    {"id": self.diagram.generate_unique_id("MessageEventDefinition")}
                )

            elif element.type == "timerCatchEvent":
                ET.SubElement(
                    xml_element,
                    self.qname(self.BPMN, "timerEventDefinition"),
                    {"id": self.diagram.generate_unique_id("TimerEventDefinition")}
                )

            elif element.type == "conditionalCatchEvent":
                ET.SubElement(
                    xml_element,
                    self.qname(self.BPMN, "conditionalEventDefinition"),
                    {"id": self.diagram.generate_unique_id("ConditionalEventDefinition")}
                )

    def add_bpmn_flow(self, process, flow):
        attributes = {
            "id": flow.element_id,
            "sourceRef": flow.startRef.element_id,
            "targetRef": flow.endRef.element_id
        }

        if flow.label is not None:
            attributes["name"] = flow.label

        ET.SubElement(
            process,
            self.qname(self.BPMN, "sequenceFlow"),
            attributes
        )

    def create_diagram_layout(self, root):
        diagram = ET.SubElement(
            root, 
            self.qname(self.BPMNDI, "BPMNDiagram"), 
            {"id": "BPMNDiagram_1"}
        )

        plane = ET.SubElement(
            diagram, 
            self.qname(self.BPMNDI, "BPMNPlane"), 
            {
                "id": "BPMNPlane_1",
                "bpmnElement": self.diagram.id
            }
        )

        self.positions = {}

        elements = self.diagram.events + self.diagram.tasks + self.diagram.gateways

        x_start = 150
        y_start = 160
        x_gap = 220
        y_gap = 140

        levels = {}
        visited = set()

        def assign_level(element, level):
            if element.element_id in visited:
                return

            visited.add(element.element_id)
            levels.setdefault(level, []).append(element)

            for flow in self.get_outgoing(element.element_id):
                assign_level(flow.endRef, level + 1)

        starts = [e for e in elements if not self.get_incoming(e.element_id)]

        for start in starts:
            assign_level(start, 0)

        for element in elements:
            if element.element_id not in visited:
                assign_level(element, 0)

        for level, level_elements in levels.items():
            x = x_start + level * x_gap

            for row, element in enumerate(level_elements):
                width, height = self.get_element_size(element)

                row_center_y = y_start + row * y_gap
                y = row_center_y - height // 2

                self.positions[element.element_id] = {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "row": row,
                    "level": level,
                    "center_y": row_center_y
                }

                shape = ET.SubElement(
                    plane, 
                    self.qname(self.BPMNDI, "BPMNShape"), 
                    {
                        "id": f"{element.element_id}_di",
                        "bpmnElement": element.element_id
                    }
                )

                ET.SubElement(
                    shape, 
                    self.qname(self.DC, "Bounds"), 
                    {
                        "x": str(x),
                        "y": str(y),
                        "width": str(width),
                        "height": str(height)
                    }
                )

        for flow in self.diagram.seq_flows:
            self.add_diagram_edge(plane, flow)

    def get_element_size(self, element):

        if element.is_event():
            return 36, 36

        if element.is_gateway():
            return 50, 50

        return 100, 80
    
    def add_diagram_edge(self, plane, flow):
        source = self.positions[flow.startRef.element_id]
        target = self.positions[flow.endRef.element_id]

        edge = ET.SubElement(
            plane, 
            self.qname(self.BPMNDI, "BPMNEdge"), 
            {
                "id": f"{flow.element_id}_di",
                "bpmnElement": flow.element_id
            }
        )

        source_center_x = source["x"] + source["width"] // 2
        source_center_y = source["y"] + source["height"] // 2
        target_center_x = target["x"] + target["width"] // 2
        target_center_y = target["y"] + target["height"] // 2

        if source["row"] == target["row"]:

            if target["level"] < source["level"]:

                source_top_x = source_center_x
                source_top_y = source["y"]

                target_top_x = target_center_x
                target_top_y = target["y"]

                mid_y = min(source_top_y, target_top_y) - 70

                waypoints = [
                    (source_top_x, source_top_y),
                    (source_top_x, mid_y),
                    (target_top_x, mid_y),
                    (target_top_x, target_top_y)
                ]

            else:
                waypoints = [
                    (source["x"] + source["width"], source_center_y),
                    (target["x"], target_center_y)
                ]

        elif target["row"] > source["row"]:
            source_x = source_center_x
            source_y = source["y"] + source["height"]

            target_x = target_center_x
            target_y = target["y"]

            mid_y = (source_y + target_y) // 2

            waypoints = [
                (source_x, source_y),
                (source_x, mid_y),
                (target_x, mid_y),
                (target_x, target_y)
            ]

        else:
            source_x = source_center_x
            source_y = source["y"]

            target_x = target_center_x
            target_y = target["y"] + target["height"]

            mid_y = (source_y + target_y) // 2

            waypoints = [
                (source_x, source_y),
                (source_x, mid_y),
                (target_x, mid_y),
                (target_x, target_y)
            ]

        for x, y in waypoints:
            ET.SubElement(
                edge, 
                self.qname(self.DI, "waypoint"), 
                {
                    "x": str(x),
                    "y": str(y)
                }
            )