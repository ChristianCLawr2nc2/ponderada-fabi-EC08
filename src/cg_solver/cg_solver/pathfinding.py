"""Pathfinding: BFS (ótimo em custo uniforme) e A* (Manhattan)."""

from __future__ import annotations

import heapq
from collections import deque
from typing import Dict, List, Optional, Sequence, Tuple

from .grid import (
    MOVES,
    Position,
    Step,
    TARGET,
    ROBOT,
    find_cell,
    is_walkable,
    reshape_map,
)


def _endpoints(
    grid: Sequence[Sequence[str]],
    start: Optional[Position],
    goal: Optional[Position],
) -> Optional[Tuple[Position, Position]]:
    start = start or find_cell(grid, ROBOT)
    goal = goal or find_cell(grid, TARGET)
    if start is None or goal is None:
        return None
    return start, goal


def _reconstruct(
    previous: Dict[Position, Optional[Tuple[Position, str]]],
    start: Position,
    goal: Position,
) -> Optional[List[Step]]:
    if goal not in previous:
        return None
    path: List[Step] = []
    current = goal
    while current != start:
        parent_info = previous[current]
        if parent_info is None:
            return None
        parent, direction = parent_info
        path.append((direction, current))
        current = parent
    path.reverse()
    return path


def bfs_shortest_path(
    grid: Sequence[Sequence[str]],
    start: Optional[Position] = None,
    goal: Optional[Position] = None,
) -> Optional[List[Step]]:
    """Caminho mínimo em grade com custo 1 por passo."""
    ends = _endpoints(grid, start, goal)
    if ends is None:
        return None
    start, goal = ends

    queue = deque([start])
    previous: Dict[Position, Optional[Tuple[Position, str]]] = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for direction, dr, dc in MOVES:
            neighbor = (current[0] + dr, current[1] + dc)
            if neighbor in previous or not is_walkable(grid, neighbor):
                continue
            previous[neighbor] = (current, direction)
            queue.append(neighbor)

    return _reconstruct(previous, start, goal)


def astar_shortest_path(
    grid: Sequence[Sequence[str]],
    start: Optional[Position] = None,
    goal: Optional[Position] = None,
) -> Optional[List[Step]]:
    """A* com heurística Manhattan (admissível → caminho ótimo)."""
    ends = _endpoints(grid, start, goal)
    if ends is None:
        return None
    start, goal = ends

    def h(pos: Position) -> int:
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    open_heap: List[Tuple[int, int, Position]] = []
    counter = 0
    heapq.heappush(open_heap, (h(start), counter, start))

    previous: Dict[Position, Optional[Tuple[Position, str]]] = {start: None}
    g_score = {start: 0}

    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current == goal:
            break
        for direction, dr, dc in MOVES:
            neighbor = (current[0] + dr, current[1] + dc)
            if not is_walkable(grid, neighbor):
                continue
            tentative = g_score[current] + 1
            if tentative >= g_score.get(neighbor, float("inf")):
                continue
            previous[neighbor] = (current, direction)
            g_score[neighbor] = tentative
            counter += 1
            heapq.heappush(open_heap, (tentative + h(neighbor), counter, neighbor))

    return _reconstruct(previous, start, goal)


_ALGORITHMS = {
    "bfs": bfs_shortest_path,
    "astar": astar_shortest_path,
}


def shortest_path(
    grid: Sequence[Sequence[str]],
    algorithm: str = "bfs",
    start: Optional[Position] = None,
    goal: Optional[Position] = None,
) -> Optional[List[Step]]:
    try:
        planner = _ALGORITHMS[algorithm]
    except KeyError as exc:
        raise ValueError(f"Algoritmo desconhecido: {algorithm}") from exc
    return planner(grid, start=start, goal=goal)


def path_from_flattened(
    flattened: Sequence[str],
    shape: Sequence[int],
    algorithm: str = "bfs",
) -> Optional[List[Step]]:
    return shortest_path(reshape_map(flattened, shape), algorithm=algorithm)
