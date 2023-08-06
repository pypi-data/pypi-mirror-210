#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.

>>> test = import_from_filename("./test.py")
>>> test = reload(test)
"""

__version__ = "0.1.0"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["import_from_filename", "reload"]

from importlib.util import spec_from_file_location, module_from_spec
from os.path import basename, splitext
from importlib._bootstrap import _exec
from types import ModuleType


def reload(module: ModuleType) -> ModuleType:
    """
    This function reload a module.
    """

    return _exec(module.__spec__, module)


def import_from_filename(filename: str) -> ModuleType:
    """
    This function returns a module from path/filename.
    """

    spec = spec_from_file_location(splitext(basename(filename))[0], filename)
    module = module_from_spec(spec)
    module.__spec__ = spec
    spec.loader.exec_module(module)

    return module
