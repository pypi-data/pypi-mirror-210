from rclpy.node import Node
from raya.enumerations import ANG_UNIT
from raya.controllers.base_controller import BaseController


class LidarController(BaseController):

    def __init__(self, name: str, node: Node, interface, extra_info):
        pass

    def get_laser_info(self, ang_unit: ANG_UNIT = ANG_UNIT.DEG) -> dict:
        return

    def get_raw_data(self):
        return

    def check_obstacle(self,
                       lower_angle: float,
                       upper_angle: float,
                       lower_distance: float = 0.0,
                       upper_distance: float = float('inf'),
                       ang_unit: ANG_UNIT = ANG_UNIT.DEG) -> bool:
        return

    def create_obstacle_listener(self,
                                 listener_name: str,
                                 callback: callable,
                                 lower_angle: float,
                                 upper_angle: float,
                                 lower_distance: float = 0.0,
                                 upper_distance: float = float('inf'),
                                 ang_unit: ANG_UNIT = ANG_UNIT.DEG) -> None:
        pass
