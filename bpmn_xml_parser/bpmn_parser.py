import xml.etree.ElementTree as ET

from bpmn_core import bpmn_diagram
from bpmn_core.bpmn_elements import event_type, gateway_type, task_type

task_types = ["userTask", "serviceTask", "manualTask", "scriptTask", "sendTask", "recieveTask", "businessRuleTask", "task"]
event_types = ["startEvent", "endEvent", "intermediateCatchEvent"]
gateway_types = ["eventBasedGateway", "exclusiveGateway", "parallelGateway", "inclusiveGateway"]

class BPMNParser:
    """
    Parses a BPMN xml file.

    Args:
        name: The filepath of the .bpmn file.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        self.namespaces = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}

    def clean_label(self, label) -> str:
        return label.replace("\n", " ") if label else None

    def parse(self) -> bpmn_diagram.Diagram:
        """
        Parse the .bpmn file and create a BPMN Diagram from it.

        Returns:
            The newly created Diagram object.
        """
        diagram_name = self.file_path.split("/")[-1][:-5]
        diagram = bpmn_diagram.Diagram(diagram_name)

        for pool in self.root.findall(".//bpmn:participant", self.namespaces):
            diagram.add_pool(
                label = self.clean_label(pool.get("name")),
                element_id = pool.get("id")
            )

        for swimlane in self.root.findall(".//bpmn:lane", self.namespaces):
            diagram.add_swimlane(
                label = self.clean_label(swimlane.get("name")),
                element_id = swimlane.get("id")
            )

        for type in task_types:
            for task in self.root.findall(f".//bpmn:{type}", self.namespaces):
                diagram.add_task(
                    label = self.clean_label(task.get("name")),
                    element_id = task.get("id"),
                    type = task_type[type]
                )

        for type in event_types:
            for event in self.root.findall(f".//bpmn:{type}", self.namespaces):
                sub_type = event_type[type]
                
                if type == "intermediateCatchEvent":

                    if event.find("bpmn:timerEventDefinition", self.namespaces) is not None:
                        sub_type = event_type.timerCatchEvent

                    if event.find("bpmn:messageEventDefinition", self.namespaces) is not None:
                        sub_type = event_type.messageCatchEvent

                    if event.find("bpmn:conditionalEventDefinition", self.namespaces) is not None:
                        sub_type = event_type.conditionalCatchEvent

                diagram.add_event(
                    label = self.clean_label(event.get("name")),
                    element_id = event.get("id"),
                    type = sub_type
                )

        for type in gateway_types:
            for gateway in self.root.findall(f".//bpmn:{type}", self.namespaces):
                diagram.add_gateway(
                    label = self.clean_label(gateway.get("name")),
                    element_id = gateway.get("id"),
                    type = gateway_type[type]
                )
        
        for seq_flow in self.root.findall(".//bpmn:sequenceFlow", self.namespaces):
            diagram.add_sequence_flow(
                label = self.clean_label(seq_flow.get("name")),
                element_id = seq_flow.get("id"),
                startRef = seq_flow.get("sourceRef"),
                endRef = seq_flow.get("targetRef")
            )

        for msg_flow in self.root.findall(".//bpmn:messageFlow", self.namespaces):
            diagram.add_message_flow(
                label = self.clean_label(msg_flow.get("name")),
                element_id = msg_flow.get("id"),
                startRef = msg_flow.get("sourceRef"),
                endRef = msg_flow.get("targetRef")
            )

        return diagram