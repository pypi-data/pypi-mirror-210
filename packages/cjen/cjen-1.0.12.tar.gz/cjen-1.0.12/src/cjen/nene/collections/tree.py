

"""
通用的数据结构
目标：把列表字典转换成树形结构
新生成树:
data = [
    [dict(id=1),dict(id=2)]
    [dict(id=1),dict(id=3)]
    [dict(id=1),dict(id=4)]
]
tree = Tree.factory(data) 
        1       
    2   3   4
添加节点:
data = [dict(id=1),dict(id=5)]
tree.add(data)
        1
    2   3   4   5
刷新树:
data = [
    [dict(id=100),dict(id=200)]
    [dict(id=100),dict(id=300)]
    [dict(id=100),dict(id=400)]
]
tree.refresh(data)
        100
    200   300   400
"""
from cjen.nene.collections.node import Node


class Tree:
    """
    total_level
    设置树形结构的层数
    """
    def __init__(self, total_level):
        self.total_level = total_level
        self.nodes: list[list[Node]] = self.new_node_list()

    def new_node_list(self):
        return [[] for i in range(self.total_level)]

    def __create_node(self, parent_idx=None, level=0, **kwargs):
        node = Node(self, parent_idx, level)
        for key, value in kwargs.items(): node.set(key, value)
        index = self.__add(parent_idx, level, node)
        if node.has_parent():
            node.get_parent().add_child(index)
        return index

    """
    添加树的节点
    :param data
    格式要求 字典列表 [dict(),dict()]
    data的长度 = total_level
    """
    def add(self, data: list[dict]):
        # 第一次节点是没有父节点的，所以首次把 parent 设置为 None
        parent = None
        for level in range(self.total_level):
            parent = self.__create_node(parent, level, **data[level])

    def clean(self):
        self.nodes: list[list[Node]] = []
        self.total_level = -1

    def index(self, level, i) -> Node:
        return self.get_level_nodes(level)[i]

    """
    指定level 
    指定索引搜索满足props条件的值
    :return 返回一个值, 如没有则返回None
    """

    def find(self, level, xrange: set, **props) -> Node:
        result = list(filter(lambda i: self.nodes[level][i].satisfy(**props), xrange))
        if not result: return None
        return self.nodes[level][result[0]]

    """
    指定level
    搜索满足props条件的值
    :return 返回所有满足条件的
    """

    def search(self, level, **props):
        return list(filter(lambda node: node.satisfy(**props), self.nodes[level]))

    def get_level_nodes(self, level) -> list[Node]:
        return self.nodes[level]

    def __add(self, parent_idx, level, node) -> int:
        level_nodes = self.nodes[level]
        if parent_idx is None:
            # level = 0 的层级节点
            # 因为level = 0 层级的节点，没有父节点，所以直接判断是否已存在相同节点，如果存在直接返回索引值
            for i in range(len(level_nodes)):
                if level_nodes[i].eql(node): return i
        else:
            # level != 0 的层级节点
            # 因为是有父节点的，所以判断有相同父节点的兄弟节点中是否已存在相同节点，如果存在直接返回索引值
            for i in self.nodes[level - 1][parent_idx].children_idx:
                if level_nodes[i].eql(node): return i
        # 节点为新节点,加入对应层级的节点列表，并返回索引
        self.nodes[level].append(node)
        return len(level_nodes) - 1
    """
    :parameter new_total_level
    默认是不改变树的层级数,如果要改变则需要传递此参数
    """
    def refresh(self, data: list[list[dict]], new_total_level=None):
        total_level = new_total_level if new_total_level else self.total_level
        self.clean()
        self.total_level = total_level
        self.nodes = self.new_node_list()
        for e in data: self.add(e)

    @classmethod
    def factory(cls, total_level, data: list[dict] = None):
        tree = Tree(total_level=total_level)
        if data is not None: tree.add(data)
        return tree
