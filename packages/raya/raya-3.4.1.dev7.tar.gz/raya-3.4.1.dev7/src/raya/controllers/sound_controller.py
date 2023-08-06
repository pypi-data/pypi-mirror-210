import typing
import pasimple
from typing import List, Any
from rclpy.node import Node
from raya.controllers.base_controller import BaseController

SIZE = 20


class SoundController(BaseController):

    def __init__(self, name: str, node: Node, interface, extra_info):
        self.FORMAT = pasimple.PA_SAMPLE_S16LE
        self.SAMPLE_WIDTH = pasimple.format2width(self.FORMAT)
        self.CHANNELS = 1
        self.SAMPLE_RATE = 8000
        self.MAX_DURATION_DATA = 60
        self.MAX_SIZE_DATA = (self.SAMPLE_RATE * self.MAX_DURATION_DATA)

    async def play_sound_from_file(self,
                                   filepath: str,
                                   volume: int = 100,
                                   callback_feedback=None,
                                   callback_finish=None,
                                   wait=True) -> None:
        return

    async def play_sound_from_data(self,
                                   audio_raw,
                                   volume: int = 100,
                                   callback_feedback=None,
                                   callback_finish=None,
                                   wait=True) -> None:
        return

    async def play_predefined_sound(self,
                                    sound_name: str,
                                    volume: int = 100,
                                    callback_feedback=None,
                                    callback_finish=None,
                                    wait=True) -> None:
        return

    def get_predefined_sounds(self) -> List[str]:
        return

    async def record_sound(self,
                           duration: float = 60.0,
                           path: str = '',
                           callback_finish: typing.Callable = None,
                           callback_finish_async: typing.Callable = None,
                           wait: bool = True) -> Any:
        return

    def is_playing(self):
        return

    def is_recording(self):
        return

    async def play_sound(self,
                         name: str = None,
                         path: str = None,
                         data: list = None,
                         volume: int = 100,
                         callback_finish: typing.Callable = None,
                         callback_finish_async: typing.Callable = None,
                         callback_feedback: typing.Callable = None,
                         callback_feedback_async: typing.Callable = None,
                         wait: bool = True) -> None:
        pass
