from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dag_service.db.connection import get_session
from dag_service.services import insert_graph, read_graph_canonical_form, read_graph_adjacency_list_form
from dag_service.schemas import *



api_router = APIRouter(prefix="/graph")


@api_router.post("/api/graph/", response_model=GraphCreateResponse, status_code=201, responses={
    400: {"model": ErrorResponse, "description": "Invalid graph data (e.g., duplicate nodes, cycle)"},
    422: {"model": HTTPValidationError, "description": "Validation Error"}
})
async def create_graph(graph: GraphCreate,
                       session: AsyncSession = Depends(get_session)):
    new_dag_id = await insert_graph(graph,session)
    return GraphCreateResponse(id=new_dag_id)


@api_router.get("/api/graph/{graph_id}", response_model=GraphReadResponse, responses={
    200: {"model": GraphReadResponse, "description": "Successful Response"},
    404: {"model": ErrorResponse, "description": "Graph entity not found"},
    422: {"model": HTTPValidationError, "description": "Validation Error"}
})
async def get_graph(graph_id: int = Path(..., title="Graph Id"), session: AsyncSession = Depends(get_session)):
    return (await  read_graph_canonical_form(graph_id, session))


@api_router.get("/api/graph/{graph_id}/adjacency_list", response_model=AdjacencyListResponse)
async def get_adjacency_list(graph_id: int = Path(..., title="Graph Id"), session: AsyncSession = Depends(get_session)):
    return (await read_graph_adjacency_list_form(graph_id,session))


@api_router.get("/api/graph/{graph_id}/reverse_adjacency_list", response_model=AdjacencyListResponse, responses={
    200: {"model": AdjacencyListResponse, "description": "Successful Response"},
    404: {"model": ErrorResponse, "description": "Graph entity not found"},
    422: {"model": HTTPValidationError, "description": "Validation Error"}
})
async def get_reverse_adjacency_list(graph_id: int = Path(..., title="Graph Id")):
    """
    Get Reverse Adjacency List

    Ручка для чтения транспонированного графа в виде списка смежности.
    """
    pass  # Логика получения транспонированного списка смежности


@api_router.delete("/api/graph/{graph_id}/node/{node_name}", status_code=204, responses={
    204: {"description": "Successful Response"},
    404: {"model": ErrorResponse, "description": "Graph or node not found"},
    422: {"model": HTTPValidationError, "description": "Validation Error"}
})
async def delete_node(
        graph_id: int = Path(..., title="Graph Id"),
        node_name: str = Path(..., title="Node Name")
):
    """
    Delete Node

    Ручка для удаления вершины из графа по ее имени.
    """
    pass  # Логика удаления вершины
