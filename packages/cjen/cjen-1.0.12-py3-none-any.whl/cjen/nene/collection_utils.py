from cjen.nene.collections.tree import Tree


def list_eql(arr1: list, arr2: list, strict: bool = False):
    """
    判断 两个列表是否相同
    strict = True: 严格模式
        a=[1,2] , b=[1,2] ab相同
        a=[1,2] , b=[2,1] ab不相同
    strict = False: 非严格模式
        a=[1,2] , b=[1,2] ab相同
        a=[1,2] , b=[2,1] ab相同
    exception list_eql([[1,2], [3,4]], [[2,1], [4,3]]) 判断为 False
    """
    if strict: return arr1 == arr2
    if len(arr1) != len(arr2): return False
    for e in arr1:
        if e not in arr2: return False
    for e in arr2:
        if e not in arr1: return False
    return True


def make_tree(total_level, data: list[dict] = None):
    return Tree.factory(total_level, data)
