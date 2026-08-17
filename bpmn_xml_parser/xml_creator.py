from bpmn_core import bpmn_diagram
import xml.etree.ElementTree as ET
import os

class XMLCreator:
    """
    Creates a BPMN xml file from a diagram object.

    Args:
        diagram: The diagram object you wish to create the xml for.
    """
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
        """
        Create the corresponding xml for the diagram.
        """
        output_folder = os.path.join(os.getcwd(), f"output/{self.diagram.name}")
        os.makedirs(output_folder, exist_ok = True)

        file_path = os.path.join(output_folder, f"{self.diagram.name}.bpmn")
        with open(file_path, "wb") as file:
            file.write(self.generate_xml_file())

    def generate_xml_file(self):
        self.incoming = {}
        self.outgoing = {}

        for flow in self.diagram.seq_flows:
            source_id = flow.startRef.element_id
            target_id = flow.endRef.element_id

            self.outgoing.setdefault(source_id, []).append(flow)
            self.incoming.setdefault(target_id, []).append(flow)

        root = ET.Element(
            self.qname(self.BPMN, "definitions"),
            {
                "id": "Definitions_1",
                "targetNamespace": "http://bpmn.io/schema/bpmn"
            }
        )

        collaboration_id = None

        if self.diagram.pools:
            collaboration_id = self.diagram.generate_unique_id("Collaboration")
            collaboration = ET.SubElement(
                root,
                self.qname(self.BPMN, "collaboration"),
                {"id": collaboration_id}
            )

            for pool in self.diagram.pools:
                attributes = {
                    "id" : pool.element_id,
                    "processRef" : self.diagram.id
                 }

                if pool.label:
                    attributes["name"] = pool.label

                ET.SubElement(
                    collaboration,
                    self.qname(self.BPMN, "participant"),
                    attributes
                )

            for flow in self.diagram.msg_flows:
                self.add_message_flow(collaboration, flow)

        process = ET.SubElement(
            root,
            self.qname(self.BPMN, "process"),
            {
                "id": self.diagram.id,
                "name": self.diagram.name,
                "isExecutable": "true"
            }
        )

        self.add_lane_set(process)

        for element in self.diagram.tasks + self.diagram.events + self.diagram.gateways:
            self.add_bpmn_element(process, element, element.type)

        for flow in self.diagram.seq_flows:
            self.add_sequence_flow(process, flow)

        self.create_diagram_layout(root, collaboration_id)

        ET.indent(root, space = "  ", level = 0)
        return ET.tostring(
            root,
            encoding = "UTF-8",
            xml_declaration = True,
        )
    
    def add_lane_set(self, process):
        if not self.diagram.swimlanes:
            return
        
        lane_set = ET.SubElement(
            process,
            self.qname(self.BPMN, "laneSet"),
            {"id": self.diagram.generate_unique_id("LaneSet")}
        )

        for lane in self.diagram.swimlanes:
            attributes = {"id": lane.element_id}

            if lane.label is not None:
                attributes["name"] = lane.label

            lane_element = ET.SubElement(
                lane_set,
                self.qname(self.BPMN, "lane"),
                attributes
            )

            for node in lane.lane_elements:
                flow_node_ref = ET.SubElement(
                    lane_element,
                    self.qname(self.BPMN, "flowNodeRef")
                )
                flow_node_ref.text = node.element_id
    
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
            incoming_element = ET.SubElement(
                xml_element, 
                self.qname(self.BPMN, "incoming")
            )
            incoming_element.text = incoming.element_id

        for outgoing in self.get_outgoing(element.element_id):
            outgoing_element = ET.SubElement(
                xml_element, 
                self.qname(self.BPMN, "outgoing")
            )
            outgoing_element.text = outgoing.element_id

        if element.is_event():
            if element.type == "messageCatchEvent":
                ET.SubElement(
                    xml_element,
                    self.qname(self.BPMN, "messageEventDefinition"),
                    {
                        "id": self.diagram.generate_unique_id("MessageEventDefinition")
                    }
                )

            elif element.type == "timerCatchEvent":
                ET.SubElement(
                    xml_element,
                    self.qname(self.BPMN, "timerEventDefinition"),
                    {
                        "id": self.diagram.generate_unique_id("TimerEventDefinition")
                    }
                )

            elif element.type == "conditionalCatchEvent":
                ET.SubElement(
                    xml_element,
                    self.qname(self.BPMN, "conditionalEventDefinition"),
                    {
                        "id": self.diagram.generate_unique_id("ConditionalEventDefinition")
                    }
                )

    def add_sequence_flow(self, process, flow):
        attributes = {
            "id": flow.element_id,
            "sourceRef": flow.startRef.element_id,
            "targetRef": flow.endRef.element_id
        }

        if flow.label:
            attributes["name"] = flow.label

        ET.SubElement(
            process,
            self.qname(self.BPMN, "sequenceFlow"),
            attributes
        )

    def add_message_flow(self, collaboration, flow):
        attributes = {
            "id": flow.element_id,
            "sourceRef": flow.startRef.element_id,
            "targetRef": flow.endRef.element_id
        }

        if flow.label:
            attributes["name"] = flow.label

        ET.SubElement(
            collaboration,
            self.qname(self.BPMN, "messageFlow"),
            attributes
        )

    def create_diagram_layout(self, root, collaboration_id=None):
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
                "bpmnElement": collaboration_id or self.diagram.id
            }
        )

        self.positions = {}

        x_start = 180
        y_start = 120
        x_gap = 220
        min_lane_height = 160
        lane_padding_top = 40
        lane_padding_bottom = 40
        row_gap = 100
        pool_gap = 80

        current_y = y_start
        pools = self.diagram.pools if self.diagram.pools else [None]

        for pool in pools:
            lanes = getattr(pool, "swimlanes", None) if pool else self.diagram.swimlanes

            if not lanes:
                lanes = self.diagram.swimlanes

            if not lanes:
                lanes = [None]

            lane_layouts = []
            pool_height = 0

            for lane_index, lane in enumerate(lanes):
                elements = lane.lane_elements if lane else (
                    self.diagram.events + self.diagram.tasks + self.diagram.gateways
                )

                levels = {}
                visited = set()

                def assign_level(element, level):
                    if element.element_id in visited:
                        return
                    
                    visited.add(element.element_id)
                    levels.setdefault(level, []).append(element)

                    for flow in self.get_outgoing(element.element_id):
                        target = flow.endRef

                        if target in elements:
                            assign_level(target, level + 1)

                starts = [
                    element for element in elements
                    if not self.get_incoming(element.element_id)
                ]

                for start in starts:
                    assign_level(start, 0)

                for element in elements:
                    if element.element_id not in visited:
                        assign_level(element, 0)

                max_level_count = max((len(v) for v in levels.values()), default = 1)
                lane_height = max(
                    min_lane_height,
                    lane_padding_top + lane_padding_bottom + ((max_level_count - 1) * row_gap) + 80
                )

                lane_layouts.append((lane, levels, lane_height))
                pool_height += lane_height

            pool_y = current_y

            max_level = max(
                (max(levels.keys(), default = 0) for _, levels, _ in lane_layouts),
                default=0
            )

            content_width = x_start + (max_level * x_gap) + 220
            pool_width = max(1250, content_width)
            lane_width = pool_width - 30

            if pool is not None:
                self.add_shape(plane, pool.element_id, 60, pool_y, pool_width, pool_height)

            lane_y = pool_y

            for lane_index, (lane, levels, lane_height) in enumerate(lane_layouts):
                if lane is not None:
                    self.add_shape(plane, lane.element_id, 90, lane_y, lane_width, lane_height)

                lane_center_y = lane_y + lane_height / 2

                for level, level_elements in levels.items():
                    x = x_start + level * x_gap

                    total_stack_height = (len(level_elements) - 1) * row_gap
                    start_center_y = lane_center_y - total_stack_height / 2

                    for row, element in enumerate(level_elements):
                        width, height = self.get_element_size(element)

                        center_y = start_center_y + row * row_gap
                        y = center_y - height / 2

                        self.positions[element.element_id] = {
                            "x": x,
                            "y": y,
                            "width": width,
                            "height": height,
                            "row": lane_index,
                            "level": level,
                            "center_x": x + width / 2,
                            "center_y": y + height / 2
                        }

                        self.add_shape(plane, element.element_id, x, y, width, height)

                lane_y += lane_height

            current_y += pool_height + pool_gap

        for flow in self.diagram.seq_flows:
            self.add_diagram_edge(plane, flow)

        for flow in self.diagram.msg_flows:
            self.add_diagram_edge(plane, flow)

    def add_shape(self, plane, element_id, x, y, width, height):
        attributes = {
            "id": f"{element_id}_di",
            "bpmnElement": element_id
        }

        if element_id in [pool.element_id for pool in self.diagram.pools]:
            attributes["isHorizontal"] = "true"

        if element_id in [lane.element_id for lane in self.diagram.swimlanes]:
            attributes["isHorizontal"] = "true"

        shape = ET.SubElement(
            plane,
            self.qname(self.BPMNDI, "BPMNShape"),
            attributes
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

    def get_element_size(self, element):

        if element.is_event():
            return 36, 36

        if element.is_gateway():
            return 50, 50

        return 100, 80
    
    def add_diagram_edge(self, plane, flow):
        source_id = flow.startRef.element_id
        target_id = flow.endRef.element_id

        source = self.positions[source_id]
        target = self.positions[target_id]

        edge = ET.SubElement(
            plane,
            self.qname(self.BPMNDI, "BPMNEdge"),
            {
                "id": f"{flow.element_id}_di",
                "bpmnElement": flow.element_id
            }
        )

        source_obj = flow.startRef
        outgoing_flows = self.get_outgoing(source_id)

        sx = source["center_x"]
        sy = source["center_y"]
        tx = target["center_x"]
        ty = target["center_y"]

        start = (source["x"] + source["width"], sy)
        end = (target["x"], ty)

        if source_obj.is_gateway() and len(outgoing_flows) > 1:
            sorted_flows = sorted(
                outgoing_flows,
                key = lambda f: self.positions[self.ref_id(f.endRef)]["center_y"]
            )

            flow_index = sorted_flows.index(flow)

            if len(sorted_flows) == 2:
                if flow_index == 0:
                    start = (sx, source["y"])
                else:
                    start = (sx, source["y"] + source["height"])

            elif len(sorted_flows) >= 3:
                if flow_index == 0:
                    start = (sx, source["y"])
                elif flow_index == 1:
                    start = (source["x"] + source["width"], sy)
                else:
                    start = (sx, source["y"] + source["height"])

        if source["row"] == target["row"]:
            mid_x = (start[0] + end[0]) / 2

            waypoints = [
                start,
                (mid_x, start[1]),
                (mid_x, end[1]),
                end
            ]

        else:
            if target["row"] > source["row"]:
                end = (tx, target["y"])
            else:
                end = (tx, target["y"] + target["height"])

            mid_y = (start[1] + end[1]) / 2

            waypoints = [
                start,
                (start[0], mid_y),
                (end[0], mid_y),
                end
            ]

        for x, y in waypoints:
            ET.SubElement(
                edge,
                self.qname(self.DI, "waypoint"),
                {
                    "x": str(round(x, 2)),
                    "y": str(round(y, 2))
                }
            )