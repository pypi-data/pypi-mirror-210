import typing
from xmlrpc.client import boolean
from rclpy.node import Node
from raya.controllers.base_controller import BaseController


class InteractionsController(BaseController):

    def __init__(self, name: str, node: Node, app, extra_info):
        pass

    def get_interactions(self) -> typing.List[str]:
        return

    async def play_interaction(self,
                               interaction_name: str,
                               callback_feedback: typing.Callable = None,
                               callback_feedback_async: typing.Callable = None,
                               callback_finish: typing.Callable = None,
                               callback_finish_async: typing.Callable = None,
                               wait=False) -> None:
        return

    def interaction_running(self) -> boolean:
        return

    async def wait_interaction_finished(self) -> None:
        pass
