class Element:

    def __init__(self, label: str, element_id: str):
        self.label = label
        self.element_id = element_id

    def __str__(self):
        return f'{self.element_id} : {self.label}'
    
    def is_task(self):
        return isinstance(self, Task)
    
    def is_event(self):
        return isinstance(self, Event)
    
    def is_gateway(self):
        return isinstance(self, Gateway)
    
    def is_sequence_flow(self):
        return isinstance(self, SequenceFlow)

class Pool(Element):
    def __init__(self, label: str, element_id: str):
        super().__init__(label, element_id)

class Swimlane(Element):

    def __init__(self, label: str, element_id: str):
        super().__init__(label, element_id)

class Task(Element):

    def __init__(self, label: str, element_id: str, type: str,):
        super().__init__(label, element_id)
        self.type = type

class Event(Element):

    def __init__(self, label: str, element_id: str, type: str):
        super().__init__(label, element_id)
        self.type = type

class Gateway(Element):

    def __init__(self, label: str, element_id: str, type: str):
        super().__init__(label, element_id)
        self.type = type

class SequenceFlow(Element):

    def __init__(self, label: str, element_id: str, startRef: str, endRef: str):
        super().__init__(label, element_id)
        self.startRef = startRef
        self.endRef = endRef

class MessageFlow(Element):

    def __init__(self, label: str, element_id: str, startRef: str, endRef: str):
        super().__init__(label, element_id)
        self.startRef = startRef
        self.endRef = endRef