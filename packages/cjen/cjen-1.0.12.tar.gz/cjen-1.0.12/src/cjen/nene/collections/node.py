"""
level 0: site
level 1 :subject
level 2 :visit
level 3 :form
level 4 :ig
level 5 :item (variable, item_id, question)
"""


class Node:

    def __init__(self, tree, parent_idx=None, level=0):
        self.children_idx: set[int] = set()
        self.parent_idx = parent_idx
        self.values = dict()
        self.level = level
        self.tree = tree

    def add_child(self, index):
        self.children_idx.add(index)

    def has_child(self) -> bool:
        return len(self.children_idx) != 0

    def has_parent(self) -> bool:
        return self.parent_idx is not None

    def set(self, key, value):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key)

    '''
    搜寻特定的子节点
    '''

    def find_child(self, **kwargs):
        if not self.has_child():
            return None
        for i in self.children_idx:
            node = self.tree.nodes[self.level+1][i]
            if node.satisfy(**kwargs):
                return node
        return None

    def get_child(self, index):
        if index in self.children_idx:
            return self.tree.nodes[self.level+1][index]
        return None

    def get_parent(self):
        if not self.has_parent():
            return None
        return self.tree.nodes[self.level-1][self.parent_idx]

    """
    判断两个节点是否相同
    """
    def eql(self, node):
        return self.satisfy(**node.values)

    '''
    根据传入的参数来判断该节点是否满足条件
    '''
    def satisfy(self, **kwargs):
        for k, v in kwargs.items():
            if self.values[k] != v:
                return False
        return True
