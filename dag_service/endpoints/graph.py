from fastapi import APIRouter, Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dag_service.db.connection import get_session
from dag_service.services import *
from dag_service.schemas import *
from dag_service.utils import is_valid_name


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
    print('----------------------\n',(await count_nodes_by_dag_id(graph_id,session)),'\n----------------------\n')
    return (await  read_graph_canonical_form(graph_id, session))


@api_router.get("/api/graph/{graph_id}/adjacency_list", response_model=AdjacencyListResponse)
async def get_adjacency_list(graph_id: int = Path(..., title="Graph Id"), session: AsyncSession = Depends(get_session)):
    return (await read_graph_adjacency_list_form(graph_id,session))


@api_router.get("/api/graph/{graph_id}/reverse_adjacency_list", response_model=AdjacencyListResponse, responses={
    200: {"model": AdjacencyListResponse, "description": "Successful Response"},
    404: {"model": ErrorResponse, "description": "Graph entity not found"},
    422: {"model": HTTPValidationError, "description": "Validation Error"}
})
async def get_reverse_adjacency_list(graph_id: int = Path(..., title="Graph Id"), session: AsyncSession = Depends(get_session)):
    return (await read_graph_reverse_adjacency_list_form(graph_id,session))


@api_router.delete("/api/graph/{graph_id}/node/{node_name}", status_code=204, responses={
    204: {"description": "Successful Response"},
    404: {"model": ErrorResponse, "description": "Graph or node not found"},
    422: {"model": HTTPValidationError, "description": "Validation Error"}
})
async def delete_node_in_graph(
        graph_id: int = Path(..., title="Graph Id"),
        node_name: str = Path(..., title="Node Name"),
        session: AsyncSession = Depends(get_session)
):
    if is_valid_name(node_name):
        await delete_node(graph_id, node_name, session)
    else:
        raise HTTPException(status_code=422,detail="Unvalid node name")