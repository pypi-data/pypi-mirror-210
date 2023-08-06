from rclpy.node import Node
import typing
from raya.controllers.base_controller import BaseController
from raya.enumerations import ANG_UNIT, MANAGE_ACTIONS


class ArmsController(BaseController):

    def __init__(self, name: str, node: Node, app, extra_info={}):
        pass

    def get_list_of_arms(self):
        return

    def get_state_of_arm(self, arm: str):
        return

    def get_limits_of_joints(self, arm: str, units: ANG_UNIT = ANG_UNIT.DEG):
        return

    async def is_any_arm_in_execution(self):
        return

    def are_checkings_in_progress(self):
        return

    async def cancel_execution(self):
        pass

    async def gripper_cmd(self,
                          arm: str,
                          desired_position: float,
                          desired_pressure: float = 0.8,
                          timeout: float = 10.0,
                          callback_finish: typing.Callable = None,
                          callback_finish_async: typing.Callable = None,
                          callback_feedback: typing.Callable = None,
                          callback_feedback_async: typing.Callable = None,
                          wait: bool = False):
        return

    async def execute_joint_values_array(
            self,
            arm: str,
            joint_values: list,
            units: ANG_UNIT = ANG_UNIT.DEG,
            tilt_constraint: bool = False,
            use_obstacles: bool = False,
            cameras: list = [],
            update_obstacles: bool = False,
            save_trajectory: bool = False,
            name_trajectory: str = '',
            velocity_scaling: float = 0.0,
            acceleration_scaling: float = 0.0,
            min_bbox_clear_obstacles: list = [],
            max_bbox_clear_obstacles: list = [],
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait=False):
        return

    async def execute_pose_array(
            self,
            arm: str,
            poses: list,
            units: ANG_UNIT = ANG_UNIT.DEG,
            cartesian_path: bool = False,
            tilt_constraint: bool = False,
            use_obstacles: bool = False,
            cameras: list = [],
            update_obstacles: bool = False,
            save_trajectory: bool = False,
            name_trajectory: str = '',
            velocity_scaling: float = 0.0,
            acceleration_scaling: float = 0.0,
            min_bbox_clear_obstacles: list = [],
            max_bbox_clear_obstacles: list = [],
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait=False):
        pass

    async def execute_pose_array_q(
            self,
            arm: str,
            poses: list,
            cartesian_path: bool = False,
            tilt_constraint: bool = False,
            use_obstacles: bool = False,
            cameras: list = [],
            update_obstacles: bool = False,
            min_bbox_clear_obstacles: list = [],
            max_bbox_clear_obstacles: list = [],
            save_trajectory: bool = False,
            name_trajectory: str = '',
            velocity_scaling: float = 0.0,
            acceleration_scaling: float = 0.0,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait=False):
        return

    async def execute_predefined_pose_array(
            self,
            arm: str,
            predefined_poses: list,
            tilt_constraint: bool = False,
            use_obstacles: bool = False,
            cameras: list = [],
            update_obstacles: bool = False,
            min_bbox_clear_obstacles: list = [],
            max_bbox_clear_obstacles: list = [],
            save_trajectory: bool = False,
            name_trajectory: str = '',
            velocity_scaling: float = 0.0,
            acceleration_scaling: float = 0.0,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait=False):
        return

    async def execute_predefined_trajectory(
            self,
            predefined_trajectory: str,
            reverse_execution: bool = False,
            use_obstacles: bool = False,
            cameras: list = [],
            update_obstacles: bool = False,
            min_bbox_clear_obstacles: list = [],
            max_bbox_clear_obstacles: list = [],
            additional_options: dict = {},
            velocity_scaling: float = 0.0,
            acceleration_scaling: float = 0.0,
            wait: bool = False,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None):
        return

    async def set_pose(self,
                       arm: str,
                       x: float,
                       y: float,
                       z: float,
                       roll: float,
                       pitch: float,
                       yaw: float,
                       units: ANG_UNIT = ANG_UNIT.DEG,
                       cartesian_path: bool = False,
                       tilt_constraint: bool = False,
                       use_obstacles: bool = False,
                       cameras: list = [],
                       update_obstacles: bool = False,
                       min_bbox_clear_obstacles: list = [],
                       max_bbox_clear_obstacles: list = [],
                       save_trajectory: bool = False,
                       name_trajectory: str = '',
                       velocity_scaling: float = 0.0,
                       acceleration_scaling: float = 0.0,
                       callback_feedback: typing.Callable = None,
                       callback_feedback_async: typing.Callable = None,
                       callback_finish: typing.Callable = None,
                       callback_finish_async: typing.Callable = None,
                       wait: bool = False):
        return

    async def set_pose_q(self,
                         arm: str,
                         x: float,
                         y: float,
                         z: float,
                         qx: float,
                         qy: float,
                         qz: float,
                         qw: float,
                         cartesian_path: bool = False,
                         tilt_constraint: bool = False,
                         use_obstacles: bool = False,
                         cameras: list = [],
                         update_obstacles: bool = False,
                         min_bbox_clear_obstacles: list = [],
                         max_bbox_clear_obstacles: list = [],
                         save_trajectory: bool = False,
                         name_trajectory: str = '',
                         velocity_scaling: float = 0.0,
                         acceleration_scaling: float = 0.0,
                         callback_feedback: typing.Callable = None,
                         callback_feedback_async: typing.Callable = None,
                         callback_finish: typing.Callable = None,
                         callback_finish_async: typing.Callable = None,
                         wait: bool = False):
        return

    async def set_multi_arms_pose(
            self,
            group: str,
            arms: list,
            goal_poses: list,
            cartesian_path: bool = False,
            tilt_constraint: bool = False,
            use_obstacles: bool = False,
            cameras: list = [],
            update_obstacles: bool = False,
            min_bbox_clear_obstacles: list = [],
            max_bbox_clear_obstacles: list = [],
            save_trajectory: bool = False,
            name_trajectory: str = '',
            velocity_scaling: float = 0.0,
            acceleration_scaling: float = 0.0,
            units: ANG_UNIT = ANG_UNIT.DEG,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait: bool = False):
        return

    async def set_predefined_pose(
            self,
            arm: str,
            predefined_pose: str,
            tilt_constraint: bool = False,
            use_obstacles: bool = False,
            cameras: list = [],
            update_obstacles: bool = False,
            min_bbox_clear_obstacles: list = [],
            max_bbox_clear_obstacles: list = [],
            save_trajectory: bool = False,
            name_trajectory: str = '',
            velocity_scaling: float = 0.0,
            acceleration_scaling: float = 0.0,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait: bool = False):
        return

    async def set_joints_position(
            self,
            arm: str,
            name_joints: list,
            angle_joints: list,
            units: ANG_UNIT = ANG_UNIT.DEG,
            tilt_constraint: bool = False,
            use_obstacles: bool = False,
            cameras: list = [],
            update_obstacles: bool = False,
            min_bbox_clear_obstacles: list = [],
            max_bbox_clear_obstacles: list = [],
            save_trajectory: bool = False,
            name_trajectory: str = '',
            velocity_scaling: float = 0.0,
            acceleration_scaling: float = 0.0,
            callback_feedback: typing.Callable = None,
            callback_feedback_async: typing.Callable = None,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait: bool = False):
        return

    def convert_orientation(self,
                            orientation: dict,
                            units: ANG_UNIT = ANG_UNIT.DEG):
        pass

    async def add_collision_object(self,
                                   id: str,
                                   types: list,
                                   dimensions: list,
                                   shapes_poses: list,
                                   units: ANG_UNIT = ANG_UNIT.DEG):
        pass

    async def add_constraints(self,
                              arm: str,
                              joint_constraints: list = [],
                              orientation_constraints: list = [],
                              position_constraints: list = [],
                              units: ANG_UNIT = ANG_UNIT.DEG):
        pass

    async def remove_collision_object(self,
                                      id: str = '',
                                      remove_all_objects: bool = True):
        pass

    async def remove_constraints(self, arm: str = ''):
        pass

    async def add_attached_object(self, arm: str, id: str, types: list,
                                  dimensions: list, shapes_poses: list):
        pass

    async def remove_attached_object(self,
                                     id: str = '',
                                     remove_all_objects: bool = True):
        pass

    async def manage_predefined_pose(
            self,
            arm: str,
            name: str,
            position: list = [],
            action: MANAGE_ACTIONS = MANAGE_ACTIONS.CREATE,
            units: ANG_UNIT = ANG_UNIT.DEG):
        pass

    async def get_current_pose(self, arm: str, units: ANG_UNIT = ANG_UNIT.DEG):
        return

    async def get_current_joint_values(self,
                                       arm: str,
                                       units: ANG_UNIT = ANG_UNIT.DEG):
        return

    async def get_list_predefined_poses(self, arm: str):
        return

    async def get_list_predefined_trajectories(self):
        return

    async def manage_predefined_trajectory(
            self,
            name: str,
            action: MANAGE_ACTIONS = MANAGE_ACTIONS.GET_INFORMATION):
        pass

    async def is_pose_valid(self,
                            arm: str,
                            x: float,
                            y: float,
                            z: float,
                            roll: float,
                            pitch: float,
                            yaw: float,
                            start_x: float = 0.0,
                            start_y: float = 0.0,
                            start_z: float = 0.0,
                            start_roll: float = 0.0,
                            start_pitch: float = 0.0,
                            start_yaw: float = 0.0,
                            start_joints: list = [],
                            name_start_joints: list = [],
                            use_start_pose: bool = False,
                            use_start_joints: bool = False,
                            cartesian_path: bool = False,
                            tilt_constraint: bool = False,
                            units: ANG_UNIT = ANG_UNIT.DEG,
                            use_obstacles: bool = False,
                            cameras: list = [],
                            update_obstacles: bool = False,
                            min_bbox_clear_obstacles: list = [],
                            max_bbox_clear_obstacles: list = [],
                            save_trajectory: bool = False,
                            name_trajectory: str = '',
                            velocity_scaling: float = 0.0,
                            acceleration_scaling: float = 0.0,
                            callback_finish: typing.Callable = None,
                            callback_finish_async: typing.Callable = None,
                            wait: bool = False):
        return

    async def is_pose_valid_q(self,
                              arm: str,
                              x: float,
                              y: float,
                              z: float,
                              qx: float,
                              qy: float,
                              qz: float,
                              qw: float,
                              start_x: float = 0.0,
                              start_y: float = 0.0,
                              start_z: float = 0.0,
                              start_qx: float = 0.0,
                              start_qy: float = 0.0,
                              start_qz: float = 0.0,
                              start_qw: float = 0.0,
                              start_joints: list = [],
                              name_start_joints: list = [],
                              use_start_pose: bool = False,
                              use_start_joints: bool = False,
                              units: ANG_UNIT = ANG_UNIT.DEG,
                              cartesian_path: bool = False,
                              tilt_constraint: bool = False,
                              use_obstacles: bool = False,
                              cameras: list = [],
                              update_obstacles: bool = False,
                              min_bbox_clear_obstacles: list = [],
                              max_bbox_clear_obstacles: list = [],
                              save_trajectory: bool = False,
                              name_trajectory: str = '',
                              velocity_scaling: float = 0.0,
                              acceleration_scaling: float = 0.0,
                              wait: bool = False,
                              callback_finish: typing.Callable = None,
                              callback_finish_async: typing.Callable = None):
        return

    async def are_joints_position_valid(
            self,
            arm: str,
            name_joints: list,
            angle_joints: list,
            units: ANG_UNIT = ANG_UNIT.DEG,
            start_joints: list = [],
            name_start_joints: list = [],
            use_start_joints: bool = False,
            tilt_constraint: bool = False,
            use_obstacles: bool = False,
            cameras: list = [],
            update_obstacles: bool = False,
            min_bbox_clear_obstacles: list = [],
            max_bbox_clear_obstacles: list = [],
            save_trajectory: bool = False,
            name_trajectory: str = '',
            velocity_scaling: float = 0.0,
            acceleration_scaling: float = 0.0,
            callback_finish: typing.Callable = None,
            callback_finish_async: typing.Callable = None,
            wait: bool = False):
        return
