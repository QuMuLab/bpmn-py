class BPMNElement:

    pass

class Swimlane(BPMNElement):

    def __init__(self, label):
        self.label = label

class Task(BPMNElement):

    def __init__(self, type, label: str):
        self.label = label
        self.type = type

class Event(BPMNElement):

    def __init__(self, type, label: str):
        self.label = label
        self.type = type

class Gateway(BPMNElement):

    def __init__(self, type, label: str):
        self.label = label
        self.type = type

class Sequence(BPMNElement):

    def __init__(self, start: BPMNElement, end: BPMNElement, label: str):
        self.start = start
        self.end = end
        self.label = label