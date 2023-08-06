# DBIS ER Diagram

[![pypi](https://img.shields.io/pypi/pyversions/dbis-er-diagram)](https://pypi.org/project/dbis-er-diagram/)
[![PyPI Status](https://img.shields.io/pypi/v/dbis-er-diagram)](https://pypi.org/project/dbis-er-diagram/)

This library is used to draw entity-relationship (ER) diagrams.

The [examples](./examples/) directory contains some examples of how to use this library.

# Features
 - Create and draw ER diagrams to images.
 - Create complex ER diagrams by combining multiple smaller diagrams.
 - Compare two ER diagrams based on a graph distance measure.


# Installation
Install via pip:
```sh
pip install dbis-er-diagram
```

# Basic Usage
## Diagrams, Merging, and Drawing
A diagram is a collection of entities and relationships. We can draw an ER diagram to an image file using [Graphviz](https://graphviz.org/):

```python
from erdiagram import ER
g = ER()

# Add entities and relationships

# draw to image file "file_name.png"
digraph = g.draw()
digraph.render("file_name", format="png", view=False, cleanup=True, engine="dot")

# OR: display in jupyter notebook
g.display()
```

We are also able to merge two diagrams together. The `merge_er_diagrams` will return a new diagram that contains all the entities and relationships from both diagrams, and matches similar objects contained in both diagrams.

```python
from erdiagram import ER, merge_er_diagrams

g1 = ER()
# Add entities and relationships to g1
g2 = ER()
# Add entities and relationships to g2

g = merge_er_diagrams(g1, g2)
```

## Entity
Entities are objects - concrete or abstract items or beings that differ from other entities. Examples of these are person, car, customer, book, etc.

Entity types are sets of entities that have the same attributes. Examples of entity types are people, cars, customers, etc.

In ER diagrams, entity types are represented by rectangles.

```python
g.add_entity(
    label: str,
    is_multiple: bool = False,
    is_weak: bool = False
)
```
**Parameters:**
 - `label`: The name of the entity.
 - `is_multiple`: Whether the entity is a set of entities.
 - `is_weak`: Whether the entity is weak.

#### Examples
```python
from erdiagram import ER

g = ER()
g.add_entity("A", is_multiple=False, is_weak=False)
g.add_entity("B", is_multiple=False, is_weak=True)
g.add_entity("C", is_multiple=True, is_weak=False)
g.add_entity("D", is_multiple=True, is_weak=True)
```
![Entities](./examples/images/entities.png)

## Relationship
Often, two or more entity types are related to each other. Relationships are represented in the ER diagram by diamonds and can also have attributes.

In the lecture, two notations were presented for cardinality restrictions: the `1:n` notation and the `(min,max)` notation. These notations can be used to specify cardinalities in addition to the depicted relation, to show in what quantity the entities of one entity type are related to entities of the other entity type. These cardinalities are written on the edges between the entity type and the relationship in the ER diagram.

```python
g.add_relation(
    from_entities: dict[str, int | str | dict[str, int | str]],
    relation_label: str,
    to_entities: dict[str, int | str | dict[str, int | str]]
)
```
**Parameters:**
 - `from_relations`: A dictionary of entities that the relationship is coming from. The key is the entity label, and the value is either the cardinality directly, or a dictionary containing the cardinality and the `is_weak` flag.
 - `relation_label`: The name of the relationship.
 - `to_relations`: A dictionary of entities that the relationship is going to. The key is the entity label, and the value is either the cardinality directly, or a dictionary containing the cardinality and the `is_weak` flag.

#### Examples
```python
from erdiagram import ER

g = ER()

g.add_relation({"Person": "1"}, "owns", {"Car": "n"})
```
![Relation 1](./examples/images/relation_1.png)

<hr>

```python
from erdiagram import ER

g = ER()

g.add_entity("Contract", is_weak=True)
g.add_relation(
    {"Person": "1"},
    "owns",
    {
        "Car": "n",
        "Contract": {
            "cardinality": "n",
            "is_weak": True
        }
    }
)
```
![Relation 2](./examples/images/relation_2.png)

## Attributes
Entities and relationships can have attributes in an ER diagram. These attributes describe the characteristics of the entity or relationship, such as color, weight, and price for the "Parts" entity type. Attribute values typically come from value ranges such as INTEGER, REAL, STRING, etc., but structured values such as lists and trees are also possible.

A key is a minimal set of attributes whose values uniquely identify the associated entity or relationship among all entities or relationships of its type. Attributes are represented in the ER diagram by ellipses:

 - Attributes are connected to the corresponding entity or relationship type by undirected edges.
 - Key attributes (primary key) are (usually) underlined.

An attribute can consist of other attributes. An example of this is an address, which consists of street + house number, postal code, and city. Sub-attributes are connected to the composite attribute by undirected edges. To create a composite attribute, a list of sub-attributes must be passed as the "composedOf" parameter when creating the attribute.

A (multi-valued) attribute can contain a set of values. An example of this is the "Author" attribute of the "Book" entity type, since a book can be written by multiple authors. A multi-valued attribute is represented by an ellipse with a double border. To indicate that an attribute is multi-valued, the "is_multiple" parameter must be set to true when creating the attribute.

```python
g.add_attribute(
    parent_label: str,
    attribute_label: str,
    is_pk: bool = False,
    is_multiple: bool = False,
    is_weak: bool = False,
    composed_of: list[str] = [],
)
```
**Parameters:**
 - `parent_label`: The label of the entity or relationship that the attribute belongs to.
 - `attribute_label`: The name of the attribute.
 - `is_pk`: Whether the attribute is a primary key.
 - `is_multiple`: Whether the attribute is multivalued.
 - `is_weak`: Whether the attribute is weak.
 - `composed_of`: A list of sub-attributes that the attribute is composed of.

#### Examples
```python
from erdiagram import ER

g = ER()

g.add_entity("A")
g.add_attribute("A", "attr_a1", is_multiple=False, is_pk=False)
g.add_attribute("A", "attr_a2", is_multiple=False, is_pk=True)
g.add_attribute("A", "attr_a3", is_multiple=True, is_pk=False)
g.add_attribute("A", "attr_a4", is_multiple=True, is_pk=True)

g.add_entity("B", is_weak=True)
g.add_attribute("B", "attr_b1", is_multiple=False, is_pk=False, is_weak=True)
g.add_attribute("B", "attr_b2", is_multiple=False, is_pk=True, is_weak=True)
g.add_attribute("B", "attr_b3", is_multiple=True, is_pk=False, is_weak=True)
g.add_attribute("B", "attr_b4", is_multiple=True, is_pk=True, is_weak=True)
```
![Attribute 1](./examples/images/attribute_1.png)

<hr>

```python
from erdiagram import ER

g = ER()

g.add_entity("A")
g.add_attribute("A", "attr_a1", composed_of=["sub_a1", "sub_a2"])

g.add_entity("B", is_weak=True)
g.add_attribute("B", "attr_b2", composed_of=["sub_b1", "sub_b2"], is_weak=True, is_pk=True)
```
![Attribute 2](./examples/images/attribute_2.png)

## Specialization/Generalization Relationships
There can be inheritance relationships (isA) between entity types and specialized entity types. These are represented in the ER diagram as inverted triangles with an undirected edge to the general entity type and one or more directed edges to the specialized entity types.

There are different forms of these inheritance relationships:

 - <u>Disjoint</u>: Specializations are disjoint (an employee cannot be both an assistant and a professor). Arrows point towards the specialization.
 - <u>Non-disjoint</u>: Specializations are not disjoint (a person can be both an employee and a student). Arrows point towards the generalization.
 - <u>Total</u>: The decomposition of the generalization is complete (there are either scientific or non-scientific employees). Represented by "t" next to the isA relationship.
 - <u>Partial</u>: The union of the specialization is a proper subset of the generalization. Represented by "p" next to the isA relationship.

```python
g.add_is_a(
    super_class_label: str,
    sub_class_labels: str | list[str],
    is_total: bool,
    is_disjunct: bool,
    custom_text: Optional[str] = None,
)
```
**Parameters:**
 - `super_class_label`: The label of the general entity type.
 - `sub_class_labels`: The label of the specialized entity type, or a list of labels of the specialized entity types.
 - `is_total`: Whether the specialization is total.
 - `is_disjunct`: Whether the specialization is disjoint.
 - `custom_text`: Custom text to be displayed next to the isA relationship in place of "p" or "t" for partial or total relationships, respectively.


# Examples
```python
from erdiagram import ER

g = ER()

g.add_entity("Person")
g.add_entity("Student")
g.add_entity("Professor")
g.add_is_a("Person", ["Student", "Professor"], is_total=False, is_disjunct=True)


g.add_entity("Brightness")
g.add_entity("Light")
g.add_entity("Darkness")
g.add_is_a("Brightness", ["Light", "Darkness"], is_total=True, is_disjunct=False)
```
![IsA 1](./examples/images/is_a_1.png)

<hr>

```python
from erdiagram import ER

g = ER()

g.add_is_a(
    "Super",
    "Sub",
    is_total=True,
    is_disjunct=True,
    custom_text="Some custom text",
)
```
![IsA 2](./examples/images/is_a_2.png)

# Further Usage
_This section is relevant to developers only._

## Internal Representation
The ER diagram class `ER` internally stores the diagram as a graph, using [networkx](https://networkx.org/). In order to query the diagram, getter methods are provided that return the corresponding ER diagram objects (entities, relationships, attributes, isA relationships). The format of the returned objects are the following dictionaries:

### Entity Format
```python
{
    "id": int,
    "node_type": NodeType.ENTITY,
    "label": str,
    "is_multiple": bool,
    "is_weak": bool,
    "relation_ids_from": list[int],
    "relation_ids_to": list[int],
    "attribute_ids": list[int],
    "is_a_super_id": int,
    "is_a_sub_id": int
}
```
Where:
 - `id`: The internal id of the entity.
 - `node_type`: The type of the node. In this case, `NodeType.ENTITY`.
 - `label`: The label of the entity.
 - `is_multiple`: Whether the entity is multivalued.
 - `is_weak`: Whether the entity is weak.
 - `relation_ids_from`: A list of relation ids where the entity is the source of the relation.
 - `relation_ids_to`: A list of relation ids where the entity is the target of the relation.
 - `attribute_ids`: A list of attribute ids that are associated with the entity.
 - `is_a_super_id`: The id of the isA relationship to its superclass.
 - `is_a_sub_id`: The id of the isA relationship to its sub classes.

### IsA Format
```python
{
    "id": int,
    "node_type": NodeType.IS_A,
    "is_total": bool,
    "is_disjunct": bool,
    "custom_text": str,
    "superclass_id": int,
    "subclass_ids": list[int]
}
```
Where:
 - `id`: The id of the isA relationship.
 - `node_type`: The type of the node. In this case, NodeType.IS_A.
 - `is_total`: Whether the isA relationship is total.
 - `is_disjunct`: Whether the isA relationship is disjunct.
 - `custom_text`: A custom text to display instead of "P" or "T".
 - `superclass_id`: The id of the superclass entity.
 - `subclass_ids`: A list of ids of the subclass entities.

### Attribute Format
```python
{
    "id": int,
    "node_type": NodeType.ATTRIBUTE,
    "parent_id": int,
    "parent_type": NodeType.ENTITY | NodeType.RELATION,
    "label": str,
    "is_pk": bool,
    "is_multiple": bool,
    "is_weak": bool,
    "composed_of_attribute_ids": list[int]
}
```
Where:
 - `id`: The internal id of the attribute.
 - `node_type`: The type of the node. In this case, NodeType.ATTRIBUTE.
 - `parent_id`: The id of the parent node (either an entity or a relation).
 - `parent_type`: The type of the parent node, either NodeType.ENTITY or NodeType.RELATION.
 - `label`: The label of the attribute.
 - `is_pk`: Whether the attribute is a primary key.
 - `is_multiple`: Whether the attribute is multivalued.
 - `is_weak`: Whether the attribute is a part of a weak entity.
 - `composed_of_attribute_ids`: A list of attribute ids that this attribute is composed of (if it is a composite attribute).

### Composed Attribute Format
```python
{
    "id": int,
    "node_type": NodeType.COMPOSED_ATTRIBUTE,
    "label": str,
    "is_pk": bool,
    "is_multiple": bool,
    "is_weak": bool,
    "parent_id": int
}
```
Where:
 - `id`: The internal id of the composed attribute.
 - `node_type`: The type of the node. In this case, NodeType.COMPOSED_ATTRIBUTE.
 - `label`: The label of the composed attribute.
 - `is_pk`: Whether the composed attribute is a primary key.
 - `is_multiple`: Whether the composed attribute is multivalued.
 - `is_weak`: Whether the composed attribute is weak.
 - `parent_id`: The id of the parent attribute that the composed attribute is composed of.

### Relation Format
```python
{
    "id": int,
    "node_type": NodeType.RELATION,
    "label": str,
    "attribute_ids": list[int],
    "from_entities": {
        "entity_label": {
            "id": int,
            "cardinality": str,
            "is_weak": bool
        }
    },
    "to_entities": {
        "entity_label": {
            "id": int,
            "cardinality": str,
            "is_weak": bool
        }
    }
}
```
Where:
 - `id`: The internal id of the relation.
 - `label`: The label of the relation.
 - `node_type`: The type of the node. In this case, NodeType.RELATION.
 - `attribute_ids`: A list of attribute ids that are associated with the relation.
 - `from_entities`: A dictionary where the keys are entity `labels` and the values are dictionaries containing the following information about the entities that the relation is coming from:
	 - `id`: The id of the entity.
	 - `cardinality`: The cardinality of the entity to the relation (e.g. "1", "n").
	 - `is_weak`: Whether the entity is bound weak to this relation.
 - `to_entities`: A dictionary where the keys are entity `labels` and the values are dictionaries containing the following information about the entities that the relation is going to:
	 - `id`: The id of the entity.
	 - `cardinality`: The cardinality of the entity to the relation (e.g. "1", "n").
	 - `is_weak`: Whether the entity is bound weak to this relation.

## Grading
This library provides a method `grade_submission` to compare a submission to a (correct) solution. The method returns a grading log and the grading score. This score represents the graph distance between submission and solution (:warning: non-negative value) and may be interpreted as the amount of errors in the submission.

> Note, that `grade_submission(solution, submission)` is not necessarily equal to `grade_submission(submission, solution)`. The grading is not symmetric in order to simplify the grading process.