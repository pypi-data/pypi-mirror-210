import typing
from rclpy.node import Node
from raya.enumerations import POS_UNIT, ANG_UNIT
from raya.controllers.base_controller import BaseController


class NavigationController(BaseController):

    def __init__(self, name: str, node: Node, interface, extra_info={}):
        pass

    async def is_localized(self):
        return

    async def is_mapping(self):
        return

    async def get_current_map(self):
        return

    async def update_current_nav_goal(self, x, y, yaw):
        pass

    async def get_map(self, map_name: str = ''):
        return

    async def get_costmap(self):
        return

    async def check_path_to_goal(self, x: float, y: float,
                                 in_map_coordinates: bool):
        return

    async def get_list_of_maps(self):
        return

    async def get_status(self):
        return

    async def start_mapping(self, options: object = {}, map_name: str = ''):
        pass

    async def stop_mapping(self, options: object = {}, save_map: bool = True):
        pass

    async def save_location(self,
                            location_name: str,
                            x: float,
                            y: float,
                            angle: float,
                            map_name: str = '',
                            current_pose: bool = False,
                            pos_unit: POS_UNIT = POS_UNIT.PIXEL,
                            ang_unit: ANG_UNIT = ANG_UNIT.DEG):
        pass

    async def delete_location(self, location_name: str, map_name: str = ''):
        pass

    async def get_location(self,
                           location_name: str,
                           map_name: str = '',
                           pos_unit: POS_UNIT = POS_UNIT.PIXEL):
        return

    async def get_locations_list(self, map_name: str = ''):
        return

    async def get_locations(self, map_name: str = ''):
        return

    async def get_zones(self, map_name: str = ''):
        return

    async def get_zones_list(self, map_name: str = ''):
        return

    async def get_zone_center(self,
                              zone_name: str,
                              pos_unit: POS_UNIT = POS_UNIT.PIXEL):
        return

    async def is_in_zone(self, zone_name: str = ''):
        return

    async def delete_zone(self, location_name: str, map_name: str = ''):
        pass

    async def get_position(self,
                           pos_unit: POS_UNIT = POS_UNIT.PIXEL,
                           ang_unit: ANG_UNIT = ANG_UNIT.DEG):
        return

    async def order_zone_points(self,
                                zone_name: str,
                                from_current_pose: bool = False):
        return

    async def get_sorted_zone_point(self, pos_unit: POS_UNIT = POS_UNIT.PIXEL):
        return

    async def set_map(self,
                      map_name: str,
                      wait_localization: bool = False,
                      timeout: float = 0.0,
                      callback_feedback: typing.Callable = None,
                      callback_feedback_async: typing.Callable = None,
                      callback_finish: typing.Callable = None,
                      callback_finish_async: typing.Callable = None,
                      wait: bool = False,
                      options: object = {}):
        pass

    async def download_map(self, map_name: str, path: str):
        pass

    async def update_map(self, map_name: str, path: str):
        pass

    def get_last_navigation_error(self):
        return

    async def navigate_to_position(
        self,
        x: float,
        y: float,
        angle: float,
        pos_unit: POS_UNIT = POS_UNIT.PIXEL,
        ang_unit: ANG_UNIT = ANG_UNIT.DEG,
        callback_feedback: typing.Callable = None,
        callback_feedback_async: typing.Callable = None,
        callback_finish: typing.Callable = None,
        callback_finish_async: typing.Callable = None,
        wait: bool = False,
        xy_tolerance: float = float('nan'),
        yaw_tolerance: float = float('nan')):
        return

    async def navigate_to_location(
        self,
        location_name: str,
        callback_feedback: typing.Callable = None,
        callback_feedback_async: typing.Callable = None,
        callback_finish: typing.Callable = None,
        callback_finish_async: typing.Callable = None,
        wait: bool = False,
        xy_tolerance: float = float('nan'),
        yaw_tolerance: float = float('nan')):
        return

    async def navigate_to_zone(self,
                               zone_name: str,
                               to_center: bool = True,
                               callback_feedback: typing.Callable = None,
                               callback_feedback_async: typing.Callable = None,
                               callback_finish: typing.Callable = None,
                               callback_finish_async: typing.Callable = None,
                               wait: bool = False,
                               xy_tolerance: float = float('nan'),
                               yaw_tolerance: float = float('nan')):
        return

    async def go_to_angle(self,
                          angle_target: float,
                          angular_velocity: float,
                          ang_unit: ANG_UNIT = ANG_UNIT.DEG,
                          callback_feedback: typing.Callable = None,
                          callback_feedback_async: typing.Callable = None,
                          callback_finish: typing.Callable = None,
                          callback_finish_async: typing.Callable = None,
                          wait=False):
        return

    async def navigate_close_to_position(
            self,
            x: float,
            y: float,
            min_radius: float = 0.0,
            max_radius: float = 0.8,
            pos_unit: POS_UNIT = POS_UNIT.PIXEL,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait=False):
        return

    async def await_until_stop(self):
        pass

    async def cancel_navigation(self):
        pass

    def is_navigating(self):
        return

    async def save_zone(self,
                        zone_name: str,
                        points: list,
                        map_name: str,
                        pos_unit: POS_UNIT = POS_UNIT.PIXEL,
                        callback_feedback: typing.Callable = None,
                        callback_feedback_async: typing.Callable = None,
                        callback_finish: typing.Callable = None,
                        callback_finish_async: typing.Callable = None,
                        wait=False):
        return

    async def update_robot_footprint(self, points: list):
        pass

    async def enable_speed_zones(self):
        pass

    async def disable_speed_zones(self):
        pass

    async def generate_speed_zones_files(self, map_name):
        pass
