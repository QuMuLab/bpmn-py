class BPMNElement:

    def __init__(self, label: str, element_id: str):
        self.label = label
        self.element_id = element_id

    def __str__(self):
        return f'{self.element_id} : {self.label}'

class Pool(BPMNElement):
    def __init__(self, label: str, element_id: str):
        super().__init__(label, element_id)

class Swimlane(BPMNElement):

    def __init__(self, label: str, element_id: str):
        super().__init__(label, element_id)

class Task(BPMNElement):

    def __init__(self, label: str, element_id: str, type: str,):
        super().__init__(label, element_id)
        self.type = type

class Event(BPMNElement):

    def __init__(self, label: str, element_id: str, type: str):
        super().__init__(label, element_id)
        self.type = type

class Gateway(BPMNElement):

    def __init__(self, label: str, element_id: str, type: str):
        super().__init__(label, element_id)
        self.type = type

class SequenceFlow(BPMNElement):

    def __init__(self, label: str, element_id: str, startRef: str, endRef: str):
        super().__init__(label, element_id)
        self.startRef = startRef
        self.endRef = endRef

class MessageFlow(BPMNElement):

    def __init__(self, label: str, element_id: str, startRef: str, endRef: str):
        super().__init__(label, element_id)
        self.startRef = startRef
        self.endRef = endRef