from __future__ import annotations

from typeguard import typechecked

import erdiagram


@typechecked
def merge_er_diagrams(
    er1: erdiagram.ER,
    er2: erdiagram.ER,
) -> erdiagram.ER:
    """
    Merge two ER diagrams.

    Parameters
    ----------
    er1 : ER
        First ER diagram.
    er2 : ER
        Second ER diagram.

    Returns
    -------
    ER
        Merged ER diagram.
    """
    g = erdiagram.ER()
    g = _merge_er_diagram_entities(g, er1, er2)
    g = _merge_er_diagram_is_as(g, er1, er2)
    g = _merge_er_diagram_relations(g, er1, er2)
    g = _merge_er_diagram_attributes(g, er1, er2)
    return g


@typechecked
def _merge_er_diagram_entities(
    g: erdiagram.ER,
    er1: erdiagram.ER,
    er2: erdiagram.ER,
) -> erdiagram.ER:
    """
    Merge the entities of two ER diagrams.

    Parameters
    ----------
    g : ER
        Merged ER diagram.
    er1 : ER
        First ER diagram.
    er2 : ER
        Second ER diagram.

    Returns
    -------
    ER
        Merged ER diagram.
    """
    # Add all entities from er1 and er2. If an entity is in both, then add it only once and set the boolean parameters to the maximum (OR).
    for entity1 in er1.get_entities():
        label = entity1["label"]
        if er2.has_entity(label):
            entity2 = er2.get_entity_by_label(label)
            g.add_entity(
                label=label,
                is_multiple=entity1["is_multiple"] or entity2["is_multiple"],
                is_weak=entity1["is_weak"] or entity2["is_weak"],
            )
        else:
            g.add_entity(
                label=label,
                is_multiple=entity1["is_multiple"],
                is_weak=entity1["is_weak"],
            )
    for entity2 in er2.get_entities():
        label = entity2["label"]
        if not er1.has_entity(label):
            g.add_entity(
                label=label,
                is_multiple=entity2["is_multiple"],
                is_weak=entity2["is_weak"],
            )
    return g


@typechecked
def _merge_er_diagram_is_as(
    g: erdiagram.ER, er1: erdiagram.ER, er2: erdiagram.ER
) -> erdiagram.ER:
    """
    Merge the is-a relations of two ER diagrams.

    Parameters
    ----------
    g : ER
        Merged ER diagram.
    er1 : ER
        First ER diagram.
    er2 : ER
        Second ER diagram.

    Returns
    -------
    ER
        Merged ER diagram.
    """

    def __merge_all_from(g: erdiagram.ER, er: erdiagram.ER) -> erdiagram.ER:
        """
        Merge all is-a relations from a single ER diagram.

        Parameters
        ----------
        g : ER
            Merged ER diagram.
        er : ER
            ER diagram.

        Returns
        -------
        ER
            Merged ER diagram.
        """
        for isa in er.get_is_as():
            superclass_id = isa["superclass_id"]
            super_class_label = er.get_entity_by_id(superclass_id)["label"]
            subclass_ids = isa["subclass_ids"]
            sub_class_labels = [
                er.get_entity_by_id(subclass_id)["label"]
                for subclass_id in subclass_ids
            ]
            g.add_is_a(
                super_class_label=super_class_label,
                sub_class_labels=sub_class_labels,
                is_total=isa["is_total"],
                is_disjunct=isa["is_disjunct"],
                custom_text=isa["custom_text"],
            )
        return g

    # Add all is-a relations from er1 and er2.
    g = __merge_all_from(g, er1)
    g = __merge_all_from(g, er2)
    return g


@typechecked
def _merge_er_diagram_relations(
    g: erdiagram.ER, er1: erdiagram.ER, er2: erdiagram.ER
) -> erdiagram.ER:
    """
    Merge the relations of two ER diagrams.

    Parameters
    ----------
    g : ER
        Merged ER diagram.
    er1 : ER
        First ER diagram.
    er2 : ER
        Second ER diagram.

    Returns
    -------
    ER
        Merged ER diagram.
    """
    for relation in list(er1.get_relations()) + list(er2.get_relations()):
        label = relation["label"]
        from_entities = relation["from_entities"]
        to_entities = relation["to_entities"]
        # for each entity from from_entities and to_entities, remove the (key,value)-pair where key="id"
        from_entities = {
            entity_label: {k: v for k, v in data.items() if k != "id"}
            for entity_label, data in from_entities.items()
        }
        to_entities = {
            entity_label: {k: v for k, v in data.items() if k != "id"}
            for entity_label, data in to_entities.items()
        }
        g.add_relation(
            from_entities=from_entities,
            relation_label=label,
            to_entities=to_entities,
        )

    return g


@typechecked
def _merge_er_diagram_attributes(
    g: erdiagram.ER, er1: erdiagram.ER, er2: erdiagram.ER
) -> erdiagram.ER:
    """
    Merge the attributes of two ER diagrams.

    Parameters
    ----------
    g : ER
        Merged ER diagram.
    er1 : ER
        First ER diagram.
    er2 : ER
        Second ER diagram.

    Returns
    -------
    ER
        Merged ER diagram.
    """

    def __merge_all_from(g: erdiagram.ER, er: erdiagram.ER) -> erdiagram.ER:
        """
        Merge all attributes from a single ER diagram.

        Parameters
        ----------
        g : ER
            Merged ER diagram.
        er : ER
            ER diagram.

        Returns
        -------
        ER
            Merged ER diagram.
        """
        for attribute in er.get_attributes():
            label = attribute["label"]
            parent_id = attribute["parent_id"]
            parent_label = er.get_label_by_id(parent_id)
            if g.has_attribute(
                parent_label=parent_label, attribute_label=label
            ):  # do not add twice! (can occour when merging two ER diagrams with the same entities)
                continue
            composed_of_attribute_ids = attribute["composed_of_attribute_ids"]
            composed_of_attribute_labels = [
                er.get_label_by_id(composed_attribute_id)
                for composed_attribute_id in composed_of_attribute_ids
            ]
            g.add_attribute(
                parent_label=parent_label,
                attribute_label=label,
                is_pk=attribute["is_pk"],
                is_multiple=attribute["is_multiple"],
                is_weak=attribute["is_weak"],
                composed_of=composed_of_attribute_labels,
            )
        return g

    g = __merge_all_from(g, er1)
    g = __merge_all_from(g, er2)
    return g
