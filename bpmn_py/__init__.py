from bpmn_core.bpmn_diagram import Diagram
from bpmn_core.bpmn_exporter import BPMNExporter

from bpmn_xml_parser.bpmn_parser import BPMNParser
from bpmn_xml_parser.xml_creator import XMLCreator

from bpmn_core.bpmn_elements import task_type, event_type, gateway_type

task = task_type.task
userTask = task_type.userTask
serviceTask = task_type.serviceTask
manualTask = task_type.manualTask
scriptTask = task_type.scriptTask
sendTask = task_type.sendTask
recieveTask = task_type.recieveTask
businessRuleTask = task_type.businessRuleTask

startEvent = event_type.startEvent
endEvent = event_type.endEvent
intermediateCatchEvent = event_type.intermediateCatchEvent
messageCatchEvent = event_type.messageCatchEvent
timerCatchEvent = event_type.timerCatchEvent
conditionalCatchEvent = event_type.conditionalCatchEvent

inclusiveGateway = gateway_type.inclusiveGateway
exclusiveGateway = gateway_type.exclusiveGateway
parallelGateway = gateway_type.parallelGateway
eventBasedGateway = gateway_type.eventBasedGateway

__all__ = [
    "Diagram",
    "BPMNExporter",
    "BPMNParser",
    "XMLCreator",

    "task_type",
    "event_type",
    "gateway_type",

    "task",
    "userTask",
    "serviceTask",
    "manualTask",
    "scriptTask",
    "sendTask",
    "recieveTask",
    "businessRuleTask",

    "startEvent",
    "endEvent",
    "intermediateCatchEvent",
    "messageCatchEvent",
    "timerCatchEvent",
    "conditionalCatchEvent",

    "inclusiveGateway",
    "exclusiveGateway",
    "parallelGateway",
    "eventBasedGateway",
]