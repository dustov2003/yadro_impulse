from typing import Any, Sequence

from fastapi import HTTPException
from sqlalchemy import Row, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dag_service.db.models import DAG, Edge, Node
from dag_service.schemas import AdjacencyListResponse
from dag_service.schemas import Edge as EdgeSchema
from dag_service.schemas import ErrorResponse, GraphCreate, GraphReadResponse
from dag_service.schemas import Node as NodeSchema


async def insert_graph(graph: GraphCreate, session: AsyncSession) -> int:
    try:
        new_dag = DAG()
        session.add(new_dag)
        await session.flush()

        new_nodes = [
            Node(dag_id=new_dag.dag_id, name=node.name) for node in graph.nodes
        ]
        session.add_all(new_nodes)
        await session.flush()

        node_id_map = {node.name: node.node_id for node in new_nodes}
        db_edges = [
            Edge(
                dag_id=new_dag.dag_id,
                source_node_id=node_id_map[edge.source],
                target_node_id=node_id_map[edge.target],
            )
            for edge in graph.edges
        ]
        session.add_all(db_edges)

        await session.commit()
        return new_dag.dag_id
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail={"message": str(e)})


async def get_graph_connections(
    dag_id: int, session: AsyncSession
) -> Sequence[Row[Any]]:
    node_alias = Node.__table__.alias("n")
    stmt = (
        select(Node.name, node_alias.c.name.label("target_name"))
        .join(Edge, Node.node_id == Edge.source_node_id)
        .join(node_alias, Edge.target_node_id == node_alias.c.node_id)
        .where(Node.dag_id == dag_id)
    )
    result = await session.execute(stmt)
    return result.all()


async def read_graph(
    dag_id: int, session: AsyncSession
) -> tuple[Sequence[Node], Sequence[Row[Any]]]:
    dag = await session.get(DAG, dag_id)
    if not dag:
        raise HTTPException(
            status_code=404, detail={"message": f"Graph with id {dag_id} not found"}
        )
    nodes = (
        (await session.execute(select(Node).filter_by(dag_id=dag_id))).scalars().all()
    )
    edges = await get_graph_connections(dag_id, session)
    return nodes, edges


async def read_graph_canonical_form(
    dag_id: int, session: AsyncSession
) -> GraphReadResponse:
    nodes, edges = await read_graph(dag_id, session)
    return GraphReadResponse(
        id=dag_id,
        nodes=[NodeSchema(name=node.name) for node in nodes],
        edges=[EdgeSchema(source=edge[0], target=edge[1]) for edge in edges],
    )


async def read_graph_adjacency_list_form(
    dag_id: int, session: AsyncSession
) -> AdjacencyListResponse:
    nodes, edges = await read_graph(dag_id, session)
    adjacency_list = {node.name: [] for node in nodes}
    for edge in edges:
        adjacency_list[edge[0]].append(edge[1])
    return AdjacencyListResponse(adjacency_list=adjacency_list)


async def read_graph_reverse_adjacency_list_form(
    dag_id: int, session: AsyncSession
) -> AdjacencyListResponse:
    nodes, edges = await read_graph(dag_id, session)
    adjacency_list = {node.name: [] for node in nodes}
    for edge in edges:
        adjacency_list[edge[1]].append(edge[0])
    return AdjacencyListResponse(adjacency_list=adjacency_list)


async def count_nodes_by_dag_id(dag_id: int, session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(Node).where(Node.dag_id == dag_id)
    result = await session.execute(stmt)
    return result.scalar()


async def delete_node(dag_id: int, node_name: str, session: AsyncSession):
    nodes_number = await count_nodes_by_dag_id(
        dag_id, session
    )  # по сути так можно узнать одновременно существует ли такой граф (так как у графа минимум одна нода) и узнать количество нод
    if nodes_number < 1:
        raise HTTPException(
            status_code=404, detail=ErrorResponse(message="ladno").model_dump()
        )

    node = (
        await session.execute(select(Node).filter_by(dag_id=dag_id, name=node_name))
    ).scalar()
    if not node:
        raise HTTPException(
            status_code=404,
            detail={"message": f"Node '{node_name}' not found in graph {dag_id}"},
        )
    if nodes_number == 1:
        await session.execute(delete(DAG).where(DAG.dag_id == dag_id))
    else:
        await session.delete(node)
    await session.commit()
