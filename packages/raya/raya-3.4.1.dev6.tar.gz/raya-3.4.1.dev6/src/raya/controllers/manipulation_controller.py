import string
import typing
from rclpy.node import Node
from raya.controllers.base_controller import BaseController


class ManipulationController(BaseController):

    def __init__(self, name: str, node: Node, app, extra_info={}):
        pass

    async def pick_object(self,
                          detector_model: string,
                          object_name: string,
                          source: string,
                          pressure: float = 0.5,
                          arms: list = [],
                          timeout: float = 10.0,
                          method: str = '',
                          options: dict = {},
                          callback_feedback: typing.Callable = None,
                          callback_feedback_async: typing.Callable = None,
                          callback_finish: typing.Callable = None,
                          callback_finish_async: typing.Callable = None,
                          wait: bool = False):
        return

    async def pick_object_point(
            self,
            point: list,
            object_height: float,
            pick_height: float,
            width: float,
            angles: list = [],
            arms: list = [],
            pressure: float = 0.5,
            method: str = '',
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait: bool = False):
        return

    async def place_object_with_reference(
            self,
            detector_model: str,
            source: str,
            object_name: str,
            distance: float,
            arm: str,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait: bool = False):
        return

    async def place_object_with_point(
            self,
            point_to_place: list,
            arm: str,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait: bool = False):
        return

    async def place_object_with_tag(
            self,
            tag_family: str,
            tag_id: int,
            tag_size: float,
            source: str,
            arm: str,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait: bool = False):
        return

    async def clean_arms_status(self, arms: list = []):
        pass

    async def wait_manipulation_finished(self):
        pass

    async def cancel_manipulation(self):
        pass

    def is_manipulation(self):
        return
