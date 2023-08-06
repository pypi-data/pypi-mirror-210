import typing
from raya.controllers.base_controller import BaseController
from rclpy.node import Node


class SkillsController(BaseController):

    def __init__(self, name: str, node: Node, app, extra_info={}):
        pass

    def get_available_skills(self) -> typing.List[str]:
        return

    def get_skill_info(self, skill_name: str):
        return

    async def run_skill(self,
                        skill_name: str,
                        callback_finish: typing.Callable = None,
                        callback_finish_async: typing.Callable = None,
                        callback_feedback: typing.Callable = None,
                        callback_feedback_async: typing.Callable = None,
                        wait: bool = False,
                        **kwargs) -> None:
        pass
