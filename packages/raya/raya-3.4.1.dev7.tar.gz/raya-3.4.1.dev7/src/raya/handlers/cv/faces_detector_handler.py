from rclpy.node import Node
from raya.handlers.cv.detector_handler_base import DetectorHandlerBase


class FacesDetectorHandler(DetectorHandlerBase):

    def __init__(self, node: Node, topic: str, model_id: int, model_info: dict,
                 continues_msg: bool, cli_cmd, cmd_call):
        pass
