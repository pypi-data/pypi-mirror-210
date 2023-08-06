import typing
from raya.controllers.base_controller import BaseController
from rclpy.node import Node
from raya.enumerations import EXECUTION_CONTROL


class LedsController(BaseController):

    def __init__(self, name: str, node: Node, app, extra_info):
        pass

    def get_groups(self) -> typing.List[str]:
        return

    def get_colors(self, group: str) -> typing.List[str]:
        pass

    def get_animations(self, group: str) -> typing.List[str]:
        pass

    def get_max_speed(self, group: str) -> typing.List[str]:
        pass

    async def animation(
            self,
            group: str,
            color: str,
            animation: str,
            speed: int = 1,
            repetitions: int = 1,
            execution_control: EXECUTION_CONTROL = EXECUTION_CONTROL.OVERRIDE,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait=True) -> None:
        return

    async def set_color(self, group: str, color: str) -> None:
        return

    async def turn_off_group(self, group: str) -> None:
        return

    async def turn_off_all(self) -> None:
        return
