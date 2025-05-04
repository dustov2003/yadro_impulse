from .graph import api_router as graph_router

list_of_routes = [
    graph_router,
]


__all__ = [
    "list_of_routes",
]