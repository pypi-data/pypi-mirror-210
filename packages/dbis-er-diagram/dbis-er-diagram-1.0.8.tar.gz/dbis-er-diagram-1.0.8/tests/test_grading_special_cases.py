from erdiagram import ER, grade_submission


def test_renamed_cardinality_1_n():
    solution = ER()
    solution.add_relation({"A": "1"}, "R1", {"B": "n"})
    solution.add_relation({"C": "1"}, "R2", {"D": "n"})
    solution.add_relation({"E": "n"}, "R3", {"F": "n"})
    solution.add_relation({"G": "n"}, "R4", {"H": "m"})
    solution.add_relation({"I": "n"}, "R5", {"J": "1", "K": "1"})
    solution.add_relation({"L": "n"}, "R6", {"M": "1", "N": "m"})
    solution.add_relation({"O": "n"}, "R7", {"P": "1", "Q": "n"})
    solution.add_relation({"R": "n"}, "R8", {"S": "m", "T": "n"})
    solution.add_relation({"U": "n"}, "R9", {"V": "m", "W": "m"})

    submission = ER()
    submission.add_relation({"A": "1"}, "R1", {"B": "n"})
    submission.add_relation({"C": "1"}, "R2", {"D": "m"})
    submission.add_relation({"E": "m"}, "R3", {"F": "m"})
    submission.add_relation({"G": "m"}, "R4", {"H": "n"})
    submission.add_relation({"I": "m"}, "R5", {"J": "1", "K": "1"})
    submission.add_relation({"L": "m"}, "R6", {"M": "1", "N": "n"})
    submission.add_relation({"O": "m"}, "R7", {"P": "1", "Q": "m"})
    submission.add_relation({"R": "m"}, "R8", {"S": "n", "T": "m"})
    submission.add_relation({"U": "m"}, "R9", {"V": "n", "W": "n"})

    score, log = grade_submission(solution, submission)
    assert score == 0


def test_renamed_cardinality_min_max():
    solution = ER()
    solution.add_relation({"A": "(1, 1)"}, "R1", {"B": "(1, n)"})
    solution.add_relation({"C": "(1, 1)"}, "R2", {"D": "(1, n)"})
    solution.add_relation({"E": "(1, n)"}, "R3", {"F": "(1, n)"})
    solution.add_relation({"G": "(1, n)"}, "R4", {"H": "(1, m)"})
    solution.add_relation({"I": "(1, n)"}, "R5", {"J": "(n, m)"})
    solution.add_relation({"L": "(m, n)"}, "R6", {"M": "(1, 1)", "N": "(1, m)"})
    solution.add_relation({"O": "(1, m)"}, "R7", {"P": "(n, m)", "Q": "(1, n)"})
    solution.add_relation({"R": "(1, m)"}, "R8", {"S": "(m, n)", "T": "(1, m)"})
    solution.add_relation({"U": "(n,m)"}, "R9", {"V": "(m, n)", "W": "(m, m)"})
    solution.add_relation({"X": "(n,m) "}, "R10", {"Y": "(m, n)", "Z": "(1, n)"})

    submission = ER()
    submission.add_relation({"A": "(1, 1)"}, "R1", {"B": "(1, n)"})
    submission.add_relation({"C": "(1, 1)"}, "R2", {"D": "(1, m)"})
    submission.add_relation({"E": "(1, m)"}, "R3", {"F": "(1, m)"})
    submission.add_relation({"G": "(1, m)"}, "R4", {"H": "(1, n)"})
    submission.add_relation({"I": "(1, m)"}, "R5", {"J": "(m,n)"})
    submission.add_relation({"L": "(n, m)"}, "R6", {"M": "(1, 1)", "N": "(1, n)"})
    submission.add_relation({"O": "(1, n)"}, "R7", {"P": "(m, n)", "Q": "(1, m)"})
    submission.add_relation({"R": "(1, n)"}, "R8", {"S": "(n,m)", "T": "(1, n)"})
    submission.add_relation({"U": "(m,n) "}, "R9", {"V": "(n, m)", "W": "(n,n)"})
    submission.add_relation({"X": "(m,n)"}, "R10", {"Y": "(n,m)", "Z": "(1, m)"})

    score, log = grade_submission(solution, submission)
    assert score == 0


def test_pk_weak_attribute_incorrect():
    solution = ER()
    solution.add_entity("A", is_weak=True)
    solution.add_attribute("A", "attr", is_pk=True, is_weak=True)
    submission = ER()
    submission.add_entity("A", is_weak=True)
    submission.add_attribute("A", "attr", is_pk=True, is_weak=False)

    score, log = grade_submission(solution, submission)
    assert score > 0


