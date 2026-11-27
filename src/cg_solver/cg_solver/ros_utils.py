"""Helpers compartilhados para nós ROS 2 do solver."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterable, Iterator

import rclpy
from cg_interfaces.srv import MoveCmd
from rclpy.client import Client
from rclpy.node import Node

from .grid import Step


@contextmanager
def ros_node(name: str, args=None) -> Iterator[Node]:
    """Inicializa rclpy + Node e garante shutdown limpo."""
    rclpy.init(args=args)
    node = Node(name)
    try:
        yield node
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


def wait_for_service(node: Node, client: Client, name: str, timeout: float = 1.0) -> None:
    while not client.wait_for_service(timeout_sec=timeout):
        node.get_logger().info(f"Aguardando serviço {name}...")


def call_service(node: Node, client: Client, request, timeout_sec: float = 10.0):
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future, timeout_sec=timeout_sec)
    if not future.done():
        raise TimeoutError(f"Timeout ao chamar serviço ({timeout_sec}s)")
    result = future.result()
    if result is None:
        raise RuntimeError("Serviço retornou None")
    return result


def move_robot(
    node: Node,
    move_client: Client,
    direction: str,
    delay: float = 0.0,
) -> MoveCmd.Response:
    req = MoveCmd.Request()
    req.direction = direction
    response = call_service(node, move_client, req)
    if response.success and delay > 0:
        time.sleep(delay)
    return response


def execute_path(
    node: Node,
    move_client: Client,
    path: Iterable[Step],
    delay: float = 0.05,
) -> bool:
    """Envia cada passo do caminho via /move_command."""
    for i, (direction, expected) in enumerate(path, start=1):
        response = move_robot(node, move_client, direction, delay=delay)
        if not response.success:
            node.get_logger().error(f"Movimento {i} falhou: {direction}")
            return False
        robot_pos = tuple(response.robot_pos)
        node.get_logger().info(
            f"{i:3d} | {direction:5s} | robot={robot_pos} expected={expected}"
        )
    return True
