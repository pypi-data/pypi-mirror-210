from rclpy.node import Node
from raya.controllers.base_controller import BaseController


class CommunicationController(BaseController):

    def __init__(self, name: str, node: Node, interface, extra_info):
        pass

    def create_incoming_msg_listener(self, callback: callable):
        pass

    async def send_msg(self, message: dict) -> None:
        pass

    async def is_robot_busy(self) -> bool:
        return
