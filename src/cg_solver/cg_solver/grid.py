"""Tipos e utilitários compartilhados da grade do Culling Games."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

Position = Tuple[int, int]
Step = Tuple[str, Position]  # (direção, posição de destino)
Grid = List[List[str]]

# Movimento ortogonal: direção -> (delta_linha, delta_coluna)
MOVE_DELTA: Dict[str, Tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

MOVES: Tuple[Tuple[str, int, int], ...] = tuple(
    (name, dr, dc) for name, (dr, dc) in MOVE_DELTA.items()
)

OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}

# Sensores 8-direções (inclui diagonais)
SENSOR_OFFSETS: Dict[str, Tuple[int, int]] = {
    **MOVE_DELTA,
    "up_left": (-1, -1),
    "up_right": (-1, 1),
    "down_left": (1, -1),
    "down_right": (1, 1),
}

WALKABLE = frozenset({"f", "t", "r"})
BLOCKED = "b"
FREE = "f"
ROBOT = "r"
TARGET = "t"


def reshape_map(flattened: Sequence[str], shape: Sequence[int]) -> Grid:
    rows, cols = int(shape[0]), int(shape[1])
    if rows < 1 or cols < 1 or len(flattened) != rows * cols:
        raise ValueError(
            f"Mapa inválido: shape=({rows},{cols}), len={len(flattened)}"
        )
    return [list(flattened[r * cols : (r + 1) * cols]) for r in range(rows)]


def find_cell(grid: Sequence[Sequence[str]], value: str) -> Optional[Position]:
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == value:
                return r, c
    return None


def in_bounds(grid: Sequence[Sequence[str]], pos: Position) -> bool:
    r, c = pos
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])


def is_walkable(grid: Sequence[Sequence[str]], pos: Position) -> bool:
    return in_bounds(grid, pos) and grid[pos[0]][pos[1]] in WALKABLE


def neighbor(pos: Position, direction: str) -> Position:
    dr, dc = MOVE_DELTA[direction]
    return pos[0] + dr, pos[1] + dc


def orthogonal_neighbors(pos: Position) -> Iterable[Tuple[str, Position]]:
    for direction, (dr, dc) in MOVE_DELTA.items():
        yield direction, (pos[0] + dr, pos[1] + dc)


def load_csv(path: str | Path) -> Grid:
    with open(path, newline="", encoding="utf-8") as f:
        return [row for row in csv.reader(f) if row]


def save_csv(grid: Sequence[Sequence[str]], path: str | Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(grid)


def directions_only(path: Iterable[Step]) -> List[str]:
    return [direction for direction, _ in path]
