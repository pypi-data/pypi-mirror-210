from __future__ import annotations

import graphviz
from typeguard import typechecked

from typing import Any

import erdiagram


@typechecked
def draw_er_diagram(
    er: erdiagram.ER,
    engine: str = "dot",
    edge_len: float | int = 1.5,
    graph_attr: dict[str, Any] = dict(),
) -> graphviz.Digraph:
    """
    Draw ER diagram using Graphviz.

    Parameters
    ----------
    er : ER
        ER diagram to draw.
    engine : str, optional
        Graphviz engine to use, by default 'dot'
    edge_len : float | int, optional
        Length of edges, by default 1.5
    graph_attr : dict[str, Any], optional
        Graph attributes, by default dict()

    Returns
    -------
    graphviz.Digraph
    """
    G = graphviz.Digraph("ER", engine=engine, graph_attr=graph_attr)

    edge_len_str = str(edge_len)

    # Add Entites
    entities = er.get_entities()
    for entity in entities:
        G = add_entity(G, entity, edge_len_str)

    # Add isAs
    is_as = er.get_is_as()
    for is_a in is_as:
        G = add_is_a(G, is_a, edge_len_str)

    # Add Relations
    relations = er.get_relations()
    for relation in relations:
        G = add_relation(G, relation, edge_len_str)

    # Add Attributes
    attributes = er.get_attributes()
    for attribute in attributes:
        G = add_attribute(G, attribute, edge_len_str)
    composed_attributes = er.get_composed_attributes()
    for composed_attribute in composed_attributes:
        G = add_composed_attribute(G, composed_attribute, edge_len_str)

    return G


@typechecked
def add_entity(
    G: graphviz.Digraph, entity: dict[str, Any], edge_len: str
) -> graphviz.Digraph:
    """
    Add entity to graphviz graph.

    Parameters
    ----------
    G : graphviz.Digraph
        Graphviz graph.
    entity : dict[str, Any]
        Entity to add.
    edge_len : str
        Length of edges.

    Returns
    -------
    graphviz.Digraph
    """
    peripheries = "2" if entity["is_multiple"] or entity["is_weak"] else "1"
    G.attr(
        "node",
        shape="box",
        style="filled",
        fillcolor="#CCCCFF",
        color="#0000FF",
        peripheries=peripheries,
    )
    G.node(name=str(entity["id"]), label=entity["label"])
    return G


@typechecked
def add_is_a(
    G: graphviz.Digraph, is_a: dict[str, Any], edge_len: str
) -> graphviz.Digraph:
    """
    Add isA to graphviz graph.

    Parameters
    ----------
    G : graphviz.Digraph
        Graphviz graph.
    is_a : dict[str, Any]
        isA to add.
    edge_len : str
        Length of edges.

    Returns
    -------
    graphviz.Digraph
    """
    G.attr(
        "node",
        shape="invtriangle",
        style="filled",
        fillcolor="#CCFFCC",
        color="#506550",
        peripheries="1",
    )
    text = "T" if is_a["is_total"] else "P"
    text = (
        is_a["custom_text"]
        if is_a["custom_text"] and len(is_a["custom_text"]) > 0
        else text
    )
    G.node(name=str(is_a["id"]), label="isA", xlabel=text)

    G.edge(
        tail_name=str(is_a["superclass_id"]),
        head_name=str(is_a["id"]),
        len=edge_len,
        arrowhead="none",
    )

    dir = "back" if not is_a["is_disjunct"] else "forward"
    for id in is_a["subclass_ids"]:
        G.edge(
            tail_name=str(is_a["id"]),
            head_name=str(id),
            len=edge_len,
            arrowhead="normal",
            dir=dir,
        )

    return G


