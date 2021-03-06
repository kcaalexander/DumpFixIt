# -*- coding: utf-8 -*-
#===============================================================================
#
#    Copyright (C) 2015-16 Alexander Thomas <alexander@collab.net>
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


__all__ = ["DumpFixItError", "DumpFileNotFoundError",
           "DumpFilenameMissingError"] 


class Error(Exception):
    """Base class for DumpFixIt exceptions."""

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


class DumpFixItError(Error):
    """Raised when for generic error."""
    def __init__(self, err):
        if isinstance(err, Exception):
            Error.__init__(self, "(%s) %s" %(
                                 err.__class__.__name__,
                                 err.message))
        elif isinstance(err, str):
            Error.__init__(self, err)
        else:
            Error.__init__(self, "Unknown error while executing.")


class DumpFileunrecognisableError(Error):
    """Raised when Dump file in not a valid svn dump file."""
    def __init__(self, fname):
        Error.__init__(self, "Dump file '%s' invalid/unrecognisable." % fname)


class DumpFileUnsupportedFormatError(Error):
    """Raised when Dump file format version is not supported."""
    def __init__(self, version):
        Error.__init__(self, "Unsupported dump file format '%s'." % version)


class DumpFileNotFoundError(Error):
    """Raised when Dump File not found."""
    def __init__(self, fname):
        Error.__init__(self, "Dump file '%s' not found." % fname)


class DumpFilenameMissingError(Error):
    """Raised when Dump Filename is missing or not provided."""
    def __init__(self):
        Error.__init__(self, "Missing Dump filename.")
