from __future__ import annotations

from typeguard import typechecked
from Levenshtein import ratio, setratio
from typing import Optional, Any
import copy

import erdiagram

scores = dict()
ratio_threshold = 0


@typechecked
def grade_submission(
    solution: erdiagram.ER,
    submission: erdiagram.ER,
    *,
    score_missing_entity: float = 1,
    score_missing_attribute: float = 1,
    score_missing_composed_attribute: float = 1,
    score_missing_relation: float = 1,
    score_missing_is_a: float = 1,
    score_missing_entity_property: float = 0.5,
    score_missing_attribute_property: float = 0.25,
    score_missing_composed_attribute_property: float = 0.125,
    score_missing_relation_property: float = 0.5,
    score_missing_is_a_property: float = 0.25,
    label_ratio_threshold: float = 0.8,
) -> tuple[float, str]:
    """
    Grades a submission given a solution. Returns the score.

    Parameters
    ----------
    solution : erdiagram.ER
        The solution diagram.
    submission : erdiagram.ER
        The submission diagram.
    score_missing_entity : float, optional
        The score to be deducted for each missing entity, by default 1
    score_missing_attribute : float, optional
        The score to be deducted for each missing attribute, by default 1
    score_missing_composed_attribute : float, optional
        The score to be deducted for each missing composed attribute, by default 1
    score_missing_relation : float, optional
        The score to be deducted for each missing relation, by default 1
    score_missing_is_a : float, optional
        The score to be deducted for each missing is-a relation, by default 1
    score_missing_entity_property : float, optional
        The score to be deducted for each missing entity property, by default 0.5
    score_missing_attribute_property : float, optional
        The score to be deducted for each missing attribute property, by default 0.25
    score_missing_composed_attribute_property : float, optional
        The score to be deducted for each missing composed attribute property, by default 0.125
    score_missing_relation_property : float, optional
        The score to be deducted for each missing relation property, by default 0.5
    score_missing_is_a_property : float, optional
        The score to be deducted for each missing is-a relation property, by default 0.25
    label_ratio_threshold : float, optional
        The minimum label ratio for two entities to be considered equal, by default 0.8

    Returns
    -------
    tuple[float, str]
        The score and the grading log.
    """
    global scores
    scores = {
        "missing_entity": score_missing_entity,
        "missing_attribute": score_missing_attribute,
        "missing_composed_attribute": score_missing_composed_attribute,
        "missing_relation": score_missing_relation,
        "missing_is_a": score_missing_is_a,
        "missing_entity_property": score_missing_entity_property,
        "missing_attribute_property": score_missing_attribute_property,
        "missing_composed_attribute_property": score_missing_composed_attribute_property,
        "missing_relation_property": score_missing_relation_property,
        "missing_is_a_property": score_missing_is_a_property,
    }
    global ratio_threshold
    ratio_threshold = label_ratio_threshold

    score = 0
    log = ""

    # Grade entities
    sub_score, sub_log = _grade_entities(solution, submission)
    score += sub_score
    log += sub_log

    # Grade relations
    sub_score, sub_log = _grade_relations(solution, submission)
    score += sub_score
    log += sub_log

    # Grade is-a relations
    sub_score, sub_log = _grade_is_as(solution, submission)
    score += sub_score
    log += sub_log

    # Grade attributes
    sub_score, sub_log = _grade_attributes(solution, submission)
    score += sub_score
    log += sub_log

    return score, log


