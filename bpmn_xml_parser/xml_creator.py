from bpmn_core import bpmn_diagram
import xml.etree.ElementTree as ET
import os

X_START = 180
Y_START = 120
X_GAP = 200
ROW_GAP = 110
MIN_LANE_HEIGHT = 160
LANE_PADDING = 60
POOL_GAP = 80
POOL_RIGHT_MARGIN = 220
MIN_POOL_WIDTH = 900
 
ELEMENT_SIZE = {"event": (36, 36), "gateway": (50, 50), "task": (100, 80)}

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
        self.outgoing = {}
        self.incoming = {}

        for flow in diagram.seq_flows:
            source_id, target_id = flow.startRef.element_id, flow.endRef.element_id
            self.outgoing.setdefault(source_id, []).append(target_id)
            self.incoming.setdefault(target_id, []).append(source_id)
 
        self.positions = {}
        self.lane_info = {}
        self.pool_info = {}
        self.backward_flows = set()

        self.elements_by_id = {
            element.element_id: element
            for element in (diagram.events + diagram.tasks + diagram.gateways)
        }

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
        self.build_layout()
 
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
            collaboration = ET.SubElement(root, self.qname(self.BPMN, "collaboration"), {"id": collaboration_id})
 
            for pool in self.diagram.pools:
                attributes = {"id": pool.element_id, "processRef": self.diagram.id}

                if pool.label:
                    attributes["name"] = pool.label

                ET.SubElement(collaboration, self.qname(self.BPMN, "participant"), attributes)
 
            for flow in self.diagram.msg_flows:
                self.add_message_flow(collaboration, flow)

        process = ET.SubElement(
            root,
            self.qname(self.BPMN, "process"),
            {"id": self.diagram.id, "name": self.diagram.name, "isExecutable": "true"}
        )
 
        self.add_lane_set(process)
 
        for element in self.diagram.tasks + self.diagram.events + self.diagram.gateways:
            self.add_bpmn_element(process, element, element.type)
 
        for flow in self.diagram.seq_flows:
            self.add_sequence_flow(process, flow)
 
        self.create_diagram_layout(root, collaboration_id)
        ET.indent(root, space = "  ", level = 0)

        return ET.tostring(root, encoding = "UTF-8", xml_declaration = True)

    def add_lane_set(self, process):
        if not self.diagram.swimlanes:
            return
 
        lane_set = ET.SubElement(
            process, self.qname(self.BPMN, "laneSet"),
            {"id": self.diagram.generate_unique_id("LaneSet")}
        )
 
        for lane in self.diagram.swimlanes:
            attributes = {"id": lane.element_id}

            if lane.label is not None:
                attributes["name"] = lane.label
 
            lane_element = ET.SubElement(lane_set, self.qname(self.BPMN, "lane"), attributes)
 
            for node in lane.lane_elements:
                flow_node_ref = ET.SubElement(lane_element, self.qname(self.BPMN, "flowNodeRef"))
                flow_node_ref.text = node.element_id

    def add_bpmn_element(self, process, element, tag):
        event_name_map = {
            "messageCatchEvent": "messageEventDefinition",
            "timerCatchEvent": "timerEventDefinition",
            "conditionalCatchEvent": "conditionalEventDefinition",
        }

        attributes = {"id": element.element_id}
        if element.label is not None:
            attributes["name"] = element.label

        if element.is_event() and element.type in event_name_map:
            tag = "intermediateCatchEvent"

        xml_element = ET.SubElement(process, self.qname(self.BPMN, tag), attributes)

        for flow in self.diagram.seq_flows:
            if flow.endRef.element_id == element.element_id:
                incoming = ET.SubElement(xml_element, self.qname(self.BPMN, "incoming"))
                incoming.text = flow.element_id

            if flow.startRef.element_id == element.element_id:
                outgoing = ET.SubElement(xml_element, self.qname(self.BPMN, "outgoing"))
                outgoing.text = flow.element_id

        if element.is_event() and element.type in event_name_map:
            definition_tag = event_name_map[element.type]
            ET.SubElement(
                xml_element, self.qname(self.BPMN, definition_tag),
                {"id": self.diagram.generate_unique_id(definition_tag[0].upper() + definition_tag[1:])}
            )

    def add_sequence_flow(self, process, flow):
        attributes = {
            "id": flow.element_id,
            "sourceRef": flow.startRef.element_id,
            "targetRef": flow.endRef.element_id
        }

        if flow.label:
            attributes["name"] = flow.label

        ET.SubElement(process, self.qname(self.BPMN, "sequenceFlow"), attributes)
 
    def add_message_flow(self, collaboration, flow):
        attributes = {
            "id": flow.element_id,
            "sourceRef": flow.startRef.element_id,
            "targetRef": flow.endRef.element_id
        }

        if flow.label:
            attributes["name"] = flow.label

        ET.SubElement(collaboration, self.qname(self.BPMN, "messageFlow"), attributes)

    def all_elements(self):
        return self.diagram.events + self.diagram.tasks + self.diagram.gateways
 
    def find_backward_flows(self, nodes):
        state = {}
        back_edges = set()
 
        def visit(node):
            state[node] = "visiting"

            for target in self.outgoing.get(node, []):
                if state.get(target) == "visiting":
                    back_edges.add((node, target))

                elif target not in state:
                    visit(target)

            state[node] = "done"
 
        for node in nodes:
            if node not in state:
                visit(node)
 
        return back_edges
 
    def assign_columns(self, nodes):
        indegree = {node: 0 for node in nodes}
        forward_out = {node: [] for node in nodes}
 
        for node in nodes:
            for target in self.outgoing.get(node, []):
                if (node, target) in self.back_edges:
                    continue

                forward_out[node].append(target)
                indegree[target] += 1
 
        column = {node: 0 for node in nodes}
        queue = [node for node in nodes if indegree[node] == 0]
 
        while queue:
            node = queue.pop(0)
            for target in forward_out[node]:
                column[target] = max(column[target], column[node] + 1)
                indegree[target] -= 1

                if indegree[target] == 0:
                    queue.append(target)
 
        return column
 
    def lane_bands(self):
        bands = []
        pools = self.diagram.pools if self.diagram.pools else [None]
 
        for pool in pools:
            lanes = getattr(pool, "swimlanes", None) if pool else self.diagram.swimlanes
            if not lanes:
                lanes = self.diagram.swimlanes or [None]
 
            pool_lanes = [
                {"lane": lane, "elements": lane.lane_elements if lane else self.all_elements()}
                for lane in lanes
            ]
            bands.append({"pool": pool, "lanes": pool_lanes})
 
        return bands
 
    def build_layout(self):
        nodes = [element.element_id for element in self.all_elements()]
        self.back_edges = self.find_backward_flows(nodes)
        column = self.assign_columns(nodes)
 
        bands = self.lane_bands()
        for pool_band in bands:
            for lane_band in pool_band["lanes"]:
                by_column = {}

                for element in lane_band["elements"]:
                    by_column.setdefault(column[element.element_id], []).append(element)

                lane_band["by_column"] = by_column
 
        max_column = max(column.values(), default = 0)
 
        pool_width = max(MIN_POOL_WIDTH, X_START + max_column * X_GAP + POOL_RIGHT_MARGIN)
        lane_width = pool_width - 30
        current_y = Y_START
 
        for pool_band in bands:
            pool = pool_band["pool"]
            lane_y = current_y
            pool_height = 0
 
            for lane_band in pool_band["lanes"]:
                stack_count = max((len(g) for g in lane_band["by_column"].values()), default=1)
                lane_height = max(MIN_LANE_HEIGHT, LANE_PADDING * 2 + (stack_count - 1) * ROW_GAP + 80)
                lane_band["y"] = lane_y
                lane_band["height"] = lane_height
                pool_height += lane_height
 
                lane = lane_band["lane"]
                if lane is not None:
                    self.lane_info[lane.element_id] = (90, lane_y, lane_width, lane_height)
 
                lane_y += lane_height
 
            if pool is not None:
                self.pool_info[pool.element_id] = (60, current_y, pool_width, pool_height)
 
            current_y += pool_height + POOL_GAP
 
        for col in range(max_column + 1):
            for pool_band in bands:
                for lane_band in pool_band["lanes"]:

                    group = lane_band["by_column"].get(col)
                    if not group:
                        continue
 
                    group.sort(key = lambda e: self.predecessor_y(e.element_id))
 
                    x = X_START + col * X_GAP
                    lane_center_y = lane_band["y"] + lane_band["height"] / 2
                    stack_height = (len(group) - 1) * ROW_GAP
                    start_y = lane_center_y - stack_height / 2
 
                    for row, element in enumerate(group):
                        width, height = self.element_size(element)
                        center_y = start_y + row * ROW_GAP
                        y = center_y - height / 2
 
                        self.positions[element.element_id] = {
                            "x": x, "y": y, "width": width, "height": height,
                            "center_x": x + width / 2, "center_y": y + height / 2,
                        }
 
    def predecessor_y(self, element_id):
        predecessor_ys = [
            self.positions[p]["center_y"]
            for p in self.incoming.get(element_id, [])
            if p in self.positions
        ]

        return sum(predecessor_ys) / len(predecessor_ys) if predecessor_ys else 0
 
    def element_size(self, element):
        if element.is_event():
            return ELEMENT_SIZE["event"]
        
        if element.is_gateway():
            return ELEMENT_SIZE["gateway"]
        
        return ELEMENT_SIZE["task"]
 
    def create_diagram_layout(self, root, collaboration_id=None):
        diagram = ET.SubElement(root, self.qname(self.BPMNDI, "BPMNDiagram"), {"id": "BPMNDiagram_1"})
        plane = ET.SubElement(
            diagram, self.qname(self.BPMNDI, "BPMNPlane"),
            {"id": "BPMNPlane_1", "bpmnElement": collaboration_id or self.diagram.id}
        )
 
        for pool in self.diagram.pools:
            x, y, w, h = self.pool_info[pool.element_id]
            self.add_shape(plane, pool.element_id, x, y, w, h, is_horizontal = True)
 
        for lane in self.diagram.swimlanes:
            x, y, w, h = self.lane_info[lane.element_id]
            self.add_shape(plane, lane.element_id, x, y, w, h, is_horizontal = True)
 
        for element in self.all_elements():
            pos = self.positions[element.element_id]
            self.add_shape(plane, element.element_id, pos["x"], pos["y"], pos["width"], pos["height"])
 
        for flow in self.diagram.seq_flows:
            self.add_sequence_flow_edge(plane, flow)
 
        for flow in self.diagram.msg_flows:
            self.add_message_flow_edge(plane, flow)
 
    def add_shape(self, plane, element_id, x, y, width, height, is_horizontal = False):
        attributes = {"id": f"{element_id}_di", "bpmnElement": element_id}

        if is_horizontal:
            attributes["isHorizontal"] = "true"
 
        shape = ET.SubElement(plane, self.qname(self.BPMNDI, "BPMNShape"), attributes)
        ET.SubElement(
            shape, self.qname(self.DC, "Bounds"),
            {"x": str(x), "y": str(y), "width": str(width), "height": str(height)}
        )
 
    def add_edge(self, plane, flow, waypoints):
        edge = ET.SubElement(
            plane, self.qname(self.BPMNDI, "BPMNEdge"),
            {"id": f"{flow.element_id}_di", "bpmnElement": flow.element_id}
        )

        for x, y in waypoints:
            ET.SubElement(
                edge, self.qname(self.DI, "waypoint"),
                {"x": str(round(x, 2)), "y": str(round(y, 2))}
            )
 
    def add_message_flow_edge(self, plane, flow):
        source = self.positions.get(flow.startRef.element_id)
        target = self.positions.get(flow.endRef.element_id)

        if not source or not target:
            return
 
        start = (source["center_x"], source["y"] + source["height"])
        end = (target["center_x"], target["y"])
        self.add_edge(plane, flow, [start, end])

    def is_gateway_id(self, element_id):
        element = self.elements_by_id.get(element_id)
        return element is not None and element.is_gateway()

    def gateway_flow_point(self, gateway_id, other_id, direction):
        gateway = self.positions[gateway_id]
        other = self.positions[other_id]

        if direction == "incoming":
            connection_count = len(self.incoming.get(gateway_id, []))

            if connection_count == 1:
                return (gateway["x"], gateway["center_y"]), "left"

            if other["center_y"] < gateway["center_y"]:
                return (gateway["center_x"], gateway["y"]), "top"

            if other["center_y"] > gateway["center_y"]:
                return (gateway["center_x"], gateway["y"] + gateway["height"]), "bottom"

            return (gateway["x"], gateway["center_y"]), "left"

        if direction == "outgoing":
            connection_count = len(self.outgoing.get(gateway_id, []))

            if connection_count == 1:
                return (gateway["x"] + gateway["width"], gateway["center_y"]), "right"

            if other["center_y"] < gateway["center_y"]:
                return (gateway["center_x"], gateway["y"]), "top"

            if other["center_y"] > gateway["center_y"]:
                return (gateway["center_x"], gateway["y"] + gateway["height"]), "bottom"

            return (gateway["x"] + gateway["width"], gateway["center_y"]), "right"

    def sequence_flow_endpoint(self, element_id, other_id, direction, backward = False):
        pos = self.positions[element_id]

        if self.is_gateway_id(element_id):
            return self.gateway_flow_point(element_id, other_id, direction)

        if backward:
            return (pos["center_x"], pos["y"] + pos["height"]), "bottom"

        if direction == "outgoing":
            return (pos["x"] + pos["width"], pos["center_y"]), "right"

        return (pos["x"], pos["center_y"]), "left"

    def orthogonal_waypoints(self, start, start_side, end, end_side):
        start_vertical = start_side in ("top", "bottom")
        end_vertical = end_side in ("top", "bottom")

        if start[0] == end[0] or start[1] == end[1]:
            return [start, end]

        if not start_vertical and not end_vertical:
            mid_x = (start[0] + end[0]) / 2

            return [start, (mid_x, start[1]), (mid_x, end[1]), end]

        if start_vertical and end_vertical:
            mid_y = (start[1] + end[1]) / 2

            return [start, (start[0], mid_y), (end[0], mid_y), end]

        if not start_vertical and end_vertical:
            return [start, (end[0], start[1]), end]

        return [start, (start[0], end[1]), end]
 
    def add_sequence_flow_edge(self, plane, flow):
        source_id = flow.startRef.element_id
        target_id = flow.endRef.element_id

        source = self.positions[source_id]
        target = self.positions[target_id]

        is_backward = (source_id, target_id) in self.back_edges

        start, start_side = self.sequence_flow_endpoint(
            source_id,
            target_id,
            "outgoing",
            backward = is_backward
        )

        end, end_side = self.sequence_flow_endpoint(
            target_id,
            source_id,
            "incoming",
            backward = is_backward
        )

        if is_backward:

            detour_y = max(
                source["y"] + source["height"],
                target["y"] + target["height"]
            ) + 60

            self.add_edge(
                plane,
                flow,
                [
                    start,
                    (start[0], detour_y),
                    (end[0], detour_y),
                    end
                ]
            )

            return

        waypoints = self.orthogonal_waypoints(start, start_side, end, end_side)
        self.add_edge(plane, flow, waypoints)