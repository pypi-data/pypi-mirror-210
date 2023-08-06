import pytest

from erdiagram import ER, NodeType


def test_add_entity():
    g = ER()
    g.add_entity("A")
    assert g.has_entity("A")


def test_add_entity_with_parameters():
    g = ER()
    g.add_entity("A", is_multiple=True, is_weak=True)
    assert g.has_entity("A")
    entity = g.get_entity_by_label("A")
    assert entity["is_multiple"]
    assert entity["is_weak"]


def test_add_multiple_entities_with_same_label_error():
    g = ER()
    g.add_entity("A")
    with pytest.raises(AssertionError):
        g.add_entity("A")


def test_add_relation_existing_entities():
    g = ER()
    g.add_entity("A")
    g.add_entity("B")
    g.add_relation({"A": "1"}, "R", {"B": "n"})
    assert g.has_entity("A")
    assert g.has_entity("B")
    assert g.has_relation("R")


def test_add_relation_missing_entities():
    g = ER()
    g.add_relation({"A": "1"}, "R", {"B": "n"})
    assert g.has_entity("A")
    assert g.has_entity("B")
    assert g.has_relation("R")


def test_add_relation_multiple_entities_from():
    g = ER()
    g.add_relation({"A": "1", "B": "n"}, "R", {"C": "1"})
    assert g.has_entity("A")
    assert g.has_entity("B")
    assert g.has_entity("C")
    assert g.has_relation("R")


def test_add_relation_multiple_entities_to():
    g = ER()
    g.add_relation({"A": "1"}, "R", {"B": "n", "C": "1"})
    assert g.has_entity("A")
    assert g.has_entity("B")
    assert g.has_entity("C")
    assert g.has_relation("R")


def test_add_relation_with_parameters():
    g = ER()
    g.add_relation(
        {"A": {"cardinality": "1", "is_weak": False}},
        "R",
        {"B": {"cardinality": "1", "is_weak": True}, "C": "n"},
    )
    a_id = g.get_entity_by_label("A")["id"]
    b_id = g.get_entity_by_label("B")["id"]
    c_id = g.get_entity_by_label("C")["id"]
    relation = g.get_relation_by_label("R")
    assert relation["from_entities"] == {
        "A": {"id": a_id, "cardinality": "1", "is_weak": False}
    }
    assert relation["to_entities"] == {
        "B": {"id": b_id, "cardinality": "1", "is_weak": True},
        "C": {"id": c_id, "cardinality": "n", "is_weak": False},
    }


def test_add_self_relation():
    g = ER()
    g.add_relation({"A": "1"}, "R", {"A": "n"})
    assert g.has_entity("A")
    assert len(g.get_entities()) == 1
    assert g.has_relation("R")
    entity = g.get_entity_by_label("A")
    relation = g.get_relation_by_label("R")
    assert entity["relation_ids_from"] == [relation["id"]]
    assert entity["relation_ids_from"] == entity["relation_ids_to"]


def test_add_multiple_relations_with_same_label():
    g = ER()
    g.add_relation({"A": "1"}, "R", {"B": "n"})
    g.add_relation({"C": "1"}, "R", {"D": "n"})
    assert g.has_entity("A")
    assert g.has_entity("B")
    assert g.has_entity("C")
    assert g.has_entity("D")
    assert g.has_relation("R")
    assert len(g.get_relations()) == 2


def test_add_relation_with_empty_from_dict():
    g = ER()
    with pytest.raises(AssertionError):
        g.add_relation({}, "R", {"B": "n"})


def test_add_relation_with_empty_to_dict():
    g = ER()
    with pytest.raises(AssertionError):
        g.add_relation({"A": "1"}, "R", {})


def test_add_attribute_duplicate_label_same_entity():
    g = ER()
    g.add_entity("A")
    g.add_attribute("A", "attr1")
    with pytest.raises(AssertionError):
        g.add_attribute("A", "attr1")


def test_add_attribute_duplicate_label_different_entities():
    g = ER()
    g.add_entity("A")
    g.add_entity("B")
    g.add_attribute("A", "attr1")
    g.add_attribute("B", "attr1")


def test_add_attribute_duplicate_label_same_relation():
    g = ER()
    g.add_relation({"A": "1"}, "R", {"B": "n"})
    g.add_attribute("R", "attr1")
    with pytest.raises(AssertionError):
        g.add_attribute("R", "attr1")


def test_add_attribute_duplicate_label_different_relations():
    g = ER()
    g.add_relation({"A": "1"}, "R1", {"B": "n"})
    g.add_relation({"C": "1"}, "R2", {"D": "n"})
    g.add_attribute("R1", "attr1")
    g.add_attribute("R2", "attr1")


def test_add_attribute_duplicate_label_entity_and_relation():
    g = ER()
    g.add_entity("A")
    g.add_relation({"A": "1"}, "R", {"B": "n"})
    g.add_attribute("A", "attr1")
    g.add_attribute("R", "attr1")


def test_add_composed_attribute_duplicate_label():
    g = ER()
    g.add_entity("A")
    with pytest.raises(AssertionError):
        g.add_attribute("A", "attr1", composed_of=["sub_attr1", "sub_attr1"])


def test_add_composed_attribute_parent_label():
    g = ER()
    g.add_entity("A")
    g.add_attribute("A", "attr1", composed_of=["attr1"])


def test_add_composed_attribute_uncle_label():
    g = ER()
    g.add_entity("A")
    g.add_attribute("A", "attr1")
    g.add_attribute("A", "attr2", composed_of=["attr1"])


def test_add_composed_attribute_cousin_label():
    g = ER()
    g.add_entity("A")
    g.add_attribute("A", "attr1", composed_of=["attr3"])
    g.add_attribute("A", "attr2", composed_of=["attr3"])


def test_add_is_a_empty_children():
    g = ER()
    with pytest.raises(AssertionError):
        g.add_is_a("A", [], is_total=True, is_disjunct=True)
