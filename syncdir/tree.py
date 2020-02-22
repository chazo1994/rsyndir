import os

class DirTree(object):
    def __init__(self, parent, name, state):
        self.parent = parent
        self.name = name
        self.state = state
        self.childrens = []
        self.level = 0
        if self.parent is not None:
            self.path = os.path.join(self.parent.path, self.name)
        else:
            self.path = ""
        self.mtime = 0
        self.total_change = 0

    def add_node(self, node):
        self.childrens.append(node)
    def is_children(self, name):
        for children in self.childrens:
            if name == children.name:
                return True
        return False
    def get_children(self, name):
        for children in self.childrens:
            if name == children.name:
                return children
        return None

    def set_parent(self, parent):
        self.parent = parent
    def set_level(self, level):
        self.level = level
    def is_leaf(self):
        if len(self.childrens) == 0:
            return True
        else:
            return False
    def get_mtime(self):
        self.mtime = os.stat(self.path)[8]
        return self.mtime
    def update_state(self, state):
        if state != 0:
            self.state = 1
        else:
            self.state = 0