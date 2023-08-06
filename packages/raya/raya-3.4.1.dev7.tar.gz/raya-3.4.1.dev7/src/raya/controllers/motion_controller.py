import typing
from rclpy.node import Node
from raya.controllers.base_controller import BaseController
from raya.enumerations import ANG_UNIT


class MotionController(BaseController):

    def __init__(self, name: str, node: Node, app, extra_info={}):
        pass

    async def set_velocity(self,
                           x_velocity: float,
                           y_velocity: float,
                           angular_velocity: float,
                           duration: float,
                           ang_unit: ANG_UNIT = ANG_UNIT.DEG,
                           callback_feedback: typing.Callable = None,
                           callback_feedback_async: typing.Callable = None,
                           callback_finish: typing.Callable = None,
                           callback_finish_async: typing.Callable = None,
                           wait: bool = False):
        return

    async def move_linear(self,
                          distance: float,
                          x_velocity: float,
                          y_velocity: float = 0.0,
                          callback_feedback: typing.Callable = None,
                          callback_feedback_async: typing.Callable = None,
                          callback_finish: typing.Callable = None,
                          callback_finish_async: typing.Callable = None,
                          wait: bool = False):
        return

    async def rotate(self,
                     angle: float,
                     angular_speed: float,
                     ang_unit: ANG_UNIT = ANG_UNIT.DEG,
                     callback_feedback: typing.Callable = None,
                     callback_feedback_async: typing.Callable = None,
                     callback_finish: typing.Callable = None,
                     callback_finish_async: typing.Callable = None,
                     wait: bool = False):
        return

    async def await_until_stop(self):
        pass

    async def cancel_motion(self):
        pass

    def is_moving(self):
        return
