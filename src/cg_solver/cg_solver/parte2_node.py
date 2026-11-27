"""Parte 2 — exploração cega + navegação ótima.

sensores → DFS → mapa → /reset → BFS → /move_command
"""

from __future__ import annotations

import os
import time
from typing import Dict, Optional

import rclpy
from cg_interfaces.msg import RobotSensors
from cg_interfaces.srv import MoveCmd, Reset
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from .exploration import explore_dfs, plan_from_exploration
from .grid import SENSOR_OFFSETS, save_csv
from .ros_utils import (
    call_service,
    execute_path,
    move_robot,
    ros_node,
    wait_for_service,
)


class SensorBuffer:
    """Última leitura do tópico de sensores."""

    def __init__(self) -> None:
        self._latest: Optional[Dict[str, str]] = None

    def callback(self, msg: RobotSensors) -> None:
        self._latest = {name: getattr(msg, name) for name in SENSOR_OFFSETS}

    def wait(self, node: Node, timeout: float = 5.0) -> Dict[str, str]:
        deadline = time.time() + timeout
        while self._latest is None and time.time() < deadline:
            rclpy.spin_once(node, timeout_sec=0.05)
        if self._latest is None:
            raise TimeoutError("Sem dados de sensor")
        return dict(self._latest)


def main(args=None) -> None:
    with ros_node("cg_solver_parte2", args=args) as node:
        delay = (
            node.declare_parameter("delay", 0.02)
            .get_parameter_value()
            .double_value
        )
        map_out = (
            node.declare_parameter("map_out", "mapa_descoberto.csv")
            .get_parameter_value()
            .string_value
        )

        move_client = node.create_client(MoveCmd, "/move_command")
        reset_client = node.create_client(Reset, "/reset")
        wait_for_service(node, move_client, "/move_command")
        wait_for_service(node, reset_client, "/reset")

        sensors = SensorBuffer()
        node.create_subscription(
            RobotSensors,
            "/culling_games/robot_sensors",
            sensors.callback,
            qos_profile_sensor_data,
        )

        def sense() -> Dict[str, str]:
            time.sleep(0.01)
            rclpy.spin_once(node, timeout_sec=0.05)
            return sensors.wait(node)

        def move(direction: str) -> bool:
            response = move_robot(node, move_client, direction, delay=delay)
            rclpy.spin_once(node, timeout_sec=0.02)
            return bool(response.success)

        node.get_logger().info("Parte 2: iniciando exploração DFS...")
        explorer = explore_dfs(move, sense, logger=node.get_logger().info)
        plan = plan_from_exploration(explorer)

        out_path = os.path.abspath(map_out)
        save_csv(plan.grid, out_path)
        node.get_logger().info(f"Mapa descoberto salvo em: {out_path}")
        node.get_logger().info(f"Início={plan.start} alvo={plan.target}")

        if plan.path is None:
            node.get_logger().error("Alvo não encontrado durante a exploração")
            return

        node.get_logger().info(
            f"Rota ótima no mapa descoberto: {len(plan.path)} movimentos"
        )

        reset_req = Reset.Request()
        reset_req.is_random = False
        reset_req.map_name = ""
        reset_resp = call_service(node, reset_client, reset_req)
        if not reset_resp.success:
            node.get_logger().error("Falha ao resetar o labirinto")
            return

        node.get_logger().info(
            f"Reset OK ({reset_resp.loaded_map_name}). Executando rota..."
        )
        time.sleep(0.2)

        if execute_path(node, move_client, plan.path, delay=delay):
            node.get_logger().info(
                f"Missão completa! {len(plan.path)} movimentos."
            )
        else:
            node.get_logger().error("Falha ao executar a rota após exploração")


if __name__ == "__main__":
    main()