def _grade_entity_pair(
    entity_pair: tuple[dict[str, Any], dict[str, Any]],
    solution: erdiagram.ER,
    submission: erdiagram.ER,
) -> Optional[tuple[float, str]]:
    """
    Grades a pair of entities.

    Parameters
    ----------
    entity_pair : tuple[dict[str, Any], dict[str, Any]]
        The pair of entities to grade. (solution_entity, submission_entity)
    solution : erdiagram.ER
        The solution diagram.
    submission : erdiagram.ER
        The submission diagram

    Returns
    -------
    Optional[tuple[float, str]]
        The score and the grading log. None if the entities are not comparable.
    """
    score = 0
    log = ""

    solution_entity, submission_entity = entity_pair
    original_solution_label, original_submission_label = (
        solution_entity["label"],
        submission_entity["label"],
    )
    solution_label, submission_label = sanitize(original_solution_label), sanitize(
        original_submission_label
    )
    label_ratio = ratio(solution_label, submission_label)

    if label_ratio < ratio_threshold:
        return None

    log += f"\t✓ Entity '{original_solution_label}' was found. (Matched against '{original_submission_label}' with a label ratio of {label_ratio:.2f}) \n"

    # Check properties `is_multiple` and `is_weak`
    if solution_entity["is_multiple"] != submission_entity["is_multiple"]:
        score += scores["missing_entity_property"]
        log += f"\t✗ Entity '{original_solution_label}' should be {'multiple' if solution_entity['is_multiple'] else 'not multiple'}. ({scores['missing_entity_property']})\n"
    else:
        log += f"\t✓ Entity '{original_solution_label}' is {'multiple' if solution_entity['is_multiple'] else 'not multiple'}.\n"

    if solution_entity["is_weak"] != submission_entity["is_weak"]:
        score += scores["missing_entity_property"]
        log += f"\t✗ Entity '{original_solution_label}' should be {'weak' if solution_entity['is_weak'] else 'not weak'}. ({scores['missing_entity_property']})\n"
    else:
        log += f"\t✓ Entity '{original_solution_label}' is {'weak' if solution_entity['is_weak'] else 'not weak'}.\n"

    return score, log


@typechecked
def _grade_entities(
    solution: erdiagram.ER, submission: erdiagram.ER
) -> tuple[float, str]:
    """
    Grades the entities of a submission given a solution. Returns the score.

    Parameters
    ----------
    solution : erdiagram.ER
        The solution diagram.
    submission : erdiagram.ER
        The submission diagram.

    Returns
    -------
    tuple[float, str]
        The score and the grading log.
    """
    score = 0
    log = ""

    # determine a grade for each entity in the submission
    for solution_entity in solution.get_entities():
        solution_label = solution_entity["label"]
        log += f"\n» Searching for entity {solution_label} in submission.\n"

        graded_entity_pairs = [
            _grade_entity_pair(
                (solution_entity, submission_entity), solution, submission
            )
            for submission_entity in submission.get_entities()
        ]
        graded_entity_pairs = [pair for pair in graded_entity_pairs if pair is not None]
        if len(graded_entity_pairs) > 0:  # entity found
            sub_score, sub_log = min(graded_entity_pairs, key=lambda pair: pair[0])
            score += sub_score
            log += sub_log
            continue

        # entity not found
        log += f"\t✗ Entity '{solution_label}' not found in submission. ({scores['missing_entity']})\n"
        score += scores["missing_entity"]

    return score, log


@typechecked
def __parse_cardinality(s: str) -> Optional[int | str | tuple[int | str, int | str]]:
    """
    Parses a string and returns the corresponding value.

    Parameters
    ----------
    s : str
        The string to parse.

    Returns
    -------
    Optional[int | str | tuple[int | str, int | str]]
        The parsed value. None if the string could not be parsed.
    """
    # Remove any whitespace from the string
    s = s.replace(" ", "")

    # To lowercase
    s = s.lower()

    if s.isdigit():
        # The string represents an integer
        return int(s)
    elif s.isalpha():
        # The string represents a single character string
        # return s
        return "n"
    elif s.startswith("(") and s.endswith(")"):
        # The string represents a tuple of two values
        parts = s[1:-1].split(",")
        if len(parts) != 2:
            return None
        val1 = parts[0].strip()
        val2 = parts[1].strip()
        if val1.isdigit() and val2.isdigit():
            return (int(val1), int(val2))
        elif val1.isdigit() and val2.isalpha():
            # return (int(val1), val2)
            return (int(val1), "n")
        elif val1.isalpha() and val2.isdigit():
            return ("n", int(val2))
            # return (val1, int(val2))
        else:
            return ("n", "n")
            # return (val1, val2)
    else:
        return None


