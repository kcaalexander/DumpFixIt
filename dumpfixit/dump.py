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

from core import Singleton
from cache import CacheProvider
import error
import parser
import os.path
import pdb

__all__ = ["DumpProvider"]



@Singleton
class DumpProvider(object):

    __dump_file__ = None # Absoulte path to dump filename.
    __dump_format__ = None # Dump file format
    __dump_uuid__ = None # Dump UUID

    _dump_fptr = None # File descriptor to open dump file.
    _rm_cache = False # Remove existing cache file.
    _retain_cache = True # In-memory cache, removed at exit.


    def __init__(self, dump_fname = None, rm_cache = False,
                 retain_cache = True):
        if dump_fname is None:
            raise DumpFilenameMissingError

        self._rm_cache = rm_cache
        self._retain_cache = retain_cache

        self.__dump_file__ = os.path.abspath(dump_fname)
        if not os.path.exists(self.__dump_file__):
            raise DumpFileNotFoundError(self.__dump_file__)

        try:
            self._dump_fptr = open(self.__dump_file__, "rt")
            header = parser.get_header(self._dump_fptr)
            self.__dump_format__ = int(header['SVN-fs-dump-format-version'])
            self.__dump_uuid__ = str(header['UUID'])
        except Exception as err:
            raise DumpFixItError(err)


    def reader(self, rev=0):
        cp = CacheProvider(self.__dump_file__, self._rm_cache,
                           not self._retain_cache)
        cp.open()

        header = parser.get_header(self._dump_fptr)
        # check for exitance/useablity/validation of dmp_fname
        # Read in dump version and uuid
        #
        #pdb.set_trace()
        revision = parser.get_revision_iter(self._dump_fptr, rev)
        #node = parser._get_node(self._dump_fptr, revision)
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
