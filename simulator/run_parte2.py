#!/usr/bin/env python3
"""Valida a Parte 2 sem ROS 2: exploração DFS + reset + BFS."""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401
from _bootstrap import ROOT
from cg_solver.exploration import explore_dfs, plan_from_exploration
from cg_solver.grid import directions_only, save_csv
from maze_sim import MazeSim


def execute(sim: MazeSim, path) -> bool:
    for i, (direction, _) in enumerate(path, start=1):
        ok = sim.move(direction)
        print(f"{i:3d} | {direction:5s} | pos={sim.robot} ok={ok}")
        if not ok:
            return False
    return bool(sim.won)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parte 2 (simulador local)")
    parser.add_argument(
        "--map",
        default=str(ROOT / "src" / "cg" / "maps" / "test.csv"),
        help="Caminho do CSV do labirinto",
    )
    parser.add_argument(
        "--out",
        default=str(ROOT / "mapa_descoberto.csv"),
        help="Arquivo CSV do mapa descoberto",
    )
    args = parser.parse_args()

    sim = MazeSim(args.map)

    print(f"Mapa: {args.map}")
    print("Explorando com DFS + backtracking...")
    explorer = explore_dfs(sim.move, sim.sensors)

    if sim.won:
        print("ERRO: robô pisou no alvo durante a exploração")
        sys.exit(1)

    plan = plan_from_exploration(explorer)
    save_csv(plan.grid, args.out)
    print(f"Mapa descoberto salvo em: {args.out}")
    print(
        f"células={len(explorer.known)} visitadas={len(explorer.visited)} "
        f"movimentos_exploracao={explorer.move_count}"
    )
    print(f"Início relativo={plan.start} alvo relativo={plan.target}")

    if plan.path is None:
        print("ERRO: alvo não encontrado")
        sys.exit(1)

    print(f"Rota ótima: {len(plan.path)} movimentos")
    print("Rota:", " ".join(directions_only(plan.path)))

    sim.reset()
    if execute(sim, plan.path):
        print(
            f"SUCESSO: missão completa em {len(plan.path)} movimentos "
            "(após exploração)"
        )
    else:
        print("ERRO na execução pós-exploração")
        sys.exit(1)


if __name__ == "__main__":
    main()
