"""Parte 1 — navegação omnisciente: /get_map → pathfinding → /move_command."""

from __future__ import annotations

from cg_interfaces.srv import GetMap, MoveCmd

from .pathfinding import path_from_flattened
from .ros_utils import call_service, execute_path, ros_node, wait_for_service


def main(args=None) -> None:
    with ros_node("cg_solver_parte1", args=args) as node:
        algorithm = (
            node.declare_parameter("algorithm", "bfs")
            .get_parameter_value()
            .string_value
        )
        delay = (
            node.declare_parameter("delay", 0.05)
            .get_parameter_value()
            .double_value
        )

        map_client = node.create_client(GetMap, "/get_map")
        move_client = node.create_client(MoveCmd, "/move_command")
        wait_for_service(node, map_client, "/get_map")
        wait_for_service(node, move_client, "/move_command")

        node.get_logger().info(f"Parte 1 iniciada (algoritmo={algorithm})")
        map_response = call_service(node, map_client, GetMap.Request())
        path = path_from_flattened(
            map_response.occupancy_grid_flattened,
            map_response.occupancy_grid_shape,
            algorithm=algorithm,
        )

        if not path:
            node.get_logger().error("Nenhum caminho encontrado até o alvo")
            return

        node.get_logger().info(f"Caminho encontrado: {len(path)} movimentos")
        if execute_path(node, move_client, path, delay=delay):
            node.get_logger().info(f"Alvo alcançado em {len(path)} movimentos!")
        else:
            node.get_logger().error("Falha ao executar a rota")


if __name__ == "__main__":
    main()
