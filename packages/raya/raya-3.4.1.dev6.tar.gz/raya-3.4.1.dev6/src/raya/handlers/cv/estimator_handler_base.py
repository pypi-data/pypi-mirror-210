import typing
from rclpy.node import Node
from raya.handlers.cv.model_base import CVModelBase


class EstimatorHandlerBase(CVModelBase):

    def __init__(self, node: Node, topic: str, model_id: int, model_info: dict,
                 continues_msg: bool, cli_cmd, cmd_call):
        pass

    def get_current_estimations(self, as_dict=False, get_timestamp=False):
        pass

    def set_estimations_callback(self,
                                 callback: typing.Callable = None,
                                 callback_async: typing.Callable = None,
                                 as_dict: bool = False,
                                 call_without_estimations: bool = False):
        pass

    def cancel_finds(self):
        pass
