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

__all__ = ["CacheProvider"]

import os
import sqlite3

import error

class CacheProvider(object):

    _dump_file = None # Fullpath to source dump file.
    _cache_file = None # Fullpath to cache file
    _cache_fresh = False # if True; remove existing cache file.
    _cache_inmem = False # if True create a non-pristine in-memory cache.
    _cache_conn = None # fd to open cache file.
    _CACHE_SCHEMA = {}


    def __init__(self, dump_fname, cache_fresh = False, cache_inmem = False):
       if dump_fname is None:
           raise DumpFilenameMissingError

       self._dump_file = os.path.abspath(dump_fname)
       self._cache_fresh = cache_fresh
       self._cache_inmem = cache_inmem
       self._cache_file = os.path.join(os.path.dirname(self._dump_file),
                                       ".%s.cache"
                                         % (os.path.basename(self._dump_file)))
