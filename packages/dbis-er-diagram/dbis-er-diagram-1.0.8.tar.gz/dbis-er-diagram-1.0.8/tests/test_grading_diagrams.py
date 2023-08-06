import pytest

from erdiagram import ER, grade_submission


def test_had_issue():
    solution = ER()
    solution.add_relation(
        {"Freizeitpark": "1"},
        "angestellt",
        {"Mitarbeiter": "n"},
    )
    solution.add_attribute("Mitarbeiter", "Gehalt")
    solution.add_attribute("Mitarbeiter", "Geschlecht")
    solution.add_attribute("Mitarbeiter", "PersonalNummer", is_pk=True)
    solution.add_relation(
        {"Mitarbeiter": "1"},
        "verwaltet",
        {"Mitarbeiter": "n"},
    )
    solution.add_is_a(
        "Mitarbeiter",
        ["Manager", "Mechaniker", "Animateur", "Kaufmann", "Koch"],
        is_total=False,
        is_disjunct=True,
    )
    submission = ER()
    submission.add_relation(
        {"Freizeitpark": "1"},
        "angestellt",
        {"Mitarbeiter": "n"},
    )
    submission.add_attribute("Mitarbeiter", "Gehalt")
    submission.add_attribute("Mitarbeiter", "Geschlecht")
    submission.add_attribute("Mitarbeiter", "PersonalNummer", is_pk=True)
    submission.add_relation(
        {"Mitarbeiter": "1"},
        "verwaltet",
        {"Mitarbeiter": "n"},
    )
    submission.add_is_a(
        "Mitarbeiter",
        ["Manager", "Mechaniker", "Animateur", "Kaufmann", "Koch"],
        is_total=False,
        is_disjunct=True,
    )
    score, log = grade_submission(solution, submission)
    assert score == 0


def test_exc_score_comparison():
    solution = ER()
    solution.add_entity("Hersteller")
    solution.add_attribute("Hersteller", "Name", is_pk=True)
    solution.add_attribute("Hersteller", "Sitz")  # 0.25 missing attribute
    solution.add_entity("Käse")  # 1p missing node

    submission = ER()
    submission.add_entity("Hersteller", is_weak=True)  # 0.5 Weak
    submission.add_attribute("Hersteller", "Name", is_pk=False)  # 0.25 PK

    score, log = grade_submission(
        solution,
        submission,
        score_missing_entity=1,
        score_missing_attribute=0.25,
        score_missing_composed_attribute=0.25,
        score_missing_relation=1,
        score_missing_is_a=1,
        score_missing_entity_property=0.5,
        score_missing_attribute_property=0.25,
        score_missing_composed_attribute_property=0.25,
        score_missing_relation_property=0.5,
        score_missing_is_a_property=0.25,
    )
    assert score == 2


def test_exc_a():
    solution = ER()
    solution.add_entity("A")
    solution.add_attribute("A", "A_ID", is_pk=True)
    solution.add_attribute("A", "B")
    solution.add_attribute("A", "C")
    solution.add_attribute("A", "D", is_multiple=True)

    submission = ER()
    submission.add_entity("A")

    score, log = grade_submission(
        solution,
        submission,
        score_missing_entity=1,
        score_missing_attribute=0.5,
        score_missing_composed_attribute=0.5,
        score_missing_relation=1,
        score_missing_is_a=1,
        score_missing_entity_property=0.5,
        score_missing_attribute_property=0.5,
        score_missing_composed_attribute_property=0.125,
        score_missing_relation_property=0.5,
        score_missing_is_a_property=0.25,
    )
    assert score == 2


def test_exc_b():
    solution = ER()
    solution.add_entity("E")
    solution.add_entity("F")
    solution.add_attribute("F", "F_ID", is_pk=True)
    solution.add_attribute("F", "G")
    solution.add_attribute("F", "H")
    solution.add_attribute("F", "I")
    solution.add_relation({"E": "1"}, "hat", {"F": "n"})

    submission = ER()
    submission.add_entity("E")
    submission.add_entity("F")

    score, log = grade_submission(
        solution,
        submission,
        score_missing_entity=1,
        score_missing_attribute=0.25,
        score_missing_composed_attribute=0.25,
        score_missing_relation=1,
        score_missing_is_a=1,
        score_missing_entity_property=0.5,
        score_missing_attribute_property=0.25,
        score_missing_composed_attribute_property=0.25,
        score_missing_relation_property=0.5,
        score_missing_is_a_property=0.25,
    )
    assert score == 2


def test_exc_c():
    solution = ER()

    solution.add_entity("U")
    solution.add_entity("V")
    solution.add_entity("W")
    solution.add_attribute("W", "W_ID", is_pk=True)
    solution.add_attribute("W", "A")
    solution.add_attribute("W", "B")
    solution.add_attribute("W", "C")
    solution.add_relation({"U": "1"}, "y", {"W": "n"})
    solution.add_relation({"V": "n"}, "x", {"U": "m"})

    submission = ER()
    submission.add_entity("U")
    submission.add_entity("V")
    submission.add_entity("W")

    score, log = grade_submission(
        solution,
        submission,
        score_missing_entity=1,
        score_missing_attribute=0.25,
        score_missing_composed_attribute=0.25,
        score_missing_relation=1,
        score_missing_is_a=1,
        score_missing_entity_property=0.5,
        score_missing_attribute_property=0.25,
        score_missing_composed_attribute_property=0.25,
        score_missing_relation_property=0.5,
        score_missing_is_a_property=0.25,
    )
    assert score == 3


def test_exc_d():
    solution = ER()
    solution.add_entity("I")
    solution.add_entity("J")
    solution.add_entity("K", is_weak=True)
    solution.add_attribute("K", "K_ID", is_pk=True)
    solution.add_attribute("K", "K2")
    solution.add_attribute("J", "J1", is_pk=True)
    solution.add_attribute("J", "JC", composed_of=["JC1", "JC2"])
    solution.add_relation({"J": "1"}, "sss", {"K": "n", "I": "n"})
    solution.add_relation({"K": "1"}, "AA", {"K": "n"})
    solution.add_relation(
        {"I": "1"}, "eee", {"K": {"cardinality": "n", "is_weak": True}}
    )

    submission = ER()
    submission.add_entity("I")
    submission.add_entity("J")

    score, log = grade_submission(
        solution,
        submission,
        score_missing_entity=1,
        score_missing_attribute=0.25,
        score_missing_composed_attribute=0.25,
        score_missing_relation=1,
        score_missing_is_a=1,
        score_missing_entity_property=0.5,
        score_missing_attribute_property=0.25,
        score_missing_composed_attribute_property=0.25,
        score_missing_relation_property=0.5,
        score_missing_is_a_property=0.25,
    )
    assert score == 6


def test_exc_e():
    solution = ER()
    solution.add_entity("S")
    solution.add_relation({"S": "1"}, "hat", {"G": "n"})
    solution.add_attribute("G", "G_ID", is_pk=True)
    solution.add_is_a("G", ["A", "B", "C", "D"], is_total=False, is_disjunct=False)

    submission = ER()
    submission.add_entity("S")

    score, log = grade_submission(
        solution,
        submission,
        score_missing_entity=0.5,
        score_missing_attribute=0.5,
        score_missing_composed_attribute=0.5,
        score_missing_relation=0.5,
        score_missing_is_a=0.5,
        score_missing_entity_property=0.5,
        score_missing_attribute_property=0.5,
        score_missing_composed_attribute_property=0.125,
        score_missing_relation_property=0.25,
        score_missing_is_a_property=0.25,
    )
    assert score == 4
