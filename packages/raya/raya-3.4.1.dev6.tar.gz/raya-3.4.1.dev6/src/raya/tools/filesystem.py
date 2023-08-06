from raya.logger import create_logger

__logger = create_logger('raya.file_system')


def check_folder_exists(path: str) -> bool:
    pass


def check_file_exists(path: str) -> bool:
    pass


def check_parent_folder_exists(path: str) -> bool:
    pass


def download_file(url: str, folder_path: str, extract: bool = False):
    pass


def open_file(path: str, mode='r', *args, **kwargs):
    pass
