from __future__ import annotations

from typing import Optional, Any

import graphviz
import networkx as nx
from networkx.readwrite import json_graph
from IPython.display import display as ipython_display
from typeguard import typechecked

import erdiagram


class ER:
    """
    Entity Relationship Diagram class
    """

    @typechecked
    def __init__(self) -> None:
        """
        Initialize the ER diagram
        """
        # The ER diagram is internally stored as a Directed Graph
        self.graph = nx.DiGraph()

        # Create a unique ID generator
        def id_generator():
            id = 0
            while True:
                yield id
                id += 1

        generator = id_generator()

        def get_id():
            return next(generator)

        self.__id = get_id

    ###################
    # Special methods #
    ###################

    @typechecked
    def draw(
        self,
        engine: str = "dot",
        edge_len: float | int = 1.5,
        graph_attr: dict[str, Any] = dict(),
    ) -> graphviz.Digraph:
        """
        Draw the ER diagram

        Parameters
        ----------
        engine : str, optional
            Graphviz engine to use, by default 'dot'
        edge_len : float | int, optional
            Length of edges, by default 1.5
        graph_attr : dict[str, Any], optional
            Graph attributes, by default dict()
        """
        return erdiagram.draw_er_diagram(self, engine, edge_len, graph_attr)

    @typechecked
    def display(
        self,
        engine: str = "dot",
        edge_len: float | int = 1.5,
        graph_attr: dict[str, Any] = dict(),
    ) -> None:
        """
        Display the ER diagram

        Parameters
        ----------
        engine : str, optional
            Graphviz engine to use, by default 'dot'
        edge_len : float | int, optional
            Length of edges, by default 1.5
        graph_attr : dict[str, Any], optional
            Graph attributes, by default dict()
        """
        ipython_display(erdiagram.draw_er_diagram(self, engine, edge_len, graph_attr))

    ###############
    # Add methods #
    ###############

    @typechecked
    def add_entity(
        self, label: str, is_multiple: bool = False, is_weak: bool = False
    ) -> None:
        """
        Add an entity to the graph

        Parameters
        ----------
        label : str
            Entity label
        is_multiple : bool, optional
            Is cardinality of the entity multiple or singular?, by default False
        is_weak : bool, optional
            Is this a weak entity?, by default False
        """
        # Check that label is not empty
        assert label != "", "Label cannot be empty"
        # Check that the entity does not already exist
        assert not self.has_entity(label), f"Entity {label} already exists"
        # Create entity
        self.graph.add_node(
            self.__id(),
            label=label,
            is_multiple=is_multiple,
            is_weak=is_weak,
            node_type=erdiagram.NodeType.ENTITY,
        )

    @typechecked
    def add_attribute(
        self,
        parent_label: str,
        attribute_label: str,
        is_pk: bool = False,
        is_multiple: bool = False,
        is_weak: bool = False,
        composed_of: list[str] = [],
    ) -> None:
        """
        Add an attribute to an entity or relation in the graph

        Parameters
        ----------
        parent_label : str
            Entity or relation label
        attribute_label : str
            Attribute label
        is_pk : bool, optional
            Is this attribute the primary key?, by default False (not primary key)
        is_multiple : bool, optional
            Is cardinality of the attribute multiple or singular?, by default False (singular)
        is_weak : bool, optional
            Is this a weak attribute?, by default False (not weak)
        composed_of : list[str], optional
            List of attributes this attribute is composed of, by default [] (none)
        """
        # Check that attribute_label is not empty
        assert attribute_label != "", "Attribute label cannot be empty"
        # Get id of parent
        parent_id = self.get_id_by_label(parent_label)
        if parent_id is None:
            # Create entity with that label
            self.add_entity(parent_label)
            parent_id = self.get_entity_by_label(parent_label)["id"]
            assert parent_id is not None, "Internal Error"
        # Check that the attribute does not already exist
        assert not self.has_attribute(
            parent_label, attribute_label
        ), f"Attribute {attribute_label} already exists"

        # Create attribute
        attribute_id = self.__id()
        self.graph.add_node(
            attribute_id,
            label=attribute_label,
            is_pk=is_pk,
            is_multiple=is_multiple,
            is_weak=is_weak,
            node_type=erdiagram.NodeType.ATTRIBUTE,
        )
        # Add edge from parent to attribute
        self.graph.add_edge(parent_id, attribute_id)

        # For each attribute this attribute is composed of create a node and add an edge from the parent attribute to the child attribute
        assert len(list(set(composed_of))) == len(
            composed_of
        ), "Duplicate attribute labels"
        for child_attribute_label in composed_of:
            # Check that child_attribute_label is not empty
            assert child_attribute_label != "", "Child attribute label cannot be empty"
            # Create child attribute
            child_attribute_id = self.__id()
            self.graph.add_node(
                child_attribute_id,
                label=child_attribute_label,
                is_pk=is_pk,
                is_multiple=is_multiple,
                is_weak=is_weak,
                node_type=erdiagram.NodeType.COMPOSED_ATTRIBUTE,
            )
            # Add edge from parent attribute to child attribute
            self.graph.add_edge(attribute_id, child_attribute_id)

        # Get parent id
        parent_id = self.get_id_by_label(parent_label)
        # Add edge from parent to attribute
        self.graph.add_edge(parent_id, attribute_id)

    @typechecked
    def add_relation(
        self,
        from_entities: dict[str, int | str | dict[str, int | str]],
        relation_label: str,
        to_entities: dict[str, int | str | dict[str, int | str]],
    ) -> None:
        """
        Add a relation between some entities in the graph

        Parameters
        ----------
        from_entities : dict[str, int | str | dict[str, int | str]]
            Dictionary of entities and their cardinality
            Structure: {entityLabel: cardinality} or {entityLabel: {cardinality: cardinality, is_weak: is_weak}}
        relation_label : str
            Relation label
        to_entities : dict[str, int | str | dict[str, int | str]]
            Dictionary of entities and their cardinality
            Structure: {entityLabel: cardinality} or {entityLabel: {cardinality: cardinality, is_weak: is_weak}}
        """
        # parse to dict[str, dict[str, Any]]
        new_from = dict()
        for entityLabel, data in from_entities.items():
            if isinstance(data, dict):
                if "is_weak" not in data.keys():
                    data["is_weak"] = False
                new_from[entityLabel] = data
            else:
                new_from[entityLabel] = {"cardinality": str(data), "is_weak": False}
        from_entities = new_from
        new_to = dict()
        for entityLabel, data in to_entities.items():
            if isinstance(data, dict):
                if "is_weak" not in data.keys():
                    data["is_weak"] = False
                new_to[entityLabel] = data
            else:
                new_to[entityLabel] = {"cardinality": str(data), "is_weak": False}
        to_entities = new_to

        # Check if input correct (exactly and only "cardinality" and "is_weak" keys. No other keys). is_weak must be bool
        assert len(from_entities.keys()) > 0, "from_entities cannot be empty"
        assert len(to_entities.keys()) > 0, "to_entities cannot be empty"
        for entityLabel, data in from_entities.items():
            assert (
                "cardinality" in data.keys()
            ), f"Cardinality missing for entity {entityLabel}"
            assert "is_weak" in data.keys(), f"is_weak missing for entity {entityLabel}"
            assert len(data.keys()) == 2, f"Too many keys for entity {entityLabel}"
            assert isinstance(
                data["is_weak"], bool
            ), f"is_weak must be a boolean for entity {entityLabel}"
        for entityLabel, data in to_entities.items():
            assert (
                "cardinality" in data.keys()
            ), f"Cardinality missing for entity {entityLabel}"
            assert "is_weak" in data.keys(), f"is_weak missing for entity {entityLabel}"
            assert len(data.keys()) == 2, f"Too many keys for entity {entityLabel}"
            assert isinstance(
                data["is_weak"], bool
            ), f"is_weak must be a boolean for entity {entityLabel}"
        # No duplicate entities
        assert len(from_entities.keys()) == len(
            set(from_entities.keys())
        ), "Duplicate entities in from_entities"
        assert len(to_entities.keys()) == len(
            set(to_entities.keys())
        ), "Duplicate entities in to_entities"
        # Check that relation_label is not empty
        assert relation_label != "", "Relation label cannot be empty"

        # Create entities if not exists
        for entityLabel, data in from_entities.items():
            if not self.has_entity(entityLabel):
                self.add_entity(entityLabel, is_weak=data["is_weak"])
        for entityLabel, data in to_entities.items():
            if not self.has_entity(entityLabel):
                self.add_entity(entityLabel, is_weak=data["is_weak"])

        # If the entity shall be weakly connected, the entity itself must be weak
        for entityLabel, data in from_entities.items():
            if data["is_weak"]:
                assert self.get_entity_by_label(entityLabel)[
                    "is_weak"
                ], f"Entity {entityLabel} must be weak, since it should be weakly connected by relation {relation_label}"
        for entityLabel, data in to_entities.items():
            if data["is_weak"]:
                assert self.get_entity_by_label(entityLabel)[
                    "is_weak"
                ], f"Entity {entityLabel} must be weak, since it should be weakly connected by relation {relation_label}"

        # Create relation
        relation_id = self.__id()
        self.graph.add_node(
            relation_id, label=relation_label, node_type=erdiagram.NodeType.RELATION
        )

        # Add directed edges from relation to entities (and vice versa)
        for entityLabel, data in from_entities.items():
            entity_id = self.get_entity_by_label(entityLabel)["id"]
            self.graph.add_edge(
                entity_id,
                relation_id,
                cardinality=data["cardinality"],
                is_weak=data["is_weak"],
            )
        for entityLabel, data in to_entities.items():
            entity_id = self.get_entity_by_label(entityLabel)["id"]
            self.graph.add_edge(
                relation_id,
                entity_id,
                cardinality=data["cardinality"],
                is_weak=data["is_weak"],
            )

    @typechecked
    def add_is_a(
        self,
        super_class_label: str,
        sub_class_labels: str | list[str],
        is_total: bool,
        is_disjunct: bool,
        custom_text: Optional[str] = None,
    ) -> None:
        """
        Add an isA relation (Generalization / Specialization) to the diagram

        Parameters
        ----------
        super_class_label : str
            Label of the superclass entity
        sub_class_labels : str | list[str]
            Label(s) of the subclass entity(s)
        is_total : bool
            Is the relation total or partial?
        is_disjunct : bool
            Are the elements of this relation disjunct?
        custom_text : Optional[str], optional
            Custom text to be displayed instead of the partial / total symbol, by default None (don't display any custom text)
        """
        if isinstance(sub_class_labels, str):
            sub_class_labels = [sub_class_labels]
        assert len(sub_class_labels) > 0, "Subclass labels cannot be empty"

        # Create entities if not exists
        if not self.has_entity(super_class_label):
            self.add_entity(super_class_label)
        for sub_class_label in sub_class_labels:
            if not self.has_entity(sub_class_label):
                self.add_entity(sub_class_label)

        # Create isA relation
        is_a_id = self.__id()
        self.graph.add_node(
            is_a_id,
            is_total=is_total,
            is_disjunct=is_disjunct,
            custom_text=custom_text,
            node_type=erdiagram.NodeType.IS_A,
        )

        # Add directed edge from superclass to isA relation
        super_class_id = self.get_entity_by_label(super_class_label)["id"]
        self.graph.add_edge(super_class_id, is_a_id)

        # Add directed edges from isA relation to subclasses
        for sub_class_label in sub_class_labels:
            sub_class_id = self.get_entity_by_label(sub_class_label)["id"]
            self.graph.add_edge(is_a_id, sub_class_id)

    ###############
    # Get methods #
    ###############

    @typechecked
    def get_graph(self) -> nx.DiGraph:
        """
        Get the graph

        Returns
        -------
        nx.DiGraph
            The graph
        """
        return self.graph

    @typechecked
    def get_type_by_id(self, node_id: int) -> erdiagram.NodeType:
        """
        Get the type of a node

        Parameters
        ----------
        node_id : int
            Node id

        Returns
        -------
        erdiagram.NodeType
            Node type
        """
        assert self.graph.has_node(node_id), f"Node {node_id} does not exist"
        return self.graph.nodes[node_id]["node_type"]

    @typechecked
    def get_label_by_id(self, node_id: int) -> str:
        """
        Get the label of a node

        Parameters
        ----------
        node_id : int
            Node id

        Returns
        -------
        str
            Node label
        """
        assert self.graph.has_node(node_id), f"Node {node_id} does not exist"
        return self.graph.nodes[node_id]["label"]

    @typechecked
    def get_id_by_label(self, label: str) -> Optional[int]:
        """
        Get the id of a node

        Parameters
        ----------
        label : str
            Node label

        Returns
        -------
        Optional[int]
            Node id
        """
        return next(
            (
                id
                for (id, data) in self.graph.nodes(data=True)
                if self.get_type_by_id(id) is not erdiagram.NodeType.IS_A
                and data["label"] == label
            ),
            None,
        )

    @typechecked
    def get_complete_entity_data(self, id: int) -> dict[str, Any]:
        """
        Get the complete data of an entity (including its relations)

        Parameters
        ----------
        id : int
            Entity id

        Returns
        -------
        dict[str, Any]
            Dictionary containing the entity data
        """
        assert (
            self.get_type_by_id(id) == erdiagram.NodeType.ENTITY
        ), "Node is not an entity"

        data = self.graph.nodes[id]

        # Get relations
        relation_ids_from = [
            b
            for (a, b) in self.graph.edges()
            if a == id and self.get_type_by_id(b) == erdiagram.NodeType.RELATION
        ]
        relation_ids_to = [
            a
            for (a, b) in self.graph.edges()
            if b == id and self.get_type_by_id(a) == erdiagram.NodeType.RELATION
        ]

        # Get attributes
        attribute_ids = [
            b
            for (a, b) in self.graph.edges()
            if a == id and self.get_type_by_id(b) == erdiagram.NodeType.ATTRIBUTE
        ]

        # If the entity is a subclass, get the top isA relation
        is_a_super_id = next(
            (
                a
                for (a, b) in self.graph.edges()
                if b == id and self.get_type_by_id(a) == erdiagram.NodeType.IS_A
            ),
            None,
        )

        # If the entity is a superclass, get the isA relations to its subclasses
        is_a_sub_id = next(
            (
                b
                for (a, b) in self.graph.edges()
                if a == id and self.get_type_by_id(b) == erdiagram.NodeType.IS_A
            ),
            None,
        )

        return dict(
            data,
            id=id,
            relation_ids_from=relation_ids_from,
            relation_ids_to=relation_ids_to,
            attribute_ids=attribute_ids,
            is_a_super_id=is_a_super_id,
            is_a_sub_id=is_a_sub_id,
        )

    @typechecked
    def get_entities(self) -> list[dict[str, Any]]:
        """
        Get all entities in the graph as a list of dictionaries containing the entity data

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the entity data
        """
        entity_ids = [
            id
            for id in self.graph.nodes()
            if self.get_type_by_id(id) == erdiagram.NodeType.ENTITY
        ]
        return [self.get_complete_entity_data(id) for id in entity_ids]

    @typechecked
    def get_entity_by_label(self, entity_label: str) -> dict[str, Any]:
        """
        Get an entity by its label

        Parameters
        ----------
        entity_label : str
            Entity label

        Returns
        -------
        dict[str, Any]
            Dictionary containing the entity data

        Raises
        ------
        TypeError
            If the entity does not exist
        """
        id = self.get_id_by_label(entity_label)
        if id is None:
            raise TypeError(f"Entity {entity_label} does not exist")
        return self.get_complete_entity_data(id)

    @typechecked
    def get_entity_by_id(self, id: int) -> dict[str, Any]:
        """
        Get an entity by its id

        Parameters
        ----------
        id : int
            Entity id

        Returns
        -------
        dict[str, Any]
            Dictionary containing the entity data
        """
        return self.get_complete_entity_data(id)

    @typechecked
    def get_complete_attribute_data(self, id: int) -> dict[str, Any]:
        """
        Get the complete data of an attribute (including its relations)

        Parameters
        ----------
        id : int
            Attribute id

        Returns
        -------
        dict[str, Any]
            Dictionary containing the attribute data
        """
        assert (
            self.get_type_by_id(id) == erdiagram.NodeType.ATTRIBUTE
        ), "Node is not an attribute"

        data = self.graph.nodes[id]

        # Get the parent id and type
        parent_id = next((a for (a, b) in self.graph.edges() if b == id))
        parent_type = self.get_type_by_id(parent_id)
        assert parent_type in [
            erdiagram.NodeType.ENTITY,
            erdiagram.NodeType.RELATION,
        ], "Internal Error"

        # If attribute is composed of more attributes, get them (by outgoing edges)
        composed_of_attribute_ids = [
            b
            for (a, b) in self.graph.edges()
            if a == id
            and self.get_type_by_id(b) == erdiagram.NodeType.COMPOSED_ATTRIBUTE
        ]

        return dict(
            data,
            id=id,
            parent_id=parent_id,
            parent_type=parent_type,
            composed_of_attribute_ids=composed_of_attribute_ids,
        )

    @typechecked
    def get_attributes(self) -> list[dict[str, Any]]:
        """
        Get all attributes in the graph as a list of dictionaries containing the attribute data

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the attribute data
        """
        attribute_ids = [
            id
            for id in self.graph.nodes()
            if self.get_type_by_id(id) == erdiagram.NodeType.ATTRIBUTE
        ]
        return [self.get_complete_attribute_data(id) for id in attribute_ids]

    @typechecked
    def get_attribute_by_label(self, attribute_label: str) -> dict[str, Any]:
        """
        Get an attribute by its attribute label

        Parameters
        ----------
        attribute_label : str
            Attribute label

        Returns
        -------
        dict[str, Any]
            Dictionary containing the attribute data

        Raises
        ------
        TypeError
            If the attribute label is not found
        """
        id = self.get_id_by_label(attribute_label)
        if id is None:
            raise TypeError(f"Attribute with label {attribute_label} not found")
        return self.get_attribute_by_id(id)

    @typechecked
    def get_attribute_by_id(self, id: int) -> dict[str, Any]:
        """
        Get an attribute by its id

        Parameters
        ----------
        id : int
            Attribute id

        Returns
        -------
        dict[str, Any]
            Dictionary containing the attribute data
        """
        return self.get_complete_attribute_data(id)

    @typechecked
    def get_attributes_by_parent_label(self, parent_label: str) -> list[dict[str, Any]]:
        """
        Get all attributes by their parent label

        Parameters
        ----------
        parent_label : str
            Parent label

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the attribute data
        """
        return [
            attribute
            for attribute in self.get_attributes()
            if attribute["parent_label"] == parent_label
        ]

    @typechecked
    def get_attributes_by_parent_id(self, parent_id: int) -> list[dict[str, Any]]:
        """
        Get all attributes by their parent id

        Parameters
        ----------
        parent_id : int
            Parent id

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the attribute data
        """
        return [
            attribute
            for attribute in self.get_attributes()
            if attribute["parent_id"] == parent_id
        ]

    @typechecked
    def get_complete_composed_attribute_data(self, id: int) -> dict[str, Any]:
        """
        Get the complete data of a composed attribute (including its relations)

        Parameters
        ----------
        id : int
            Composed attribute id

        Returns
        -------
        dict[str, Any]
            Dictionary containing the composed attribute data
        """
        assert (
            self.get_type_by_id(id) == erdiagram.NodeType.COMPOSED_ATTRIBUTE
        ), "Node is not a composed attribute"

        data = self.graph.nodes[id]

        # Get the parent attribute id
        parent_id = next((a for (a, b) in self.graph.edges() if b == id))
        assert (
            self.get_type_by_id(parent_id) == erdiagram.NodeType.ATTRIBUTE
        ), "Internal Error"

        return dict(data, id=id, parent_id=parent_id)

    @typechecked
    def get_composed_attributes(self) -> list[dict[str, Any]]:
        """
        Get all composed attributes in the graph as a list of dictionaries containing the attribute data

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the composed attribute data
        """
        composed_attribute_ids = [
            id
            for id in self.graph.nodes()
            if self.get_type_by_id(id) == erdiagram.NodeType.COMPOSED_ATTRIBUTE
        ]
        return [
            self.get_complete_composed_attribute_data(id)
            for id in composed_attribute_ids
        ]

    @typechecked
    def get_composed_attribute_by_label(
        self, composed_attribute_label: str
    ) -> dict[str, Any]:
        """
        Get a composed attribute by its composed attribute label

        Parameters
        ----------
        composed_attribute_label : str
            Composed attribute label

        Returns
        -------
        dict[str, Any]
            Dictionary containing the composed attribute data
        """
        id = self.get_id_by_label(composed_attribute_label)
        if id is None:
            raise TypeError(
                f"Composed attribute with label {composed_attribute_label} not found"
            )
        return self.get_composed_attribute_by_id(id)

    @typechecked
    def get_composed_attribute_by_id(self, id: int) -> dict[str, Any]:
        """
        Get a composed attribute by its id

        Parameters
        ----------
        id : int
            Composed attribute id

        Returns
        -------
        dict[str, Any]
            Dictionary containing the composed attribute data
        """
        return self.get_complete_composed_attribute_data(id)

    @typechecked
    def get_complete_relation_data(self, id: int) -> dict[str, Any]:
        """
        Get the complete data of a relation (including its attributes)

        Parameters
        ----------
        id : int
            Relation id

        Returns
        -------
        dict[str, Any]
            Dictionary containing the relation data
        """
        assert (
            self.get_type_by_id(id) == erdiagram.NodeType.RELATION
        ), "Node is not a relation"

        data = self.graph.nodes[id]

        # Get entities and edges ingoing into this relation
        from_edges = [
            edge
            for edge in self.graph.reverse().edges(id, data=True)
            if self.get_type_by_id(edge[1]) == erdiagram.NodeType.ENTITY
        ]
        from_entities = [self.get_entity_by_id(edge[1]) for edge in from_edges]
        # Get entities and edges outgoing from this relation
        to_edges = [
            edge
            for edge in self.graph.edges(id, data=True)
            if self.get_type_by_id(edge[1]) == erdiagram.NodeType.ENTITY
        ]
        to_entities = [self.get_entity_by_id(edge[1]) for edge in to_edges]

        # Get any attributes of this relation
        attribute_ids = [
            b
            for (a, b) in self.graph.edges()
            if a == id and self.get_type_by_id(b) == erdiagram.NodeType.ATTRIBUTE
        ]

        # Build relation dictionary (from, relation, to; with from and to being {entityLabel: {cardinality: cardinality, is_weak: is_weak}})
        from_dict = {
            entity["label"]: {
                "id": entity["id"],
                "cardinality": edge[2]["cardinality"],
                "is_weak": edge[2]["is_weak"],
            }
            for (entity, edge) in zip(from_entities, from_edges)
        }
        to_dict = {
            entity["label"]: {
                "id": entity["id"],
                "cardinality": edge[2]["cardinality"],
                "is_weak": edge[2]["is_weak"],
            }
            for (entity, edge) in zip(to_entities, to_edges)
        }

        return dict(
            data,
            id=id,
            attribute_ids=attribute_ids,
            from_entities=from_dict,
            to_entities=to_dict,
        )

    @typechecked
    def get_relations(self) -> list[dict[str, Any]]:
        """
        Get all relations in the graph as a list of dictionaries containing the relation data

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the relation data
        """
        relation_ids = [
            id
            for id in self.graph.nodes()
            if self.get_type_by_id(id) == erdiagram.NodeType.RELATION
        ]
        return [self.get_complete_relation_data(id) for id in relation_ids]

    @typechecked
    def get_relation_by_label(self, relation_label: str) -> dict[str, Any]:
        """
        Get a relation by its label

        Parameters
        ----------
        relation_label : str
            Relation label

        Returns
        -------
        dict[str, Any]
            Dictionary containing the relation data

        Raises
        ------
        TypeError
            If the relation label is not found in the graph
        """
        id = self.get_id_by_label(relation_label)
        if id is None:
            raise TypeError(f"Relation with label {relation_label} not found")
        return self.get_relation_by_id(id)

    @typechecked
    def get_relation_by_id(self, id: int) -> dict[str, Any]:
        """
        Get a relation by its id

        Parameters
        ----------
        id : int
            Relation id

        Returns
        -------
        dict[str, Any]
            Dictionary containing the relation data
        """
        return self.get_complete_relation_data(id)

    @typechecked
    def get_relations_from_entity_label(
        self, entity_label: str
    ) -> list[dict[str, Any]]:
        """
        Get all relations from an entity in the graph as a list of dictionaries containing the relation data

        Parameters
        ----------
        entity_label : str
            Label of the entity

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the relation data
        """
        return [
            self.get_complete_relation_data(id)
            for id in self.get_entity_by_label(entity_label)["relation_ids_from"]
        ]

    @typechecked
    def get_relations_from_entity_id(self, entity_id: int) -> list[dict[str, Any]]:
        """
        Get all relations from an entity in the graph as a list of dictionaries containing the relation data

        Parameters
        ----------
        entity_id : int
            Id of the entity

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the relation data
        """
        return [
            self.get_complete_relation_data(id)
            for id in self.get_entity_by_id(entity_id)["relation_ids_from"]
        ]

    @typechecked
    def get_relations_to_entity_label(self, entity_label: str) -> list[dict[str, Any]]:
        """
        Get all relations to an entity in the graph as a list of dictionaries containing the relation data

        Parameters
        ----------
        entity_label : str
            Label of the entity

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the relation data
        """
        return [
            self.get_complete_relation_data(id)
            for id in self.get_entity_by_label(entity_label)["relation_ids_to"]
        ]

    @typechecked
    def get_relations_to_entity_id(self, entity_id: int) -> list[dict[str, Any]]:
        """
        Get all relations to an entity in the graph as a list of dictionaries containing the relation data

        Parameters
        ----------
        entity_id : int
            Id of the entity

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the relation data
        """
        return [
            self.get_complete_relation_data(id)
            for id in self.get_entity_by_id(entity_id)["relation_ids_to"]
        ]

    @typechecked
    def get_complete_is_a_data(self, id: int) -> dict[str, Any]:
        """
        Get all data of an isA relation in the graph as a dictionary containing the relation data

        Parameters
        ----------
        id : int
            Id of the isA relation

        Returns
        -------
        dict[str, Any]
            Dictionary containing the isA data
        """
        assert (
            self.get_type_by_id(id) == erdiagram.NodeType.IS_A
        ), "Id is not of type isA"

        data = self.graph.nodes[id]

        # Get superclass (in-edge)
        superclass_id = next((a for (a, b) in self.graph.edges() if b == id))
        assert (
            self.get_type_by_id(superclass_id) == erdiagram.NodeType.ENTITY
        ), "Internal Error"

        # Get subclasses (out-edges)
        subclass_ids = [b for (a, b) in self.graph.edges() if a == id]
        assert len(subclass_ids) > 0 and all(
            self.get_type_by_id(subclass) == erdiagram.NodeType.ENTITY
            for subclass in subclass_ids
        ), "Internal Error"

        return dict(data, id=id, superclass_id=superclass_id, subclass_ids=subclass_ids)

    @typechecked
    def get_is_as(self) -> list[dict[str, Any]]:
        """
        Get all isA relations in the graph as a list of dictionaries containing the relation data

        Returns
        -------
        list[dict[str, Any]]
            List of dictionaries containing the is_a data
        """
        is_a_ids = [
            id
            for id in self.graph.nodes()
            if self.get_type_by_id(id) == erdiagram.NodeType.IS_A
        ]
        return [self.get_complete_is_a_data(id) for id in is_a_ids]

    @typechecked
    def get_is_a_by_id(self, id: int) -> dict[str, Any]:
        """
        Get an isA relation by its id

        Parameters
        ----------
        id : int
            Id of the isA relation

        Returns
        -------
        dict[str, Any]
            Dictionary containing the isA data
        """
        return self.get_complete_is_a_data(id)

    ###############
    # Has methods #
    ###############

    @typechecked
    def id_is_type(self, id: int, node_type: erdiagram.NodeType) -> bool:
        """
        Check if a node id is of a certain type

        Parameters
        ----------
        id : int
            Node id
        node_type : erdiagram.NodeType
            Type of the node

        Returns
        -------
        bool
            True if the node is of the given type, False otherwise
        """
        # Get node
        node = self.graph.nodes[id]
        if node is None:
            raise ValueError(f"Node with id {id} does not exist")
        # Check if node is of the given type
        return node["node_type"] == node_type

    @typechecked
    def has_entity(self, label: str) -> bool:
        """
        Check if an entity exists in the graph

        Parameters
        ----------
        label : str
            Label of the entity

        Returns
        -------
        bool
            True if the entity exists, False otherwise
        """
        # Get all entities
        entities = self.get_entities()
        # Check if entity exists
        return label in [entity["label"] for entity in entities]

    @typechecked
    def has_attibute(self, label: str) -> bool:
        """
        Check if an attribute exists in the graph

        Parameters
        ----------
        label : str
            Label of the attribute

        Returns
        -------
        bool
            True if the attribute exists, False otherwise
        """
        # Get all attributes
        attributes = self.get_attributes()
        # Check if attribute exists
        return label in [attribute["label"] for attribute in attributes]

    @typechecked
    def has_attribute(self, parent_label: str, attribute_label: str) -> bool:
        """
        Check if a parent entity has a specific attribute

        Parameters
        ----------
        parent_label : str
            Label of the parent entity
        attribute_label : str
            Label of the attribute

        Returns
        -------
        bool
            True if the attribute exists, False otherwise
        """
        # Get parent id
        parent_id = self.get_id_by_label(parent_label)
        # Get type of parent
        parent_type = self.get_type_by_id(parent_id)
        # Get parent node
        if parent_type == erdiagram.NodeType.ENTITY:
            parent = self.get_entity_by_id(parent_id)
        elif parent_type == erdiagram.NodeType.RELATION:
            parent = self.get_relation_by_id(parent_id)
        else:
            raise ValueError(f"Node with id {parent_id} is not an entity or relation")
        # Check if attribute exists
        try:
            attribute = self.get_attribute_by_label(attribute_label)
        except TypeError:  # NoneType -> attribute does not exist
            return False
        return attribute["id"] in parent["attribute_ids"]

    @typechecked
    def has_composed_attribute(self, label: str) -> bool:
        """
        Check if a composed attribute exists in the graph

        Parameters
        ----------
        label : str
            Label of the composed attribute

        Returns
        -------
        bool
            True if the composed attribute exists, False otherwise
        """
        # Get all composed attributes
        composedAttributes = self.get_composed_attributes()
        # Check if composed attribute exists
        return label in [
            composedAttribute["label"] for composedAttribute in composedAttributes
        ]

    @typechecked
    def has_relation(self, label: str) -> bool:
        """
        Check if a relation exists in the graph

        Parameters
        ----------
        label : str
            Label of the relation

        Returns
        -------
        bool
            True if the relation exists, False otherwise
        """
        # Get all relations
        relations = self.get_relations()
        # Check if relation exists
        return label in [relation["label"] for relation in relations]

    @typechecked
    def has_is_a_super(self, superclass_label: str) -> bool:
        """
        Check if an isA relation exists in the graph with specified superclass label

        Parameters
        ----------
        superclass_label : str
            Label of the isA relation

        Returns
        -------
        bool
            True if the isA relation exists, False otherwise
        """
        # Get all isA relations
        isAs = self.get_is_as()
        # Check if isA relation exists
        return superclass_label in [
            self.get_entity_by_id(isA["superclass_id"])["label"] for isA in isAs
        ]

    #################
    # Other Methods #
    #################

    @typechecked
    def as_solution(self, format="json"):
        if format == "json":
            return json_graph.node_link_data(self.graph)

        return "please pick data format"
