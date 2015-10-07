#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#
#    Copyright (C) 2015 Alexander Thomas <alexander@collab.net>
#
#    This file is part of DumpFixit!
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
import sys
import os
import getopt
import string
import sys
import os
import glob
import time
import re
import importlib

from dumpfixit.extension import ExtensionProvider
from dumpfixit.core import CommandProvider
from dumpfixit import version
from dumpfixit import core
from dumpfixit import usage


def main(*args):
    """ Mother of all beginings. """
    command = CommandProvider(*args)
    if command.cmd == "version":
        command.execute(ExtensionProvider.registry['version'])
    elif command.cmd == "help":
        command.execute(ExtensionProvider.registry['usage'])
    else:
        pass


if __name__ == "__main__":
    try:
        _getopt = getopt.gnu_getopt
    except AttributeError:
        _getopt = getopt.getopt

    sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]),
                                                    'dumpfixit'))
    main(*sys.argv[1:])