def test_pk_weak_attribute_correct():
    solution = ER()
    solution.add_entity("A", is_weak=True)
    solution.add_attribute("A", "attr", is_pk=True, is_weak=True)
    submission = ER()
    submission.add_entity("A", is_weak=True)
    submission.add_attribute("A", "attr", is_pk=True, is_weak=True)

    score, log = grade_submission(solution, submission)
    assert score == 0


def test_non_pk_weak_attribute():
    solution = ER()
    solution.add_entity("A", is_weak=True)
    solution.add_attribute("A", "attr", is_pk=False, is_weak=True)
    solution.add_attribute("A", "attr2", is_pk=False, is_weak=True)
    solution.add_attribute("A", "attr3", is_pk=False, is_weak=False)
    solution.add_attribute("A", "attr4", is_pk=False, is_weak=False)
    submission = ER()
    submission.add_entity("A", is_weak=True)
    submission.add_attribute("A", "attr", is_pk=False, is_weak=True)
    submission.add_attribute("A", "attr2", is_pk=False, is_weak=False)
    submission.add_attribute("A", "attr3", is_pk=False, is_weak=True)
    submission.add_attribute("A", "attr4", is_pk=False, is_weak=False)

    score, log = grade_submission(solution, submission)
    assert score == 0


def test_relation_any_direction():
    solution = ER()
    # 1 from 1 to
    solution.add_relation({"A": "1"}, "R1", {"B": "n"})
    solution.add_relation({"A": "1"}, "R2", {"B": "n"})  # swap in submission
    # 1 from 2 to
    solution.add_relation({"C": "1"}, "R3", {"D": "n", "E": "n"})
    solution.add_relation(
        {"C": "1"}, "R4", {"D": "n", "E": "n"}
    )  # swap C,D in submission
    solution.add_relation(
        {"C": "1"}, "R5", {"D": "n", "E": "n"}
    )  # swap C,E in submission
    solution.add_relation(
        {"C": "1"}, "R6", {"D": "n", "E": "n"}
    )  # swap C,D+E in submission
    # 2 from 1 to
    solution.add_relation({"F": "n", "G": "n"}, "R7", {"H": "1"})
    solution.add_relation(
        {"F": "n", "G": "n"}, "R8", {"H": "1"}
    )  # swap F,H in submission
    solution.add_relation(
        {"F": "n", "G": "n"}, "R9", {"H": "1"}
    )  # swap G,H in submission
    solution.add_relation(
        {"F": "n", "G": "n"}, "R10", {"H": "1"}
    )  # swap F,G+H in submission
    # 2 from 2 to
    solution.add_relation({"I": "n", "J": "1"}, "R11", {"K": "m", "L": "n"})
    solution.add_relation(
        {"I": "n", "J": "1"}, "R12", {"K": "m", "L": "n"}
    )  # swap I,K in submission
    solution.add_relation(
        {"I": "n", "J": "1"}, "R13", {"K": "m", "L": "n"}
    )  # swap I,L in submission
    solution.add_relation(
        {"I": "n", "J": "1"}, "R14", {"K": "m", "L": "n"}
    )  # swap I,K+L in submission
    solution.add_relation(
        {"I": "n", "J": "1"}, "R15", {"K": "m", "L": "n"}
    )  # swap J,K in submission
    solution.add_relation(
        {"I": "n", "J": "1"}, "R16", {"K": "m", "L": "n"}
    )  # swap J,L in submission
    solution.add_relation(
        {"I": "n", "J": "1"}, "R17", {"K": "m", "L": "n"}
    )  # swap J,K+L in submission
    solution.add_relation(
        {"I": "n", "J": "1"}, "R18", {"K": "m", "L": "n"}
    )  # swap I+J,K in submission
    solution.add_relation(
        {"I": "n", "J": "1"}, "R19", {"K": "m", "L": "n"}
    )  # swap I+J,L in submission
    solution.add_relation(
        {"I": "n", "J": "1"}, "R20", {"K": "m", "L": "n"}
    )  # swap I+J,K+L in submission
    # self relation
    solution.add_relation({"M": "n"}, "R21", {"M": "1"})
    solution.add_relation({"M": "n"}, "R22", {"M": "1"})  # swap M,M in submission
    # self relation with a third entity
    solution.add_relation({"N": "n"}, "R23", {"N": "1", "O": "n"})
    solution.add_relation(
        {"N": "n"}, "R24", {"N": "1", "O": "n"}
    )  # swap N,N in submission
    solution.add_relation(
        {"N": "n"}, "R25", {"N": "1", "O": "n"}
    )  # swap N,O in submission
    solution.add_relation(
        {"N": "n"}, "R26", {"N": "1", "O": "n"}
    )  # swap N,N+O in submission

    submission = ER()
    # 1 from 1 to
    submission.add_relation({"A": "1"}, "R1", {"B": "n"})
    submission.add_relation({"B": "n"}, "R2", {"A": "1"})
    # 1 from 2 to
    submission.add_relation({"C": "1"}, "R3", {"D": "n", "E": "n"})
    submission.add_relation({"D": "n"}, "R4", {"C": "1", "E": "n"})
    submission.add_relation({"E": "n"}, "R5", {"C": "1", "D": "n"})
    submission.add_relation({"D": "n", "E": "n"}, "R6", {"C": "1"})
    # 2 from 1 to
    submission.add_relation({"F": "n", "G": "n"}, "R7", {"H": "1"})
    submission.add_relation({"H": "1", "G": "n"}, "R8", {"F": "n"})
    submission.add_relation({"F": "n", "H": "1"}, "R9", {"G": "n"})
    submission.add_relation({"F": "n", "G": "n"}, "R10", {"H": "1"})
    # 2 from 2 to
    submission.add_relation({"I": "n", "J": "1"}, "R11", {"K": "m", "L": "n"})
    submission.add_relation({"K": "m"}, "R12", {"I": "n", "L": "n"})
    submission.add_relation({"L": "n"}, "R13", {"I": "n", "K": "m"})
    submission.add_relation({"K": "m", "L": "n"}, "R14", {"I": "n", "J": "1"})
    submission.add_relation({"J": "1", "L": "n"}, "R15", {"I": "n", "K": "m"})
    submission.add_relation({"I": "n", "L": "n"}, "R16", {"J": "1", "K": "m"})
    submission.add_relation({"K": "m", "J": "1"}, "R17", {"I": "n", "L": "n"})
    submission.add_relation({"I": "n", "J": "1"}, "R18", {"K": "m", "L": "n"})
    submission.add_relation({"I": "n", "J": "1"}, "R19", {"K": "m", "L": "n"})
    submission.add_relation({"I": "n", "J": "1"}, "R20", {"K": "m", "L": "n"})
    # self relation
    submission.add_relation({"M": "n"}, "R21", {"M": "1"})
    submission.add_relation({"M": "1"}, "R22", {"M": "n"})
    # self relation with a third entity
    submission.add_relation({"N": "n"}, "R23", {"N": "1", "O": "n"})
    submission.add_relation({"N": "1"}, "R24", {"N": "n", "O": "n"})
    submission.add_relation({"O": "n"}, "R25", {"N": "1", "N": "n"})
    submission.add_relation({"N": "n", "O": "n"}, "R26", {"N": "1"})

    score, log = grade_submission(solution, submission)
    assert score == 0.0


