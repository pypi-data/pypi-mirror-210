import copy
import itertools
import random

from erdiagram import ER, NodeType


def powerset(iterable, include_empty_set=True):
    s = list(iterable)
    return [
        list(comb)
        for r in range(0 if include_empty_set else 1, len(s) + 1)
        for comb in itertools.combinations(s, r)
    ]


def test_get_entity():
    for is_multiple, is_weak in itertools.product([True, False], repeat=2):
        g = ER()
        assert len(g.get_entities()) == 0
        g.add_entity("A", is_multiple=is_multiple, is_weak=is_weak)
        assert len(g.get_entities()) == 1

        # The same entity should be returned regardless of the way it is retrieved.
        entity_by_label = g.get_entity_by_label("A")
        entity_id = entity_by_label["id"]
        entity_by_id = g.get_entity_by_id(entity_id)
        assert entity_by_id == entity_by_label

        entity = entity_by_id

        # Test the format of the entity.
        assert isinstance(entity, dict)
        assert set(entity.keys()) == {
            "id",
            "label",
            "is_multiple",
            "is_weak",
            "node_type",
            "attribute_ids",
            "relation_ids_from",
            "relation_ids_to",
            "is_a_super_id",
            "is_a_sub_id",
        }
        assert entity["id"] == entity_id
        assert entity["label"] == "A"
        assert entity["is_multiple"] == is_multiple
        assert entity["is_weak"] == is_weak
        assert entity["node_type"] == NodeType.ENTITY
        assert entity["attribute_ids"] == []
        assert entity["relation_ids_from"] == []
        assert entity["relation_ids_to"] == []
        assert entity["is_a_super_id"] == None
        assert entity["is_a_sub_id"] == None


def test_get_relation():
    # use itertools to get all combinations of the following:
    # either 1 or 2 entities from
    # either 1 or 2 entities to
    # for each entity either is_weak true or false
    # for each entity (if is_weak is false) either format 1 or format 2
    # then also use random to select random cardinality for each entity (number or "n" or "m")
    # Create a function that generates all possible dicts to create a single entity
    def generate_entity_dicts(name):
        options = list()
        for is_weak, format in [(True, True), (False, True), (False, False)]:
            cardinality = random.choice(["n", "m"] + [str(i) for i in range(1, 10)])
            if format:
                options.append({name: {"cardinality": cardinality, "is_weak": is_weak}})
            else:
                options.append({name: {"cardinality": cardinality, "is_weak": is_weak}})
                options.append({name: cardinality})
        return options

    for num_entities_from, num_entities_to in itertools.product([1, 2], repeat=2):
        from_entities = list()  # list of options (in total: list of list of dicts)
        to_entities = list()  # list of options (in total: list of list of dicts)
        for i in range(num_entities_from):
            from_entities.append(generate_entity_dicts("A" + str(i)))
        for i in range(num_entities_to):
            to_entities.append(generate_entity_dicts("B" + str(i)))

        # for all pair of options, test the relation (i.e. select one dict for each super list)
        from_combinations = itertools.product(*from_entities)
        to_combinations = itertools.product(*to_entities)

        for from_combination, to_combination in itertools.product(
            from_combinations, to_combinations
        ):
            # merge the tuple of dicts into a single dict
            from_part = dict()
            extended_from_part = dict()
            for d in copy.deepcopy(from_combination):
                from_part.update(d)
                # check whether d is dict[str, str] or dict[str, dict]
                new_d = dict()
                for key, value in d.items():
                    if isinstance(value, dict):
                        new_d = d
                    else:
                        new_d[key] = {"cardinality": value, "is_weak": False}
                extended_from_part.update(new_d)
            to_part = dict()
            extended_to_part = dict()
            for d in copy.deepcopy(to_combination):
                to_part.update(d)
                # check whether d is dict[str, str] or dict[str, dict]
                new_d = dict()
                for key, value in d.items():
                    if isinstance(value, dict):
                        new_d = d
                    else:
                        new_d[key] = {"cardinality": value, "is_weak": False}
                extended_to_part.update(new_d)

            assert from_part.keys() == extended_from_part.keys()
            assert to_part.keys() == extended_to_part.keys()
            assert len(from_part) == num_entities_from
            assert len(to_part) == num_entities_to

            g = ER()
            assert len(g.get_relations()) == 0
            g.add_relation(from_part, "R", to_part)
            assert len(g.get_relations()) == 1
            assert len(g.get_entities()) == num_entities_from + num_entities_to

            # The same relation should be returned regardless of the way it is retrieved.
            relation_by_label = g.get_relation_by_label("R")
            relation_id = relation_by_label["id"]
            relation_by_id = g.get_relation_by_id(relation_id)
            assert relation_by_id == relation_by_label

            relation = relation_by_id

            # Get the entity IDs and add them to the extended dicts
            for key, value in extended_from_part.items():
                entity = g.get_entity_by_label(key)
                value["id"] = entity["id"]
            for key, value in extended_to_part.items():
                entity = g.get_entity_by_label(key)
                value["id"] = entity["id"]

            # Test the format of the relation.
            assert isinstance(relation, dict)
            assert set(relation.keys()) == {
                "id",
                "label",
                "node_type",
                "attribute_ids",
                "from_entities",
                "to_entities",
            }
            assert relation["id"] == relation_id
            assert relation["label"] == "R"
            assert relation["node_type"] == NodeType.RELATION
            assert relation["attribute_ids"] == []
            assert relation["from_entities"] == extended_from_part
            assert relation["to_entities"] == extended_to_part


