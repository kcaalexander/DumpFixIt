#===============================================================================
#
#    Copyright (C) 2015 Alexander Thomas <alexander@collab.net>
#
#    This file is part of SVNDumpFixit!
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#===============================================================================

__all__ = ["CommandProvider", "Singleton"]

import re
import error

def Singleton(cls):
    _instances_ = {}

    def CreateInstance(*args, **kwargs):
        if cls not in _instances_:
           _instances_[cls] = cls(*args, **kwargs)

        return _instances_[cls]

    return CreateInstance


class CommandProvider(object):
    cmd = None
    arg_list = None

    def __new__(cls, *args):
        if len(args) <= 0: # No args to parse.
            return None

        return super(CommandProvider, cls).__new__(cls)

    def __init__(self, *args):
        if re.match("[A-Za-z][_A-Za-z0-9]*$", args[0]) is None:
            self.cmd = "help"
        else:
            self.cmd = args[0].lower()

        if len(args) > 1:
            self.arg_list = args[1:]

    def execute(self, cls):
        cls()
        pass
