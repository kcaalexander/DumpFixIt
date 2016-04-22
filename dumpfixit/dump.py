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

from core import Singleton
from cache import CacheProvider
import error
from parser import DumpParser
import os.path
import pdb

__all__ = ["DumpProvider"]


@Singleton
class DumpProvider(DumpParser, CacheProvider):

    # is the max version of dump file format support by the DumpProvider.
    SUPPORTED_DUMP_FORMAT_VERSIONS = [1, 2]

    __dump_file__ = None # Absoulte path to dump filename.
    __dump_format__ = None # Dump file format
    __dump_uuid__ = None # Dump UUID

    _dump_fptr = None # File descriptor to open dump file.
    _rm_cache = False # Remove existing cache file.
    _retain_cache = True # In-memory cache, removed at exit.


    def __init__(self, dump_fname = None, rm_cache = False,
                 retain_cache = True):
        if dump_fname is None:
            raise error.DumpFilenameMissingError

        self._rm_cache = rm_cache
        self._retain_cache = retain_cache

        self.__dump_file__ = os.path.abspath(dump_fname)
        if not os.path.exists(self.__dump_file__):
            raise error.DumpFileNotFoundError(self.__dump_file__)

        try:
            self._dump_fptr = open(self.__dump_file__, "rt")
            header = self.get_header()

            if header.has_key(self.DUMP_FORMAT_STR):
               self.__dump_format__ = int(header[self.DUMP_FORMAT_STR])

            if header.has_key(self.UUID_STR):
               self.__dump_uuid__ = str(header[self.UUID_STR])
        except Exception as err:
            raise error.DumpFixItError(err)

        # Declares file not a svn dump file if format version is missing.
        if self.__dump_format__ is None:
            raise error.DumpFileunrecognisableError(dump_fname)
        # Check for support dump formats.
        if self.__dump_format__ not in self.SUPPORTED_DUMP_FORMAT_VERSIONS:
            raise error.DumpFileUnsupportedFormatError(self.__dump_format__)

        CacheProvider.__init__(self, dump_fname, rm_cache, not retain_cache)

    def reader(self, rev=0):

        header = self.get_header()

        # check for exitance/useablity/validation of dmp_fname
        # Read in dump version and uuid
        #
        #pdb.set_trace()
        revision = self.get_revision_iter(rev)
        #node = self._get_node(revision)
        while True:
          try:
             rev = revision.next()
             if rev[0] is None:
                 break;
             else:
                 while True:
                    try:
                       node = rev[4].next()
                    except StopIteration:
                       break;
          except StopIteration:
             break;
        pass


    def writer(self, dump_fname = None, dump_ver = 2, dump_uuid = None):
        pass