@typechecked
def _grade_relation_pair(
    relation_pair: tuple[dict[str, Any], dict[str, Any]],
    solution: erdiagram.ER,
    submission: erdiagram.ER,
) -> Optional[tuple[float, str]]:
    """
    Grades a pair of relations.

    Parameters
    ----------
    relation_pair : tuple[dict[str, Any], dict[str, Any]]
        The pair of relations to grade. (solution_relation, submission_relation)
    solution : erdiagram.ER
        The solution diagram.
    submission : erdiagram.ER
        The submission diagram

    Returns
    -------
    Optional[tuple[float, str]]
        The score and the grading log. None if the relations are not comparable.
    """
    score = 0
    log = ""

    solution_relation, submission_relation = relation_pair
    original_solution_label, original_submission_label = (
        solution_relation["label"],
        submission_relation["label"],
    )
    solution_label, submission_label = sanitize(original_solution_label), sanitize(
        original_submission_label
    )
    label_ratio = ratio(solution_label, submission_label)

    log += f"\t✓ Relation '{original_solution_label} found. (Matched against '{original_submission_label}' with a label ratio of {label_ratio:.2f}) \n"

    transform_dict_to_list = lambda x: [{"label": k, **v} for k, v in x.items()]
    from_entities_solution = transform_dict_to_list(solution_relation["from_entities"])
    from_entities_submission = transform_dict_to_list(
        submission_relation["from_entities"]
    )
    to_entities_solution = transform_dict_to_list(solution_relation["to_entities"])
    to_entities_submission = transform_dict_to_list(submission_relation["to_entities"])

    entities_solution = from_entities_solution + to_entities_solution
    entities_submission = from_entities_submission + to_entities_submission

    # for each entity in either list, add a ID (so make it tuple(ID, entity))
    entities_solution = [(i, entity) for i, entity in enumerate(entities_solution)]
    entities_submission = [(i, entity) for i, entity in enumerate(entities_submission)]

    entity_pairs_dict = (
        list()
    )  # from solution entity find all possible submission entities
    for solution_entity in entities_solution:
        candidates = []
        for submission_entity in entities_submission:
            if (
                ratio(
                    sanitize(solution_entity[1]["label"]),
                    sanitize(submission_entity[1]["label"]),
                )
                > 0.8
            ):
                candidates.append(submission_entity)
        entity_pairs_dict.append((solution_entity, candidates))

    # sort above dictionary by length of value list, ascending, to a list of tuple(key, list)
    entity_pairs = sorted(entity_pairs_dict, key=lambda x: len(x[1]))

    def grade_relation_entity_pair(
        solution_entity: dict[str, Any],
        submission_entity: dict[str, Any],
        cardinality_letter_map: dict[str, str],
    ) -> tuple[tuple[float, str], dict[str, str]]:
        score = 0.0
        log = ""
        cardinality_letter_map = copy.deepcopy(cardinality_letter_map)

        original_solution_entity_label = solution_entity["label"]
        original_submission_entity_label = submission_entity["label"]
        solution_entity_label = sanitize(original_solution_entity_label)
        submission_entity_label = sanitize(original_submission_entity_label)
        label_ratio = ratio(solution_entity_label, submission_entity_label)

        log += f"\t✓ Relation '{original_solution_label}' has an entity '{original_solution_entity_label}' comparable to '{original_submission_entity_label}' with a label ratio of {label_ratio:.2f}.\n"

        # check for the same cardinality
        solution_entity_cardinality = __parse_cardinality(
            str(solution_entity["cardinality"])
        )
        submission_entity_cardinality = __parse_cardinality(
            str(submission_entity["cardinality"])
        )

        # check if we can map the cardinality letter to the solution cardinality, and if so, map it
        if isinstance(solution_entity_cardinality, str) and isinstance(
            submission_entity_cardinality, str
        ):
            if submission_entity_cardinality not in cardinality_letter_map:
                cardinality_letter_map[
                    submission_entity_cardinality
                ] = solution_entity_cardinality
            submission_entity_cardinality = cardinality_letter_map[
                submission_entity_cardinality
            ]
        elif isinstance(solution_entity_cardinality, tuple) and isinstance(
            submission_entity_cardinality, tuple
        ):
            new_submission_cardinality_tuple = []
            for index in range(2):
                sol_idx = solution_entity_cardinality[index]
                sub_idx = submission_entity_cardinality[index]
                if isinstance(sol_idx, str) and isinstance(sub_idx, str):
                    if sub_idx not in cardinality_letter_map:
                        cardinality_letter_map[sub_idx] = sol_idx
                    new_submission_cardinality_tuple.append(
                        cardinality_letter_map[sub_idx]
                    )
                else:
                    new_submission_cardinality_tuple.append(sub_idx)
            submission_entity_cardinality = tuple(new_submission_cardinality_tuple)

        # Check if the cardinality is the same
        if solution_entity_cardinality != submission_entity_cardinality:
            score += scores["missing_relation_property"]
            log += f"\t✗ Relation '{original_solution_label}' should have an entity '{original_solution_entity_label}' with cardinality '{solution_entity_cardinality}', but has '{submission_entity_cardinality}'. ({scores['missing_relation_property']})\n"

        # check for the same is_weak
        solution_entity_is_weak = solution_entity["is_weak"]
        submission_entity_is_weak = submission_entity["is_weak"]
        if solution_entity_is_weak != submission_entity_is_weak:
            score += scores["missing_relation_property"]
            log += f"\t✗ Relation '{original_solution_label}' should be connected to entity '{original_solution_entity_label}' {'weak' if solution_entity_is_weak else 'not weak'}, but is {'weak' if submission_entity_is_weak else 'not weak'}. ({scores['missing_relation_property']})\n"

        return ((score, log), cardinality_letter_map)

    def grade_all_relation_entity_pairs(
        entity_pairs: list[
            tuple[tuple[int, dict[str, Any]], list[tuple[int, dict[str, Any]]]]
        ],
        already_matched_submission_entities: list[int],
        cardinality_letter_map: dict[str, str],
    ) -> tuple[float, str]:
        entity_pairs = copy.deepcopy(entity_pairs)
        already_matched_submission_entities = copy.deepcopy(
            already_matched_submission_entities
        )
        score = 0.0
        log = ""
        cardinality_letter_map = copy.deepcopy(cardinality_letter_map)

        if len(entity_pairs) == 0:
            return (score, log)

        # pop first pair
        (_, solution_entity), submission_entities = entity_pairs.pop(0)
        original_solution_entity_label = solution_entity["label"]

        # remove alrady matched entities from submission_entities
        submission_entities = [
            (id, entity)
            for id, entity in submission_entities
            if id not in already_matched_submission_entities
        ]

        if len(submission_entities) == 0:
            score += scores["missing_relation_property"] * 3
            log += f"\t✗ Relation '{original_solution_label}' should have an entity '{original_solution_entity_label}'. ({scores['missing_relation_property'] * 3})\n"
            remaining_score, remaining_log = grade_all_relation_entity_pairs(
                entity_pairs,
                already_matched_submission_entities,
                cardinality_letter_map,
            )
            return (score + remaining_score, log + remaining_log)

        branches = []
        for submission_entity_id, submission_entity in submission_entities:
            branch = grade_relation_entity_pair(
                solution_entity, submission_entity, cardinality_letter_map
            )
            branches.append((branch, submission_entity_id))

        # grade remaining entity pairs recursively
        graded_branches = []
        for (
            (current_score, current_log),
            current_cardinality_letter_map,
        ), submission_entity_id in list(branches):
            remaining_score, remaining_log = grade_all_relation_entity_pairs(
                entity_pairs,
                already_matched_submission_entities + [submission_entity_id],
                current_cardinality_letter_map,
            )
            graded_branches.append(
                (current_score + remaining_score, current_log + remaining_log)
            )

        # get best branch by min score
        best_branch = min(graded_branches, key=lambda x: x[0])

        return best_branch

    score, log = grade_all_relation_entity_pairs(entity_pairs, list(), dict())

    return score, log


