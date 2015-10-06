# -*- coding: utf-8 -*-
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


__all__ = []


class Error(Exception):
    """Base class for SvnDumpFixIt exceptions."""

    @property
    def errmsg(self):
        """Getter function for error message."""
        return self._errmsg

    @errmsg.setter
    def errmsg(self, msg):
        """Setter function for error message."""
        self.__errmsg = msg

    def __init__( self, msg=''):
        self._errmsg = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self._errmsg

    __str__ = __repr__


