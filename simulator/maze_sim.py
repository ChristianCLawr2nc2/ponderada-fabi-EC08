"""Simulador leve do Culling Games (sem ROS 2 / Pygame)."""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "cg_solver"))

from cg_solver.grid import (  # noqa: E402
    BLOCKED,
    FREE,
    MOVE_DELTA,
    ROBOT,
    SENSOR_OFFSETS,
    TARGET,
    find_cell,
    load_csv,
)

Position = Tuple[int, int]


class MazeSim:
    def __init__(self, map_path: str | Path):
        self.map_path = Path(map_path)
        self.initial = load_csv(self.map_path)
        self.grid: List[List[str]] = []
        self.robot: Optional[Position] = None
        self.target: Optional[Position] = None
        self.won = False
        self.reset()

    def reset(self, reload: bool = False) -> None:
        if reload:
            self.initial = load_csv(self.map_path)
        self.grid = copy.deepcopy(self.initial)
        self.robot = find_cell(self.grid, ROBOT)
        self.target = find_cell(self.grid, TARGET)
        self.won = False
        if self.robot is None or self.target is None:
            raise ValueError("Mapa precisa ter 'r' e 't'")

    def flatten(self) -> Tuple[List[str], Tuple[int, int]]:
        rows, cols = len(self.grid), len(self.grid[0])
        return [cell for row in self.grid for cell in row], (rows, cols)

    def sensors(self) -> Dict[str, str]:
        assert self.robot is not None
        r, c = self.robot
        rows, cols = len(self.grid), len(self.grid[0])
        reading: Dict[str, str] = {}
        for name, (dr, dc) in SENSOR_OFFSETS.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                reading[name] = self.grid[nr][nc]
            else:
                reading[name] = BLOCKED
        return reading

    def move(self, direction: str) -> bool:
        if self.won or direction not in MOVE_DELTA:
            return False
        assert self.robot is not None and self.target is not None

        dr, dc = MOVE_DELTA[direction]
        nr, nc = self.robot[0] + dr, self.robot[1] + dc
        if not (0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[0])):
            return False
        if self.grid[nr][nc] == BLOCKED:
            return False

        self.grid[self.robot[0]][self.robot[1]] = FREE
        self.grid[nr][nc] = ROBOT
        self.robot = (nr, nc)
        if self.robot == self.target:
            self.won = True
        return True