@typechecked
def _grade_relations(
    solution: erdiagram.ER, submission: erdiagram.ER
) -> tuple[float, str]:
    """
    Grades the relations of a submission given a solution. Returns the score.

    Parameters
    ----------
    solution : erdiagram.ER
        The solution diagram.
    submission : erdiagram.ER
        The submission diagram.

    Returns
    -------
    tuple[float, str]
        The score and the grading log.
    """
    score = 0
    log = ""

    for solution_relation in solution.get_relations():
        solution_label = solution_relation["label"]
        log += f"\n» Searching for relation {solution_label} in submission.\n"

        graded_relation_pairs = [
            _grade_relation_pair(
                (solution_relation, submission_relation), solution, submission
            )
            for submission_relation in submission.get_relations()
        ]
        graded_relation_pairs = [
            pair for pair in graded_relation_pairs if pair is not None
        ]
        if len(graded_relation_pairs) > 0:  # relation found
            sub_score, sub_log = min(graded_relation_pairs, key=lambda pair: pair[0])
            score += sub_score
            log += sub_log
            continue

        # Score missing node
        s = scores["missing_relation"] * (
            len(solution_relation["from_entities"])
            * len(solution_relation["to_entities"])
        )
        score += s
        # relation not found
        log += f"\t✗ Relation '{solution_label}' not found in submission. ({s})\n"

    return score, log


