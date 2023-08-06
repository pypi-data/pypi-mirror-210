import pytest

from erdiagram import ER, grade_submission


def test_relation():
    solution = ER()

    solution.add_entity("S")
    solution.add_entity("Bewertung")
    solution.add_relation({"S": "1"}, "hat", {"Bewertung": "n"})

    submission = ER()
    submission.add_entity("S")
    submission.add_entity("Bewertung")
    submission.add_relation({"S": "1"}, "fsdfsdfsdfsdf", {"Bewertung": "n"})

    score, log = grade_submission(solution, submission)
    assert score == 0


def test_is_a():
    solution = ER()
    solution.add_is_a("A", ["B", "C", "D"], is_total=True, is_disjunct=True)
    submission = ER()
    submission.add_is_a("A", ["C", "D", "B"], is_total=True, is_disjunct=True)
    score, log = grade_submission(solution, submission)
    assert score == 0


def test_levenshtein():
    solution = ER()
    solution.add_is_a("A", ["Bewertung", "Schule"], is_total=True, is_disjunct=True)
    solution.add_attribute("Episode", "Titel")
    solution.add_attribute("Episode", "Bewertung_ID")

    submission = ER()
    submission.add_is_a("A", ["Bewertungs", "Schuule"], is_total=True, is_disjunct=True)
    submission.add_attribute("Episode", "Title")
    submission.add_attribute("Episode", "Bewertungs_ID")

    score, log = grade_submission(solution, submission)
    assert score == 0


def test_spaces_in_cardinalities():
    solution = ER()
    solution.add_entity("S")
    solution.add_entity("B")
    solution.add_entity("E")
    solution.add_relation({"S": "(1, 1)"}, "b", {"E": "n", "F": "(1, n)"})
    solution.add_relation({"E": "m"}, "sfsdf", {"B": "n"})

    submission = ER()
    submission.add_entity("S")
    submission.add_entity("B")
    submission.add_entity("E")
    submission.add_relation({"S": "(1,1)"}, "b", {"E": "n", "F": "(1,n)"})
    submission.add_relation({"E": "m"}, "sfsdf", {"B": "n"})

    score, log = grade_submission(solution, submission)
    assert score == 0
