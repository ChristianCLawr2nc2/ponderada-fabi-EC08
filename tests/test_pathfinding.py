"""Testes unitários dos algoritmos (sem ROS)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "cg_solver"))

from cg_solver.exploration import explore_dfs, plan_from_exploration
from cg_solver.grid import load_csv
from cg_solver.pathfinding import astar_shortest_path, bfs_shortest_path, shortest_path

# Reusa o simulador local
sys.path.insert(0, str(ROOT / "simulator"))
from maze_sim import MazeSim  # noqa: E402


def _grid(name: str):
    return load_csv(ROOT / "src" / "cg" / "maps" / name)


def test_bfs_test_map_length():
    path = bfs_shortest_path(_grid("test.csv"))
    assert path is not None
    assert len(path) == 25


def test_astar_matches_bfs_length_on_test():
    grid = _grid("test.csv")
    assert len(bfs_shortest_path(grid)) == len(astar_shortest_path(grid))


def test_bfs_maze1_length():
    path = bfs_shortest_path(_grid("1.csv"))
    assert path is not None
    assert len(path) == 102


def test_shortest_path_dispatcher():
    grid = _grid("test.csv")
    assert len(shortest_path(grid, algorithm="bfs")) == 25
    assert len(shortest_path(grid, algorithm="astar")) == 25


def test_parte2_reproduces_parte1_on_test():
    sim = MazeSim(ROOT / "src" / "cg" / "maps" / "test.csv")
    explorer = explore_dfs(sim.move, sim.sensors)
    assert not sim.won
    plan = plan_from_exploration(explorer)
    assert plan.path is not None
    assert len(plan.path) == 25

    sim.reset()
    for direction, _ in plan.path:
        assert sim.move(direction)
    assert sim.won


if __name__ == "__main__":
    test_bfs_test_map_length()
    test_astar_matches_bfs_length_on_test()
    test_bfs_maze1_length()
    test_shortest_path_dispatcher()
    test_parte2_reproduces_parte1_on_test()
    print("OK: todos os testes passaram")