def test_too_few_entities_self_relation():
    solution = ER()
    solution.add_relation({"A": "1"}, "R1", {"A": "m", "B": "n"})
    submission = ER()
    submission.add_relation({"A": "1"}, "R1", {"B": "n"})

    score, log = grade_submission(solution, submission)
    assert score > 0.0


def test_self_relation_same_cardinality():
    solution = ER()
    solution.add_relation({"A": "1"}, "R1", {"A": "1"})
    solution.add_relation({"B": "n"}, "R2", {"B": "n"})
    solution.add_relation({"C": "(1,2)"}, "R3", {"C": "(1,2)"})
    solution.add_relation({"D": "(1,n)"}, "R4", {"D": "(1,n)"})
    solution.add_relation({"E": "(n,m)"}, "R5", {"E": "(n,m)"})
    solution.add_relation({"F": "1"}, "R6", {"F": "1", "G": "n"})
    solution.add_relation({"G": "n"}, "R7", {"F": "1", "G": "n"})
    solution.add_relation({"H": "(1,2)"}, "R8", {"H": "(1,2)", "I": "(1,2)"})
    solution.add_relation({"I": "(1,n)"}, "R9", {"H": "(1,n)", "I": "(1,n)"})
    solution.add_relation({"J": "(n,m)"}, "R10", {"J": "(n,m)", "K": "(n,m)"})

    submission = ER()
    submission.add_relation({"A": "1"}, "R1", {"A": "1"})
    submission.add_relation({"B": "n"}, "R2", {"B": "n"})
    submission.add_relation({"C": "(1,2)"}, "R3", {"C": "(1,2)"})
    submission.add_relation({"D": "(1,n)"}, "R4", {"D": "(1,n)"})
    submission.add_relation({"E": "(n,m)"}, "R5", {"E": "(n,m)"})
    submission.add_relation({"F": "1"}, "R6", {"F": "1", "G": "n"})
    submission.add_relation({"G": "n"}, "R7", {"F": "1", "G": "n"})
    submission.add_relation({"H": "(1,2)"}, "R8", {"H": "(1,2)", "I": "(1,2)"})
    submission.add_relation({"I": "(1,n)"}, "R9", {"H": "(1,n)", "I": "(1,n)"})
    submission.add_relation({"J": "(n,m)"}, "R10", {"J": "(n,m)", "K": "(n,m)"})

    score, log = grade_submission(solution, submission)
    assert score == 0.0
