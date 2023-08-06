import pytest

from cjen.nene.collections.tree import Tree


@pytest.fixture
def data_one():
    return [dict(site_id=1, site_name="D01")]


def test_one_level_tree(data_one):
    tree = Tree.factory(total_level=1, data=data_one)
    assert len(tree.nodes) == 1
    assert len(tree.get_level_nodes(0)) == 1
    root0 = tree.get_level_nodes(0)[0]
    assert root0.values["site_id"] == 1
    assert root0.values["site_name"] == "D01"
    tree.add(data_one)
    assert len(tree.nodes) == 1
    assert len(tree.get_level_nodes(0)) == 1
    assert root0.values["site_id"] == 1
    assert root0.values["site_name"] == "D01"


@pytest.fixture
def data_two():
    return [[dict(site_id=1, site_name="D01"), dict(subject_id=1, subject_name="S01")],
            [dict(site_id=1, site_name="D01"), dict(subject_id=1, subject_name="S01")],
            [dict(site_id=1, site_name="D01"), dict(subject_id=2, subject_name="S02")],
            [dict(site_id=2, site_name="D02"), dict(subject_id=1, subject_name="S01")],
            [dict(site_id=2, site_name="D02"), dict(subject_id=2, subject_name="S02")],
            [dict(site_id=2, site_name="D02"), dict(subject_id=3, subject_name="S04")],
            [dict(site_id=2, site_name="D03"), dict(subject_id=3, subject_name="S04")]]


def test_two_level_tree(data_two):
    tree = Tree.factory(total_level=2)
    for e in data_two:
        tree.add(e)
        assert len(tree.nodes) == 2

    assert len(tree.get_level_nodes(0)) == 3
    root0 = tree.get_level_nodes(0)[0]
    root1 = tree.get_level_nodes(0)[1]
    root2 = tree.get_level_nodes(0)[2]
    assert root0.values["site_id"] == 1
    assert root0.values["site_name"] == "D01"
    assert root1.values["site_id"] == 2
    assert root1.values["site_name"] == "D02"
    assert root2.values["site_id"] == 2
    assert root2.values["site_name"] == "D03"
    assert len(tree.get_level_nodes(1)) == 6
    assert len(root0.children_idx) == 2
    assert root0.find_child(subject_id=1, subject_name="S01") is not None
    assert root0.find_child(subject_id=1, subject_name="S01").get_parent().satisfy(site_id=1, site_name="D01") is True
    assert root0.find_child(subject_id=2, subject_name="S02") is not None
    assert root0.find_child(subject_id=2, subject_name="S02").get_parent().satisfy(site_id=1, site_name="D01") is True
    assert len(root1.children_idx) == 3
    assert root1.find_child(subject_id=1, subject_name="S01") is not None
    assert root1.find_child(subject_id=1, subject_name="S01").get_parent().satisfy(site_id=2, site_name="D02") is True
    assert root1.find_child(subject_id=2, subject_name="S02") is not None
    assert root1.find_child(subject_id=2, subject_name="S02").get_parent().satisfy(site_id=2, site_name="D02") is True
    assert root1.find_child(subject_id=3, subject_name="S04") is not None
    assert root1.find_child(subject_id=3, subject_name="S04").get_parent().satisfy(site_id=2, site_name="D02") is True
    assert len(root2.children_idx) == 1
    assert root2.find_child(subject_id=3, subject_name="S04") is not None
    assert root2.find_child(subject_id=3, subject_name="S04").get_parent().satisfy(site_id=2, site_name="D03") is True


@pytest.fixture
def data_three():
    return [[dict(site_id=1, site_name="D01"), dict(subject_id=1, subject_name="S01"), dict(visit_id=1, visit_name="V01")],
            [dict(site_id=1, site_name="D01"), dict(subject_id=1, subject_name="S01"), dict(visit_id=1, visit_name="V01")],
            [dict(site_id=1, site_name="D01"), dict(subject_id=1, subject_name="S01"), dict(visit_id=2, visit_name="V02")],
            [dict(site_id=1, site_name="D01"), dict(subject_id=2, subject_name="S02"), dict(visit_id=1, visit_name="V01")],
            [dict(site_id=2, site_name="D02"), dict(subject_id=1, subject_name="S01"), dict(visit_id=1, visit_name="V01")],
            [dict(site_id=2, site_name="D02"), dict(subject_id=2, subject_name="S02"), dict(visit_id=2, visit_name="V02")],
            [dict(site_id=2, site_name="D02"), dict(subject_id=3, subject_name="S04"), dict(visit_id=3, visit_name="V03")],
            [dict(site_id=2, site_name="D03"), dict(subject_id=3, subject_name="S04"), dict(visit_id=1, visit_name="V01")]]


