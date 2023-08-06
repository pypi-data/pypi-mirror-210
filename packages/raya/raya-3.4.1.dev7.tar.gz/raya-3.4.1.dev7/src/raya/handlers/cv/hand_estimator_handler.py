from rclpy.node import Node
from raya.handlers.cv.estimator_handler_base import EstimatorHandlerBase


class HandEstimatorHandler(EstimatorHandlerBase):

    def __init__(self, node: Node, topic: str, model_id: int, model_info: dict,
                 continues_msg: bool, cli_cmd, cmd_call):
        pass