def test_get_attribute_of_entity():
    for is_pk, is_multiple, is_weak, composed_of in itertools.product(
        [True, False],
        [True, False],
        [True, False],
        powerset(["sub_attr_1", "sub_attr_2", "sub_attr_3"]),
    ):
        g = ER()
        g.add_entity("A")
        g.add_attribute(
            "A",
            "attr_1",
            is_pk=is_pk,
            is_multiple=is_multiple,
            is_weak=is_weak,
            composed_of=composed_of,
        )

        assert len(g.get_attributes()) == 1
        assert len(g.get_entities()) == 1

        entity = g.get_entity_by_label("A")
        attribute = g.get_attribute_by_label("attr_1")

        assert entity["attribute_ids"] == [attribute["id"]]
        assert attribute["node_type"] == NodeType.ATTRIBUTE
        assert attribute["label"] == "attr_1"
        assert attribute["is_pk"] == is_pk
        assert attribute["is_multiple"] == is_multiple
        assert attribute["is_weak"] == is_weak
        assert attribute["parent_id"] == entity["id"]
        assert attribute["parent_type"] == NodeType.ENTITY

        composed_of_attribute_ids = attribute["composed_of_attribute_ids"]
        assert len(composed_of_attribute_ids) == len(composed_of)
        for sub_attr_label in composed_of:
            sub_attr = g.get_composed_attribute_by_label(sub_attr_label)
            assert sub_attr["parent_id"] == attribute["id"]
            assert sub_attr["node_type"] == NodeType.COMPOSED_ATTRIBUTE
            assert sub_attr["label"] in composed_of
            assert sub_attr["id"] in composed_of_attribute_ids
            assert sub_attr["is_pk"] == is_pk
            assert sub_attr["is_multiple"] == is_multiple
            assert sub_attr["is_weak"] == is_weak

        assert len(g.get_composed_attributes()) == len(composed_of)


def test_get_attribute_of_relation():
    for is_pk, is_multiple, is_weak, composed_of in itertools.product(
        [True, False],
        [True, False],
        [True, False],
        powerset(["sub_attr_1", "sub_attr_2", "sub_attr_3"]),
    ):
        g = ER()
        g.add_entity("A")
        g.add_entity("B")
        g.add_relation({"A": "1"}, "R", {"B": "1"})
        g.add_attribute(
            "R",
            "attr_1",
            is_pk=is_pk,
            is_multiple=is_multiple,
            is_weak=is_weak,
            composed_of=composed_of,
        )

        assert len(g.get_attributes()) == 1
        assert len(g.get_entities()) == 2
        assert len(g.get_relations()) == 1

        relation = g.get_relation_by_label("R")
        attribute = g.get_attribute_by_label("attr_1")

        assert relation["attribute_ids"] == [attribute["id"]]
        assert attribute["node_type"] == NodeType.ATTRIBUTE
        assert attribute["label"] == "attr_1"
        assert attribute["is_pk"] == is_pk
        assert attribute["is_multiple"] == is_multiple
        assert attribute["is_weak"] == is_weak
        assert attribute["parent_id"] == relation["id"]
        assert attribute["parent_type"] == NodeType.RELATION

        composed_of_attribute_ids = attribute["composed_of_attribute_ids"]
        assert len(composed_of_attribute_ids) == len(composed_of)
        for sub_attr_label in composed_of:
            sub_attr = g.get_composed_attribute_by_label(sub_attr_label)
            assert sub_attr["parent_id"] == attribute["id"]
            assert sub_attr["node_type"] == NodeType.COMPOSED_ATTRIBUTE
            assert sub_attr["label"] in composed_of
            assert sub_attr["id"] in composed_of_attribute_ids
            assert sub_attr["is_pk"] == is_pk
            assert sub_attr["is_multiple"] == is_multiple
            assert sub_attr["is_weak"] == is_weak

        assert len(g.get_composed_attributes()) == len(composed_of)


def test_get_is_a():
    for is_total, is_disjunct, custom_text, sub_class_labels in itertools.product(
        [True, False],
        [True, False],
        ["custom_text", None],
        ["A"] + powerset(["A", "B", "C"], include_empty_set=False),
    ):
        g = ER()
        g.add_entity("Super")
        g.add_is_a(
            "Super",
            sub_class_labels=sub_class_labels,
            is_total=is_total,
            is_disjunct=is_disjunct,
            custom_text=custom_text,
        )

        assert len(g.get_is_as()) == 1
        assert (
            len(g.get_entities()) == 1 + len(sub_class_labels)
            if isinstance(sub_class_labels, list)
            else 1
        )

        super_class = g.get_entity_by_label("Super")
        is_a = g.get_is_as()[0]

        assert is_a["node_type"] == NodeType.IS_A
        assert is_a["superclass_id"] == super_class["id"]
        assert is_a["id"] == super_class["is_a_sub_id"]
        assert is_a["is_total"] == is_total
        assert is_a["is_disjunct"] == is_disjunct
        assert is_a["custom_text"] == custom_text

        subclass_ids = is_a["subclass_ids"]
        assert (
            len(subclass_ids) == len(sub_class_labels)
            if isinstance(sub_class_labels, list)
            else 1
        )
        for subclass_label in sub_class_labels:
            subclass = g.get_entity_by_label(subclass_label)
            assert subclass["is_a_super_id"] == is_a["id"]
            assert subclass["id"] in subclass_ids
