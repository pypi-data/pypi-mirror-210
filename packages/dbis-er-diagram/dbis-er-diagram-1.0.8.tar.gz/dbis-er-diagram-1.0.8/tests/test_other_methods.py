import pytest

from erdiagram import ER


def test_as_solution():
    g = ER()
    g.add_entity("E1", is_multiple=True, is_weak=True)
    g.add_entity("E2", is_multiple=True, is_weak=False)
    g.add_entity("E3", is_multiple=False, is_weak=True)
    g.add_entity("E4", is_multiple=False, is_weak=False)

    g.add_relation(
        {
            "E1": "1",
        },
        "R1",
        {
            "E2": "1",
        },
    )
    g.add_relation(
        {
            "E3": "1",
        },
        "R2",
        {"E4": "1", "E1": {"cardinality": "1", "is_weak": True}},
    )

    g.add_attribute("E1", "A1")
    g.add_attribute("R1", "A2", composed_of=["E1", "E2"], is_weak=True, is_pk=True)

    g.add_is_a("E1", ["E3", "E4"], is_total=True, is_disjunct=True)
    g.add_is_a(
        "E2", ["E3", "E4"], is_total=False, is_disjunct=False, custom_text="custom"
    )

    solution = g.as_solution(format="json")
    solution_2 = g.as_solution(format="none")

    assert type(solution) == dict
    assert type(solution_2) == str