@typechecked
def _grade_is_as(solution: erdiagram.ER, submission: erdiagram.ER) -> tuple[float, str]:
    """
    Grades the is-a relations of a submission given a solution. Returns the score.

    Parameters
    ----------
    solution : erdiagram.ER
        The solution diagram.
    submission : erdiagram.ER
        The submission diagram.

    Returns
    -------
    tuple[float, str]
        The score and the grading log.
    """
    score = 0
    log = ""
    for solution_is_a in solution.get_is_as():
        solution_super_label = solution.get_entity_by_id(
            solution_is_a["superclass_id"]
        )["label"]
        solution_sub_labels = [
            solution.get_entity_by_id(sub_id)["label"]
            for sub_id in solution_is_a["subclass_ids"]
        ]

        log += f"\n» Searching for is-a relation {solution_super_label} -> {solution_sub_labels} in submission.\n"

        submission_is_a = max(
            filter(
                lambda pair: pair[1] > ratio_threshold,
                [
                    (
                        possible_submission_is_a,
                        ratio(
                            sanitize(solution_super_label),
                            sanitize(
                                submission.get_entity_by_id(
                                    possible_submission_is_a["superclass_id"]
                                )["label"]
                            ),
                        ),
                    )
                    for possible_submission_is_a in submission.get_is_as()
                ],
            ),
            key=lambda pair: pair[1],
            default=None,
        )
        if submission_is_a is None:
            s = scores["missing_is_a"]
            score += s
            log += f"\t✗ Is-a relation {solution_super_label} -> {solution_sub_labels} not found in submission. ({s})\n"
            continue

        log += f"\t✓ Is-a relation {solution_super_label} -> {solution_sub_labels} found in submission. (Matched against {submission.get_entity_by_id(submission_is_a[0]['superclass_id'])['label']} -> {[submission.get_entity_by_id(sub_id)['label'] for sub_id in submission_is_a[0]['subclass_ids']]} with a ratio of {submission_is_a[1]:.2f})\n"

        # check if the subclasses are the same
        submission_super_label = submission.get_entity_by_id(
            submission_is_a[0]["superclass_id"]
        )["label"]
        submission_sub_labels = [
            submission.get_entity_by_id(sub_id)["label"]
            for sub_id in submission_is_a[0]["subclass_ids"]
        ]

        set_ratio = setratio(
            list(set([sanitize(label) for label in solution_sub_labels])),
            list(set([sanitize(label) for label in submission_sub_labels])),
        )

        if set_ratio < ratio_threshold:
            s = scores["missing_is_a_property"] * len(solution_sub_labels) * set_ratio
            score += s
            log += f"\t✗ The is-a relation {solution_super_label} -> {solution_sub_labels} is not comparable to {submission_super_label} -> {submission_sub_labels} with a set ratio of {set_ratio:.2f}. ({s})\n"

        # check if the custom text is the same
        solution_custom_text = solution_is_a["custom_text"]
        submission_custom_text = submission_is_a[0]["custom_text"]
        if (solution_custom_text is not None and submission_custom_text is None) or (
            solution_custom_text is None and submission_custom_text is not None
        ):
            log += f"\t✗ The is-a relation {solution_super_label} -> {solution_sub_labels} should{' not' if solution_custom_text is None else ''} have a custom text. ({scores['missing_is_a_property']})\n"
            score += scores["missing_is_a_property"]
        elif solution_custom_text is not None and submission_custom_text is not None:
            label_ratio = ratio(
                sanitize(solution_custom_text), sanitize(submission_custom_text)
            )
            if label_ratio < ratio_threshold:
                s = scores["missing_is_a_property"] * label_ratio
                score += s
                log += f"\t✗ The is-a relation {solution_super_label} -> {solution_sub_labels} has a custom text with a ratio of {label_ratio:.2f}. ({s})\n"

        # check if `is_total` and `is_disjunct` are the same
        if solution_is_a["is_total"] != submission_is_a[0]["is_total"]:
            log += f"\t✗ The is-a relation {solution_super_label} -> {solution_sub_labels} should{'' if solution_is_a['is_total'] else ' not'} be total. ({scores['missing_is_a_property']})\n"
            score += scores["missing_is_a_property"]
        if solution_is_a["is_disjunct"] != submission_is_a[0]["is_disjunct"]:
            log += f"\t✗ The is-a relation {solution_super_label} -> {solution_sub_labels} should{'' if solution_is_a['is_disjunct'] else ' not'} be disjunct. ({scores['missing_is_a_property']})\n"
            score += scores["missing_is_a_property"]

    return score, log


