from enum import Enum
from typing import List, Dict
from raya.controllers.base_pseudo_controller import BasePseudoController
from raya.constants import *
from raya.exceptions import *
from raya.enumerations import *


class UIController(BasePseudoController):

    def __init__(self, name: str, interface):
        pass

    async def display_split_screen(self,
                                   title: str = None,
                                   title_size: TITLE_SIZE = TITLE_SIZE.MEDIUM,
                                   first_component_type: SPLIT_TYPE = None,
                                   first_component_data: dict = None,
                                   second_component_type: SPLIT_TYPE = None,
                                   second_component_data: dict = None,
                                   show_back_button: bool = True,
                                   back_button_text: str = 'Back',
                                   button_size: int = 1,
                                   languages: list = None,
                                   chosen_language: str = None,
                                   theme: THEME_TYPE = THEME_TYPE.DARK,
                                   custom_style: dict = None,
                                   wait: bool = False):
        return

    async def display_modal(self,
                            title: str = None,
                            title_size: TITLE_SIZE = TITLE_SIZE.MEDIUM,
                            subtitle: str = None,
                            content: str = None,
                            modal_type: MODAL_TYPE = MODAL_TYPE.INFO,
                            modal_size: MODAL_SIZE = MODAL_SIZE.NORMAL,
                            submit_text: str = 'Yes',
                            cancel_text: str = 'No',
                            show_icon: bool = True,
                            button_size: int = 1,
                            theme: THEME_TYPE = THEME_TYPE.DARK,
                            custom_style: dict = None,
                            wait: bool = True,
                            callback: callable = None) -> Enum:
        pass

    async def display_input_modal(self,
                                  title: str = None,
                                  title_size: TITLE_SIZE = TITLE_SIZE.MEDIUM,
                                  subtitle: str = None,
                                  submit_text: str = 'OK',
                                  cancel_text: str = 'Cancel',
                                  placeholder: str = None,
                                  input_type: INPUT_TYPE = INPUT_TYPE.TEXT,
                                  show_back_button: bool = False,
                                  back_button_text: str = 'Back',
                                  button_size: int = 1,
                                  languages: list = None,
                                  chosen_language=None,
                                  theme: THEME_TYPE = THEME_TYPE.DARK,
                                  custom_style: dict = None,
                                  wait: bool = True,
                                  callback: callable = None) -> Enum:
        pass

    async def display_screen(self,
                             title: str = None,
                             title_size: TITLE_SIZE = TITLE_SIZE.MEDIUM,
                             subtitle: str = None,
                             show_loader: bool = True,
                             show_back_button: bool = True,
                             back_button_text: str = 'Back',
                             button_size: int = 1,
                             languages: list = None,
                             chosen_language=None,
                             theme: THEME_TYPE = THEME_TYPE.DARK,
                             custom_style: dict = None) -> Enum:
        return

    async def display_interactive_map(
            self,
            title: str = None,
            title_size: TITLE_SIZE = TITLE_SIZE.MEDIUM,
            subtitle: str = None,
            map_name: str = None,
            show_robot_position: bool = True,
            view_only: bool = False,
            show_back_button: bool = True,
            back_button_text: str = 'Back',
            button_size: int = 1,
            languages: list = None,
            chosen_language=None,
            theme: THEME_TYPE = THEME_TYPE.DARK,
            custom_style: dict = None,
            wait: bool = True,
            callback: callable = None) -> Enum:
        pass

    async def display_action_screen(self,
                                    title: str = None,
                                    title_size: TITLE_SIZE = TITLE_SIZE.MEDIUM,
                                    subtitle: str = None,
                                    button_text: str = None,
                                    show_back_button: bool = True,
                                    back_button_text: str = 'Back',
                                    button_size: str = None,
                                    languages: list = None,
                                    chosen_language=None,
                                    theme: THEME_TYPE = THEME_TYPE.DARK,
                                    custom_style: dict = None,
                                    wait: bool = True,
                                    callback: callable = None) -> Enum:
        pass

    async def display_choice_selector(
            self,
            data: List[Dict],
            max_items_shown: int = None,
            title: str = None,
            title_size: TITLE_SIZE = TITLE_SIZE.MEDIUM,
            scroll_arrow_buttom_text: str = None,
            scroll_arrow_upper_text: str = None,
            show_back_button: bool = True,
            back_button_text: str = 'Back',
            button_size: int = 1,
            languages: list = None,
            chosen_language=None,
            theme: THEME_TYPE = THEME_TYPE.DARK,
            custom_style: dict = None,
            wait: bool = True,
            callback: callable = None) -> Enum:
        pass

    async def display_animation(self,
                                title: str = None,
                                title_size: TITLE_SIZE = TITLE_SIZE.MEDIUM,
                                subtitle: str = None,
                                content=None,
                                format: ANIMATION_TYPE = None,
                                show_loader: bool = False,
                                show_back_button: bool = True,
                                back_button_text: str = 'Back',
                                button_size: int = 1,
                                languages: list = None,
                                chosen_language: str = None,
                                theme: THEME_TYPE = THEME_TYPE.DARK,
                                custom_style: dict = None) -> Enum:
        return

    async def open_link(self,
                        url: str,
                        title: str = None,
                        title_size: TITLE_SIZE = TITLE_SIZE.MEDIUM,
                        show_back_button: bool = True,
                        back_button_text: str = 'Back',
                        button_size: int = 1,
                        languages: list = None,
                        chosen_language=None,
                        theme: THEME_TYPE = THEME_TYPE.DARK,
                        custom_style: dict = None,
                        wait: bool = True,
                        callback: callable = None) -> Enum:
        pass

    async def open_conference(self,
                              title: str = None,
                              title_size: TITLE_SIZE = TITLE_SIZE.MEDIUM,
                              subtitle: str = None,
                              client: str = None,
                              call_on_join: bool = False,
                              button_text: str = 'Make a Call',
                              loading_subtitle: str = 'Loading ...',
                              show_back_button: bool = True,
                              back_button_text: str = 'Back',
                              button_size: int = 1,
                              languages: list = None,
                              theme: THEME_TYPE = THEME_TYPE.DARK,
                              chosen_language=None,
                              custom_style: dict = None,
                              wait: bool = True,
                              callback: callable = None) -> Enum:
        pass