@typechecked
def add_relation(
    G: graphviz.Digraph, relation: dict[str, Any], edge_len: str
) -> graphviz.Digraph:
    """
    Add relation to graphviz graph.

    Parameters
    ----------
    G : graphviz.Digraph
        Graphviz graph.
    relation : dict[str, Any]
        Relation to add.
    edge_len : str
        Length of edges.

    Returns
    -------
    graphviz.Digraph
    """
    from_entities = relation["from_entities"]
    to_entities = relation["to_entities"]

    any_is_weak = False
    for _, data in from_entities.items():
        if data["is_weak"]:
            any_is_weak = True
            break
    for _, data in to_entities.items():
        if data["is_weak"]:
            any_is_weak = True
            break

    peripheries = "2" if any_is_weak else "1"
    G.attr(
        "node",
        shape="diamond",
        style="filled",
        fillcolor="#FFCCCC",
        color="#BA2128",
        peripheries=peripheries,
    )
    G.node(name=str(relation["id"]), label=relation["label"])

    for _, data in from_entities.items():
        edge_color = "black:invis:black" if data["is_weak"] else "black"
        G.edge(
            tail_name=str(data["id"]),
            head_name=str(relation["id"]),
            label=str(data["cardinality"]),
            len=edge_len,
            arrowhead="none",
        )
    for _, data in to_entities.items():
        edge_color = "black:invis:black" if data["is_weak"] else "black"
        G.edge(
            tail_name=str(relation["id"]),
            head_name=str(data["id"]),
            label=str(data["cardinality"]),
            len=edge_len,
            arrowhead="none",
            color=edge_color,
        )

    return G


@typechecked
def add_attribute(
    G: graphviz.Digraph, attribute: dict[str, Any], edge_len: str
) -> graphviz.Digraph:
    """
    Add attribute to graphviz graph.

    Parameters
    ----------
    G : graphviz.Digraph
        Graphviz graph.
    attribute : dict[str, Any]
        Attribute to add.
    edge_len : str
        Length of edges.

    Returns
    -------
    graphviz.Digraph
    """
    peripheries = "2" if attribute["is_multiple"] else "1"
    G.attr(
        "node",
        shape="ellipse",
        style="filled",
        fillcolor="#FFFBD6",
        color="#656354",
        peripheries=peripheries,
    )

    label = attribute["label"]
    if attribute["is_weak"] and attribute["is_pk"]:
        i = 0
        tpm_label = ""
        for c in label:
            if i % 2 == 0:
                tpm_label += f"<U>{c}</U>"
            else:
                tpm_label += c
            i += 1
        label = f"<{tpm_label}>"
    elif attribute["is_pk"]:
        label = f"<<U>{label}</U>>"

    G.node(name=str(attribute["id"]), label=label)

    G.edge(
        tail_name=str(attribute["parent_id"]),
        head_name=str(attribute["id"]),
        arrowhead="none",
    )

    return G


@typechecked
def add_composed_attribute(
    G: graphviz.Digraph, composed_attribute: dict[str, Any], edge_len: str
) -> graphviz.Digraph:
    """
    Add composed attribute to graphviz graph.

    Parameters
    ----------
    G : graphviz.Digraph
        Graphviz graph.
    composed_attribute : dict[str, Any]
        Composed attribute to add.
    edge_len : str
        Length of edges.

    Returns
    -------
    graphviz.Digraph
    """
    peripheries = "2" if composed_attribute["is_multiple"] else "1"
    G.attr(
        "node",
        shape="ellipse",
        style="filled",
        fillcolor="#FFFBD6",
        color="#656354",
        peripheries=peripheries,
    )

    label = composed_attribute["label"]
    if composed_attribute["is_weak"] and composed_attribute["is_pk"]:
        i = 0
        tpm_label = ""
        for c in label:
            if i % 2 == 0:
                tpm_label += f"<U>{c}</U>"
            else:
                tpm_label += c
            i += 1
        label = f"<{tpm_label}>"
    elif composed_attribute["is_pk"]:
        label = f"<<U>{label}</U>>"

    G.node(name=str(composed_attribute["id"]), label=label)

    G.edge(
        tail_name=str(composed_attribute["parent_id"]),
        head_name=str(composed_attribute["id"]),
        arrowhead="none",
    )

    return G
