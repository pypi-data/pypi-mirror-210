import pytest

from erdiagram import ER, merge_er_diagrams


def test_merge_er_diagrams():
    g1 = ER()

    g1.add_entity("E1", is_multiple=True, is_weak=True)
    g1.add_entity("E2", is_multiple=True, is_weak=False)
    g1.add_entity("E3", is_multiple=False, is_weak=True)

    g1.add_relation(
        {
            "E1": "1",
        },
        "R1",
        {
            "E2": "1",
        },
    )

    g1.add_attribute("E1", "A1")
    g1.add_attribute("R1", "A2", composed_of=["E1", "E2"], is_weak=True, is_pk=True)

    g1.add_is_a("E1", ["E3"], is_total=True, is_disjunct=True)

    g2 = ER()

    g2.add_entity("E3", is_multiple=False, is_weak=True)
    g2.add_entity("E4", is_multiple=False, is_weak=False)
    g2.add_entity("E5", is_multiple=False, is_weak=False)

    g2.add_relation(
        {
            "E3": "1",
        },
        "R2",
        {"E4": "1", "E1": {"cardinality": "1", "is_weak": True}},
    )

    g2.add_attribute("E3", "A3")
    g2.add_attribute("R2", "A4", composed_of=["E3", "E4"], is_weak=True, is_pk=True)

    g2.add_is_a("E3", ["E5"], is_total=True, is_disjunct=True)

    g = merge_er_diagrams(g1, g2)