@typechecked
def _grade_attributes(
    solution: erdiagram.ER, submission: erdiagram.ER
) -> tuple[float, str]:
    """
    Grades the attributes of a submission given a solution. Returns the score.

    Parameters
    ----------
    solution : erdiagram.ER
        The solution diagram.
    submission : erdiagram.ER
        The submission diagram.

    Returns
    -------
    tuple[float, str]
        The score and the grading log.
    """
    score = 0
    log = ""
    for solution_attribute in solution.get_attributes():
        solution_attribute_label = solution_attribute["label"]
        solution_parent_label = solution.get_label_by_id(
            solution_attribute["parent_id"]
        )
        solution_parent_type = solution_attribute["parent_type"]

        log += f"\n» Searching for attribute {solution_attribute_label} of {str(solution_parent_type).lower()} {solution_parent_label} in submission.\n"

        # Filter possible attributes by parent type and ratio threshold
        filtered_attributes = list(
            filter(
                lambda pair: pair[1] >= ratio_threshold,
                [
                    (
                        possible_submission_attribute,
                        ratio(
                            sanitize(solution_parent_label),
                            sanitize(
                                submission.get_label_by_id(
                                    possible_submission_attribute["parent_id"]
                                )
                            ),
                        ),
                    )
                    for possible_submission_attribute in submission.get_attributes()
                    if possible_submission_attribute["parent_type"]
                    == solution_parent_type
                ],
            )
        )

        # Find maximal ratio value
        max_ratio = max([pair[1] for pair in filtered_attributes], default=None)

        # Filter attributes with maximal ratio value
        maximal_attributes = [
            pair[0] for pair in filtered_attributes if pair[1] == max_ratio
        ]

        # Filter the attributes by label ratio above threshold, and get the one with maximal label ratio
        submission_attribute = max(
            list(
                filter(
                    lambda pair: pair[1] >= ratio_threshold,
                    [
                        (
                            possible_submission_attribute,
                            ratio(
                                sanitize(solution_attribute_label),
                                sanitize(possible_submission_attribute["label"]),
                            ),
                        )
                        for possible_submission_attribute in maximal_attributes
                    ],
                )
            ),
            key=lambda pair: pair[1],
            default=None,
        )

        if submission_attribute is None:
            s = scores["missing_attribute"]
            score += s
            log += f"\t✗ Attribute {solution_attribute_label} of {str(solution_parent_type).lower()} {solution_parent_label} not found in submission.({s})\n"
            continue

        log += f"\t✓ Attribute {solution_attribute_label} of {str(solution_parent_type).lower()} {solution_parent_label} found in submission. (Matched against submission attribute {submission_attribute[0]['label']} of {str(submission_attribute[0]['parent_type']).lower()} {submission.get_label_by_id(submission_attribute[0]['parent_id'])} with ratio {submission_attribute[1]:.2f})\n"

        # check if `is_pk`, `is_multiple`, and `is_weak` are the same
        if solution_attribute["is_pk"] != submission_attribute[0]["is_pk"]:
            log += f"\t✗ The attribute {solution_attribute_label} of {str(solution_parent_type).lower()} {solution_parent_label} should{'' if solution_attribute['is_pk'] else ' not'} be a primary key. ({scores['missing_attribute_property']})\n"
            score += scores["missing_attribute_property"]
        if solution_attribute["is_multiple"] != submission_attribute[0]["is_multiple"]:
            log += f"\t✗ The attribute {solution_attribute_label} of {str(solution_parent_type).lower()} {solution_parent_label} should{'' if solution_attribute['is_multiple'] else ' not'} be multiple. ({scores['missing_attribute_property']})\n"
            score += scores["missing_attribute_property"]
        if (
            solution_attribute["is_pk"]
            and solution_attribute["is_weak"] != submission_attribute[0]["is_weak"]
        ):
            log += f"\t✗ The attribute {solution_attribute_label} of {str(solution_parent_type).lower()} {solution_parent_label} should{'' if solution_attribute['is_weak'] else ' not'} be weak. ({scores['missing_attribute_property']})\n"
            score += scores["missing_attribute_property"]

        solution_composed_attribute_labels = [
            sanitize(solution.get_label_by_id(composed_attribute_id))
            for composed_attribute_id in solution_attribute["composed_of_attribute_ids"]
        ]
        submission_composed_attribute_labels = [
            sanitize(submission.get_label_by_id(composed_attribute_id))
            for composed_attribute_id in submission_attribute[0][
                "composed_of_attribute_ids"
            ]
        ]
        set_ratio = setratio(
            list(set(solution_composed_attribute_labels)),
            list(set(submission_composed_attribute_labels)),
        )
        if set_ratio < ratio_threshold:
            s = (
                scores["missing_composed_attribute"]
                * len(solution_attribute["composed_of_attribute_ids"])
                * set_ratio
            )
            score += s
            log += f"\t✗ The attribute {solution_attribute_label} of {str(solution_parent_type).lower()} {solution_parent_label} has a different composition. ({s})\n"

    return score, log


@typechecked
def sanitize(s: str) -> str:
    """
    Sanitizes a string for comparison.

    Parameters
    ----------
    s : str
        The string to sanitize.

    Returns
    -------
    str
        The sanitized string.
    """
    return s.lower().strip().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
