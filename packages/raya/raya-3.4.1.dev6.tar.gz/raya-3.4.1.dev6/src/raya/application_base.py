import pathlib
from typing import Union
from raya.exceptions import *
from raya.logger import create_logger
from raya.controllers.analytics_controller import AnalyticsController
from raya.controllers.arms_controller import ArmsController
from raya.controllers.cameras_controller import CamerasController
from raya.controllers.communication_controller import CommunicationController
from raya.controllers.cv_controller import CVController
from raya.controllers.fleet_controller import FleetController
from raya.controllers.manipulation_controller import ManipulationController
from raya.controllers.interactions_controller import InteractionsController
from raya.controllers.leds_controller import LedsController
from raya.controllers.lidar_controller import LidarController
from raya.controllers.motion_controller import MotionController
from raya.controllers.navigation_controller import NavigationController
from raya.controllers.sensors_controller import SensorsController
from raya.controllers.skills_controller import SkillsController
from raya.controllers.sound_controller import SoundController
from raya.controllers.ui_controller import UIController

list_type = list
type_func = type
except_no_print_bases = [pathlib.Path(__file__).parent.resolve()]
DEPRECATED_CONTROLLER_NAMES = {'grasping': 'manipulation'}


class RayaApplicationBase():

    def __init__(self, exec_settings):
        self.log = create_logger(f'RayaApp.app.{self.__app_id}')

    @__only_in_args_getting('get_argument')
    def get_argument(self,
                     *name_or_flags: str,
                     type=str,
                     required: bool = False,
                     help: str = None,
                     default=None,
                     list: bool = False,
                     **kwargs):
        return

    @__only_in_args_getting('get_flag_argument')
    def get_flag_argument(self, *name_or_flags: str, help: str = None):
        return

    @__only_in_setup('Create Logger')
    def create_logger(self, name):
        return

    def create_task(self, name, afunc, *args, **kargs):
        pass

    def is_task_running(self, name):
        return

    def is_task_done(self, name):
        return

    def cancel_task(self, name):
        pass

    def pop_task_return(self, name):
        return

    async def wait_for_task(self, name):
        pass

    async def sleep(self, sleep_time: float):
        pass

    def create_timer(self, name: str, timeout: float):
        pass

    def is_timer_done(self, name: str) -> bool:
        return

    def is_timer_running(self, name: str) -> bool:
        return

    @__only_in_setup('enable_controller')
    async def enable_controller(
        self, ctlr_name: str
    ) -> Union[
        (AnalyticsController, ArmsController, CamerasController,
         CommunicationController, CVController, FleetController,
         ManipulationController, InteractionsController, LedsController,
         LidarController, MotionController, NavigationController,
         SensorsController, SkillsController, SoundController, UIController)]:
        return

    def finish_app(self):
        pass

    def abort_app(self):
        pass
