from raya.exceptions import *
from raya.controllers.base_pseudo_controller import BasePseudoController
from raya.enumerations import *
from raya.constants import *


class FleetController(BasePseudoController):

    def __init__(self, name: str, interface):
        pass

    async def request_action(self,
                             title,
                             message,
                             timeout: float = 30.0,
                             task_id=None):
        pass

    async def finish_task(self,
                          result: FINISH_STATUS = None,
                          message: str = None,
                          task_id=None):
        return

    async def update_app_status(self,
                                task_id: int = None,
                                status: UPDATE_STATUS = None,
                                message: str = None):
        return

    async def get_path(self, x: float, y: float, origin: str = None):
        return

    async def can_navigate(self,
                           x: float,
                           y: float,
                           origin: str = None,
                           wait: bool = False,
                           callback: callable = None):
        pass

    def register_fleet_msgs_listener(self, callback: callable):
        pass

    async def get_status(self):
        return
