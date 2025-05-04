from typing import Dict, List, Set

def is_acyclic(nodes: List[str], edges: Dict[str, List[str]]) -> bool:
    visited: Set[str] = set()
    rec_stack: Set[str] = set()

    def dfs(vertex: str) -> bool:
        visited.add(vertex)
        rec_stack.add(vertex)
        for neighbor in edges.get(vertex, []):
            if neighbor not in visited:
                if not dfs(neighbor):
                    return False
            elif neighbor in rec_stack:
                return False
        rec_stack.remove(vertex)
        return True

    for vertex in nodes:
        if vertex not in visited:
            if not dfs(vertex):
                return False
    return True