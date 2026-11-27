#!/usr/bin/env python3
"""Valida a Parte 1 sem ROS 2: pathfinding + execução no MazeSim."""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401
from _bootstrap import ROOT
from cg_solver.grid import directions_only
from cg_solver.pathfinding import path_from_flattened
from maze_sim import MazeSim


def execute(sim: MazeSim, path) -> bool:
    for i, (direction, expected) in enumerate(path, start=1):
        ok = sim.move(direction)
        print(f"{i:3d} | {direction:5s} | pos={sim.robot} expected={expected} ok={ok}")
        if not ok or sim.robot != expected:
            return False
    return bool(sim.won)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parte 1 (simulador local)")
    parser.add_argument(
        "--map",
        default=str(ROOT / "src" / "cg" / "maps" / "test.csv"),
        help="Caminho do CSV do labirinto",
    )
    parser.add_argument(
        "--algorithm",
        choices=("bfs", "astar"),
        default="bfs",
        help="Algoritmo de pathfinding",
    )
    args = parser.parse_args()

    sim = MazeSim(args.map)
    flat, shape = sim.flatten()
    path = path_from_flattened(flat, shape, algorithm=args.algorithm)

    if not path:
        print("ERRO: nenhum caminho encontrado")
        sys.exit(1)

    print(f"Mapa: {args.map}")
    print(f"Algoritmo: {args.algorithm}")
    print(f"Início: {sim.robot} | Alvo: {sim.target}")
    print(f"Caminho: {len(path)} movimentos")
    print("Rota:", " ".join(directions_only(path)))

    if execute(sim, path):
        print(f"SUCESSO: alvo alcançado em {len(path)} movimentos")
    else:
        print("ERRO na execução")
        sys.exit(1)


if __name__ == "__main__":
    main()
