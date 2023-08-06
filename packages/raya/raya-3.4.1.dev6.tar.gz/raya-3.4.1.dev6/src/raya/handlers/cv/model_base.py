from rclpy.node import Node


class CVModelBase():

    def __init__(self, node: Node, topic: str, model_id: int,
                 model_info: dict):
        self.model_id = model_id