def test_three_level_tree(data_three):
    tree = Tree.factory(total_level=3)
    for e in data_three:
        tree.add(e)
    assert len(tree.nodes) == 3
    tree.refresh(data_three)
    assert len(tree.nodes) == 3
    assert len(tree.get_level_nodes(0)) == 3
    root0 = tree.get_level_nodes(0)[0]
    root1 = tree.get_level_nodes(0)[1]
    root2 = tree.get_level_nodes(0)[2]
    assert root0.values["site_id"] == 1
    assert root0.values["site_name"] == "D01"
    assert root1.values["site_id"] == 2
    assert root1.values["site_name"] == "D02"
    assert root2.values["site_id"] == 2
    assert root2.values["site_name"] == "D03"
    assert len(tree.get_level_nodes(1)) == 6
    assert len(root0.children_idx) == 2
    assert root0.find_child(subject_id=1, subject_name="S01") is not None
    assert root0.find_child(subject_id=1, subject_name="S01").get_parent().satisfy(site_id=1, site_name="D01") is True
    assert root0.find_child(subject_id=2, subject_name="S02") is not None
    assert root0.find_child(subject_id=2, subject_name="S02").get_parent().satisfy(site_id=1, site_name="D01") is True
    assert len(root1.children_idx) == 3
    assert root1.find_child(subject_id=1, subject_name="S01") is not None
    assert root1.find_child(subject_id=1, subject_name="S01").get_parent().satisfy(site_id=2, site_name="D02") is True
    assert root1.find_child(subject_id=2, subject_name="S02") is not None
    assert root1.find_child(subject_id=2, subject_name="S02").get_parent().satisfy(site_id=2, site_name="D02") is True
    assert root1.find_child(subject_id=3, subject_name="S04") is not None
    assert root1.find_child(subject_id=3, subject_name="S04").get_parent().satisfy(site_id=2, site_name="D02") is True
    assert len(root2.children_idx) == 1
    assert root2.find_child(subject_id=3, subject_name="S04") is not None
    assert root2.find_child(subject_id=3, subject_name="S04").get_parent().satisfy(site_id=2, site_name="D03") is True

    assert len(tree.get_level_nodes(2)) == 7
    assert len(root0.find_child(subject_id=1, subject_name="S01").children_idx) == 2
    assert root0.find_child(subject_id=1, subject_name="S01").find_child(visit_id=1, visit_name="V01").get_parent().get_parent().satisfy(site_id=1, site_name="D01") is True
    assert root0.find_child(subject_id=1, subject_name="S01").find_child(visit_id=2, visit_name="V02").get_parent().get_parent().satisfy(site_id=1, site_name="D01") is True
    assert len(root0.find_child(subject_id=2, subject_name="S02").children_idx) == 1
    assert root0.find_child(subject_id=2, subject_name="S02").find_child(visit_id=1, visit_name="V01").get_parent().get_parent().satisfy(site_id=1, site_name="D01") is True
    assert len(root1.find_child(subject_id=1, subject_name="S01").children_idx) == 1
    assert root1.find_child(subject_id=1, subject_name="S01").find_child(visit_id=1, visit_name="V01").get_parent().get_parent().satisfy(site_id=2, site_name="D02") is True
    assert len(root1.find_child(subject_id=2, subject_name="S02").children_idx) == 1
    assert root1.find_child(subject_id=2, subject_name="S02").find_child(visit_id=2, visit_name="V02").get_parent().get_parent().satisfy(site_id=2, site_name="D02") is True
    assert len(root1.find_child(subject_id=3, subject_name="S04").children_idx) == 1
    assert root1.find_child(subject_id=3, subject_name="S04").find_child(visit_id=3, visit_name="V03").get_parent().get_parent().satisfy(site_id=2, site_name="D02") is True
    assert len(root2.find_child(subject_id=3, subject_name="S04").children_idx) == 1
    assert root2.find_child(subject_id=3, subject_name="S04").find_child(visit_id=1, visit_name="V01").get_parent().get_parent().satisfy(site_id=2, site_name="D03") is True
