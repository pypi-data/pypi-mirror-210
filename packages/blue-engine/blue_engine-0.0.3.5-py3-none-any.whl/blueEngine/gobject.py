import uuid

class GameObject:
    def __init__(self, parent=None) -> None:
        id = uuid.uuid1().int
        self.children = {}
        if parent == None:
            self.parent = 'app'
        else:
            self.parent = parent 

    def add_child(self, object):
        self.children[object.uuid] = object
        object.parent = self
