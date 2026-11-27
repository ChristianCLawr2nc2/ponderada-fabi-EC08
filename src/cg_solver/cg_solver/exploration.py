"""Exploração cega com sensores locais (DFS + backtracking).

O robô não pisa no alvo durante a exploração — isso encerraria o jogo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple

from .grid import (
    BLOCKED,
    FREE,
    MOVES,
    OPPOSITE,
    ROBOT,
    SENSOR_OFFSETS,
    TARGET,
    Grid,
    Position,
    Step,
    neighbor,
)
from .pathfinding import bfs_shortest_path

SensorReading = Dict[str, str]
MoveFn = Callable[[str], bool]
SenseFn = Callable[[], SensorReading]
LogFn = Callable[[str], None]


@dataclass
class PlanResult:
    path: Optional[List[Step]]
    grid: Grid
    start: Position
    target: Optional[Position]


@dataclass
class Explorer:
    """Mapa relativo construído a partir de sensores 8-direções."""

    pos: Position = (0, 0)
    known: Dict[Position, str] = field(default_factory=lambda: {(0, 0): FREE})
    visited: Set[Position] = field(default_factory=lambda: {(0, 0)})
    target: Optional[Position] = None
    move_count: int = 0

    def register_sensors(self, reading: SensorReading) -> None:
        for name, (dr, dc) in SENSOR_OFFSETS.items():
            value = reading.get(name)
            if value is None:
                continue
            cell = (self.pos[0] + dr, self.pos[1] + dc)
            # Mantém o alvo se já foi visto e o sensor atual não o reporta
            if self.known.get(cell) == TARGET and value != TARGET:
                continue
            self.known[cell] = value
            if value == TARGET:
                self.target = cell

    def apply_move(self, direction: str) -> None:
        self.pos = neighbor(self.pos, direction)
        self.visited.add(self.pos)
        self.known[self.pos] = FREE
        self.move_count += 1

    def mark_blocked(self, direction: str) -> None:
        self.known[neighbor(self.pos, direction)] = BLOCKED

    def unvisited_neighbors(self) -> List[Tuple[str, Position]]:
        """Vizinhos ortogonais livres ainda não visitados (exceto o alvo)."""
        options: List[Tuple[str, Position]] = []
        for direction, dr, dc in MOVES:
            nxt = (self.pos[0] + dr, self.pos[1] + dc)
            cell = self.known.get(nxt)
            if cell is None or cell == BLOCKED:
                continue
            if cell == TARGET:
                self.target = nxt
                continue
            if nxt in self.visited:
                continue
            options.append((direction, nxt))
        return options

    def to_grid(self) -> Tuple[Grid, Position, Optional[Position]]:
        """Converte o mapa esparso em grade densa com 'r' e 't'."""
        if not self.known:
            return [], (0, 0), None

        rows = [p[0] for p in self.known]
        cols = [p[1] for p in self.known]
        min_r, max_r = min(rows), max(rows)
        min_c, max_c = min(cols), max(cols)

        height = max_r - min_r + 1
        width = max_c - min_c + 1
        grid: Grid = [[BLOCKED for _ in range(width)] for _ in range(height)]

        for (r, c), value in self.known.items():
            gr, gc = r - min_r, c - min_c
            if value == TARGET:
                grid[gr][gc] = TARGET
            elif value == BLOCKED:
                grid[gr][gc] = BLOCKED
            else:
                grid[gr][gc] = FREE

        start = (-min_r, -min_c)
        grid[start[0]][start[1]] = ROBOT

        target = None
        if self.target is not None:
            target = (self.target[0] - min_r, self.target[1] - min_c)
            grid[target[0]][target[1]] = TARGET

        return grid, start, target


def explore_dfs(
    move: MoveFn,
    sense: SenseFn,
    logger: LogFn = print,
) -> Explorer:
    """Explora o espaço alcançável e termina de volta à origem."""
    explorer = Explorer()
    stack: List[str] = []

    explorer.register_sensors(sense())
    logger(f"[explore] início em {explorer.pos}")

    while True:
        options = explorer.unvisited_neighbors()
        if options:
            direction, _ = options[0]
            if not move(direction):
                explorer.mark_blocked(direction)
                continue
            explorer.apply_move(direction)
            stack.append(direction)
            explorer.register_sensors(sense())
            continue

        if not stack:
            break

        back = OPPOSITE[stack.pop()]
        if not move(back):
            raise RuntimeError(f"Falha no backtracking com '{back}'")
        explorer.apply_move(back)
        explorer.register_sensors(sense())

    logger(
        f"[explore] fim | células={len(explorer.known)} "
        f"visitadas={len(explorer.visited)} movimentos={explorer.move_count} "
        f"alvo={explorer.target}"
    )
    return explorer


def plan_from_exploration(explorer: Explorer) -> PlanResult:
    """BFS sobre o mapa descoberto, do início relativo até o alvo."""
    grid, start, target = explorer.to_grid()
    path = None
    if target is not None:
        path = bfs_shortest_path(grid, start=start, goal=target)
    return PlanResult(path=path, grid=grid, start=start, target=target)
