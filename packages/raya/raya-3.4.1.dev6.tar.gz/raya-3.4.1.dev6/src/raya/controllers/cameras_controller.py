import typing
from rclpy.node import Node
from raya.controllers.base_controller import BaseController


class CamerasController(BaseController):

    def __init__(self, name: str, node: Node, app, extra_info: dict):
        pass

    def available_color_cameras(self):
        return

    async def enable_color_camera(self, camera_name: str):
        pass

    async def disable_color_camera(self, camera_name: str):
        pass

    async def get_next_frame(self,
                             camera_name: str,
                             compressed: bool = False,
                             get_timestamp: bool = False,
                             timeout: float = (-1.0)):
        pass

    def create_color_frame_listener(self,
                                    camera_name: str,
                                    callback: typing.Callable = None,
                                    callback_async: typing.Callable = None,
                                    compressed: bool = False):
        pass

    def delete_listener(self, camera_name: str):
        pass

    async def enable_streaming(self, camera_name: str):
        return

    async def disable_streaming(self, camera_name: str):
        return
