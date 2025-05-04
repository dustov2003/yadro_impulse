from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from dag_service.schemas import GraphCreate, GraphReadResponse, AdjacencyListResponse
from dag_service.schemas import Node as NodeSchema
from dag_service.schemas import Edge as EdgeSchema
from dag_service.db.models import DAG, Node, Edge
from typing import Tuple,List



async def insert_graph(graph: GraphCreate, session: AsyncSession) -> int:
    try:
        new_dag = DAG()
        session.add(new_dag)
        await session.flush()

        new_nodes = [Node(dag_id=new_dag.dag_id, name=node.name) for node in graph.nodes]
        session.add_all(new_nodes)
        await session.flush()

        node_id_map = {node.name: node.node_id for node in new_nodes}
        db_edges = [
            Edge(
                dag_id=new_dag.dag_id,
                source_node_id=node_id_map[edge.source],
                target_node_id=node_id_map[edge.target]
            )
            for edge in graph.edges
        ]
        session.add_all(db_edges)

        await session.commit()
        return new_dag.dag_id
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail={"message": str(e)})


async def read_graph(dag_id: int, session: AsyncSession) -> Tuple[List[Node], List[Edge]]:
    dag = await session.get(DAG, dag_id)
    if not dag:
        raise HTTPException(status_code=404, detail={"message": f"Graph with id {dag_id} not found"})
    nodes = (await session.execute(select(Node).filter_by(dag_id=dag_id))).scalars().all()
    edges = (await session.execute(select(Edge).filter_by(dag_id=dag_id))).scalars().all()
    return nodes, edges

async def read_graph_canonical_form(dag_id: int, session: AsyncSession) -> GraphReadResponse:
    nodes, edges = await read_graph(dag_id, session)
    node_id_to_name = {node.node_id: node.name for node in nodes}
    return GraphReadResponse(
        id=dag_id,
        nodes=[NodeSchema(name=node.name) for node in nodes],
        edges=[EdgeSchema(source=node_id_to_name[edge.source_node_id], target=node_id_to_name[edge.target_node_id]) for edge in edges]
    )

async def read_graph_adjacency_list_form(dag_id:int, session:AsyncSession) ->AdjacencyListResponse:
    nodes, edges = await read_graph(dag_id, session)
    node_id_to_name = {node.node_id: node.name for node in nodes}
    adjacency_list = {node.name:[] for node in nodes}
    for edge in edges:
        source_node = node_id_to_name[edge.source_node_id]
        target_node = node_id_to_name[edge.target_node_id]
        adjacency_list[source_node].append(target_node)
    return AdjacencyListResponse(
        adjacency_list=adjacency_list
    )