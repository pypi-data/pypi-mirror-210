import typing
from rclpy.node import Node
from raya.handlers.cv.model_base import CVModelBase


class SegmentatorHandlerBase(CVModelBase):

    def __init__(self, node: Node, topic: str, model_id: int, model_info: dict,
                 continues_msg: bool, cli_cmd, cmd_call):
        self.cli_cmd = cli_cmd

    async def get_segmentations_once(self, as_dict=False, get_timestamp=False):
        pass

    def get_current_segmentations(self, as_dict=False, get_timestamp=False):
        pass

    def set_segmentations_callback(self,
                                   callback: typing.Callable = None,
                                   callback_async: typing.Callable = None,
                                   as_dict: bool = False,
                                   call_without_segmentations: bool = False):
        pass

    def cancel_finds(self):
        pass
