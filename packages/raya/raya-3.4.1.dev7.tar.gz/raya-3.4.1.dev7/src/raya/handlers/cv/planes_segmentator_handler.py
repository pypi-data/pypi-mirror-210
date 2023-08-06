import typing
from rclpy.node import Node
from raya.handlers.cv.segmentator_handler_base import SegmentatorHandlerBase


class PlanesSegmentatorHandler(SegmentatorHandlerBase):

    def __init__(self, node: Node, topic: str, model_id: int, model_info: dict,
                 continues_msg: bool, cli_cmd, cmd_call):
        pass

    async def find_planes(self,
                          planes: list,
                          callback: typing.Callable = None,
                          callback_async: typing.Callable = None,
                          wait: bool = False,
                          timeout: float = 0.0,
                          as_dict: bool = False):
        return

    def cancel_find_planes(self):
        pass

    def get_planes_names(self):
        return
