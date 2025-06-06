from typing import Dict, List

from pydantic import BaseModel, model_validator

from dag_service.utils import is_acyclic, is_valid_name


class Node(BaseModel):
    name: str

    @model_validator(mode="after")
    def validate_name(cls, node):
        if not is_valid_name(node.name):
            raise ValueError("Unvalid node name")
        return node


class Edge(BaseModel):
    source: str
    target: str


class GraphCreate(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

    @model_validator(mode="after")
    def validate_graph(cls, graph):

        if len(graph.nodes) == 0:
            raise ValueError("Graph must contain at least one node")

        node_names = [node.name for node in graph.nodes]
        node_set = set(node_names)

        if len(node_names) != len(node_set):
            raise ValueError("Duplicate node names found")

        edge_set = set()
        for edge in graph.edges:
            source = edge.source
            target = edge.target
            if source == target:
                raise ValueError(f"Self-loops are not allowed: {source} -> {target}")
            if source not in node_set:
                raise ValueError(f"Source node '{source}' not found in nodes")
            if target not in node_set:
                raise ValueError(f"Target node '{target}' not found in nodes")
            edge_tuple = (source, target)
            if edge_tuple in edge_set:
                raise ValueError("Duplicate edges found")
            edge_set.add(edge_tuple)

        nodes_list = node_names
        edges_dict = {node: [] for node in node_names}
        for edge in graph.edges:
            edges_dict[edge.source].append(edge.target)
        if not is_acyclic(nodes_list, edges_dict):
            raise ValueError("Graph contains a cycle")

        return graph


class GraphCreateResponse(BaseModel):
    id: int


class GraphReadResponse(BaseModel):
    id: int
    nodes: List[Node]
    edges: List[Edge]


class AdjacencyListResponse(BaseModel):
    adjacency_list: Dict[str, List[str]]


class ErrorResponse(BaseModel):
    message: str


class ValidationError(BaseModel):
    loc: List[str | int]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: List[ValidationError]
