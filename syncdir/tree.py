import os

class DirTree(object):
    def __init__(self, parent, name, state, version):
        self.parent = parent
        self.name = name
        self.state = state
        self.version =version
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
    def update_state(self):
        self.state = state

    def update_version(self):
        self.version += 1

    #Format: "Node name|parent name|children names|state|version"
    def node_info(self):
        info_str = self.name + "|" + self.parent.name + "|" + " ".join([chil.name for chil in self.childrens] + "|" + str(self.state) + "|" + str(self.version))
        return info_str
