import os
import sys
import pathlib
import re
from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py



def get_lib_version():
    VERSIONFILE = 'src/raya/_version.py'
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." %
                           (VERSIONFILE, ))
    return verstr


def get_ext_paths(root_dir, exclude_folders=[]):
    '''get filepaths for compilation'''
    paths = []
    root_directory = Path(root_dir)
    a = root_directory.glob('**/*')
    for path_object in root_directory.glob('**/*'):
        if not path_object.is_file() or not path_object.suffix == '.py':
            continue
        exclude = False
        for exclude_folder in exclude_folders:
            if Path(exclude_folder) in path_object.parents:
                exclude = True
                break
        if not exclude:
            paths.append(str(path_object))
    return paths


class build_py(_build_py):

    def find_package_modules(self, package, package_dir):
        return []


def package_files(src_path, package, directory):
    paths = []
    data_path = os.path.join(src_path, package, directory)
    for (path, directories, filenames) in os.walk(data_path):
        for filename in filenames:
            p = pathlib.Path(os.path.join(path, filename))
            p = pathlib.Path(*p.parts[2:])
            paths.append(str(p))
    return paths


# with open('README.md', 'r', encoding='utf-8') as fh:
#     long_description = fh.read()

setup_args = {
    'name':
    'raya',
    'version':
    get_lib_version(),
    'author':
    'Unlimited Robotics',
    'author_email':
    'camilo@unlimited-robotics.com',
    'description':
    'Unlimited Robotics - Ra-Ya Python Library',
    # 'long_description': long_description,
    'long_description_content_type':
    'text/markdown',
    'url':
    'https://documentation.unlimited-robotics.com/',
    'project_urls': {
        'Bug Tracker': 'https://github.com/pypa/sampleproject/issues',
    },
    'classifiers': [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    'package_dir': {
        '': 'src'
    },
    'packages':
    find_packages(where='src'),
    'package_data': {
        'raya': package_files('./src/', 'raya', 'ros2lib')
    },
    'python_requires':
    '>=3.8',
    # 'install_requires': ['numpy>=1.22', 'PyYAML==6.0', 'opencv-python==4.2.0.32', 'transforms3d'],
}


setup(**setup_args)
