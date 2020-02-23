from syncdir.tree import DirTree
import os, sys


def build_dir_tree(root_dir):
    root_name = os.path.basename(root_dir)

    root_node = DirTree(None, root_name, 0, 0)
    root_node.set_level(0)
    root_node.path = root_dir
    for root, _, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file).replace(root_dir + os.sep, "")
            elements = filter(None, file_path.split(os.sep))
            node_level = 1
            parent_node = root_node
            for element in elements:
                if not element:
                    continue

                if parent_node.is_children(element):
                    current_node = parent_node.get_children(element)
                else:
                    current_node = DirTree(parent_node, element, 0, 0)
                    parent_node.add_node(current_node)
                current_node.set_level(node_level)
                parent_node = current_node
                node_level += 1
    return root_node

def update_status(root_node):
    total_change = 0
    root_dir = root_node.path
    for root, _, files in os.walk():
        for file in files:
            file_path = os.path.join(root, file).replace(root_dir + os.sep, "")
            elements = filter(None, file_path.split(os.sep))
            current_node = root_node
            for element in elements:
                if not element:
                    continue
                if current_node.is_children(element):
                    children_node = current_node.get_children(element)
                    mtime = os.stat(children_node.path)[8]
                    if mtime != children_node.mtime:
                        children_node.update_state(1)
                        children_node.update_version()
                        total_change += 1
                    else:
                        children_node.update_state(0)
                    current_node = children_node
                else:
                    new_node = DirTree(current_node, element, 0)
                    new_node.mtime = os.stat(children_node.path)[8]
                    new_node.update_state(1)
                    current_node.add_node(new_node)
                    current_node = new_node
                    total_change += 1
    return total_change

def dir_table(table, root_node):

    if root_node.is_leaf():
        table.append(root_node.node_info)
        return
    for chil in root_node.childrens:
        dir_table(table, chil)
def write_dir_table_to_file(table, file_name):
    with open(file_name,"w") as f:
        for line in table:
            f.write(line + "\n")
def load_node_from_file():
    pass
def load_table_from_file():
    pass

class DirManager(object):
    def __init__(self, checkpoint, rootdir):
        self.root_node = None
        self.rootdir = rootdir
        self.checkpoint = checkpoint
        if os.path.isfile(self.checkpoint):
            self.load_checkpoint()
        else:
            self.build_dir_tree(self.rootdir)
            self.save_checkpoint()
        self.table = []
        self.get_dir_table()
    def load_checkpoint(self):
        return None
    def build_dir_tree(self):
        self.root_node = build_dir_tree(self.rootdir)
    def update_status(self):
        total_change = update_status(self.root_node)
        if total_change != 0:
            self.save_checkpoint()
            self.get_dir_table()
        return total_change
    def get_dir_table(self):
        if self.table:
            self.table.clear()
        dir_table(self.table, self.root_node)
    def save_checkpoint(self):
        if not self.table:
            self.get_dir_table()
        write_dir_table_to_file(self.table, self.checkpoint)



def print_tree(root_node):
    if root_node.is_leaf():
        print(root_node.path)
        print("Time: %s, Path: %s" % (str(root_node.get_mtime()), root_node.path))
        return
    for children in root_node.childrens:
        print_tree(children)

def test_walk(root_dir):
    for root, _, files in os.walk(root_dir):
        fps = []
        for file in files:
            file_path = os.path.join(root, file)
            fps.append(file_path)

        for fn in fps:
            print(fn)
if __name__=="__main__":
    # test_walk(sys.argv[1])
    root_node = build_dir_tree(sys.argv[1])
    print_tree(root_node)