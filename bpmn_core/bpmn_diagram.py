from bpmn_core import bpmn_elements
from re import sub
import random
import string

unique_ids = []

class Diagram:
    """
    Represents a BPMN process diagram.

    Args:
        name: Name of the BPMN diagram.
    """
    def __init__(self, name: str):
        self.name = self.clean_name(name)
        self.id = self.generate_unique_id("process")
        self.pools = []
        self.swimlanes = []
        self.tasks = []
        self.events = []
        self.gateways = []
        self.seq_flows = []
        self.msg_flows = []

    def generate_unique_id(self, prefix: str):
        element_id = f"{prefix}_" + "".join(
            random.choices(string.ascii_letters + string.digits, k = 7)
        )

        while element_id in unique_ids:
            element_id = f"{prefix}_" + "".join(
                random.choices(string.ascii_letters + string.digits, k = 7)
            )

        return element_id

    def clean_name(self, name: str) -> str:
        return sub(r"[^a-zA-Z0-9_]", "_", name.lower())

    def get_elements(self) -> list[bpmn_elements.Element]:
        return self.pools + self.swimlanes + self.tasks + self.events + self.gateways + self.seq_flows + self.msg_flows

    def add_pool(self, label: str, element_id: str = None):
        """
        Add a pool to the BPMN diagram.

        Args:
            label: The name of the pool.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created Pool object.
        """
        pool = bpmn_elements.Pool(label, element_id, self)
        self.pools.append(pool)

        return pool

    def add_swimlane(self, label: str, element_id: str = None):
        """
        Add a swimlane to the BPMN diagram.

        Args:
            label: The name of the swimlane.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created Swimlane object.
        """
        swimlane = bpmn_elements.Swimlane(label, element_id)
        self.swimlanes.append(swimlane)

        return swimlane

    def add_task(self, label: str, type: bpmn_elements.task_type, element_id: str = None):
        """
        Add a task to the BPMN diagram.

        Args:
            label: The name of the task.
            type: BPMN task type.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created Task object.
        """
        task = bpmn_elements.Task(label, element_id, type)
        self.tasks.append(task)

        return task

    def add_event(self, label: str, type: bpmn_elements.event_type, element_id: str = None):
        """
        Add an event to the BPMN diagram.

        Args:
            label: The name of the event.
            type: BPMN event type.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created Event object.
        """
        event = bpmn_elements.Event(label, element_id, type)
        self.events.append(event)

        return event

    def add_gateway(self, label: str, type: bpmn_elements.gateway_type, element_id: str = None):
        """
        Add a gateway to the BPMN diagram.

        Args:
            label: The name of the gateway.
            type: BPMN gateway type.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created Gateway object.
        """
        gateway = bpmn_elements.Gateway(label, element_id, type)
        self.gateways.append(gateway)

        return gateway

    def add_sequence_flow(self, startRef: str, endRef: str, label: str = None, element_id: str = None):
        """
        Add a sequence flow to the BPMN diagram.

        Args:
            startRef: The element ID of the BPMN element the flow starts from.
            endRef: The elemnent ID of the BPMN element the flow ends at.
            label: The name of the sequence flow.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created SequenceFlow object.
        """
        seq_flow = bpmn_elements.SequenceFlow(label, element_id, startRef, endRef)
        self.seq_flows.append(seq_flow)

        return seq_flow

    def add_message_flow(self, startRef: str, endRef: str, label: str = None, element_id: str = None):
        """
        Add a message flow to the BPMN diagram.

        Args:
            startRef: The element ID of the BPMN element the flow starts from.
            endRef: The elemnent ID of the BPMN element the flow ends at.
            label: The name of the message flow.
            element_id: Optional BPMN element ID. If omitted, an ID is generated automatically.

        Returns:
            The newly created MessageFlow object.
        """
        msg_flow = bpmn_elements.MessageFlow(label, element_id, startRef, endRef)
        self.msg_flows.append(msg_flow)

        return msg_flow

    def print_elements(self):
        """
        Print all the elements in the BPMN diagram.
        """
        elements = self.get_elements()
        for element in elements:
            print(element)