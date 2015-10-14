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

    _CACHE_SCHEMA[0] = []
    _CACHE_SCHEMA[1] = [
      """PRAGMA foreign_keys = ON""",
      """DROP TABLE IF EXISTS Header""",
      """CREATE TABLE Header(DumpVersion SMALLINT NOT NULL,
                             Uuid TEXT NOT NULL,
                             Checksum TEXT)""",
      """DROP TABLE IF EXISTS Revision""",
      """CREATE TABLE Revision(Rev INTEGER PRIMARY KEY NOT NULL,
                               PropContentLen INTEGER,
                               ContentLen INTEGER,
                               FilePos INTEGER,
                               RecLen INTEGER,
                               Checksum TEXT)""",
      """DROP TABLE IF EXISTS RevisionProps""",
      """CREATE TABLE RevisionProps(Rev INTEGER NOT NULL,
                                    Key TEXT,
                                    Value TEXT,
                                    FOREIGN KEY(Rev)
                                    REFERENCES Revision(Rev))""",
      """DROP TABLE IF EXISTS Node""",
      """CREATE TABLE Node(Rev INTEGER NOT NULL,
                           NodeID INTEGER,
                           NodePath TEXT NOT NULL,
                           NodeKind TEXT,
                           NodeAction TEXT,
                           NodeCopyFromRev INTEGER,
                           NodeCopyFromPath TEXT,
                           PropContentLen INTEGER,
                           TextContentLen INTEGER,
                           TextCopySrcMD5 TEXT,
                           TextCopySrcSHA1 TEXT,
                           TextContentMD5 TEXT,
                           TextContentSHA1 TEXT,
                           ContentLen INTEGER,
                           FilePos INTEGER,
                           RecLen INTEGER,
                           Checksum TEXT,
                           PRIMARY KEY(Rev, NodeID))""",
      """DROP TABLE IF EXISTS NodeProps""",
      """CREATE TABLE NodeProps(Rev INTEGER NOT NULL,
                                NodeID INTEGER NOT NULL,
                                Key TEXT,
                                VALUE TEXT,
                                FOREIGN KEY(Rev, NodeID)
                                REFERENCES Node(Rev, NodeID))"""
    ]


    def __init__(self, dump_fname, cache_fresh = False, cache_inmem = False):
       if dump_fname is None:
           raise DumpFilenameMissingError

       self._dump_file = os.path.abspath(dump_fname)
       self._cache_fresh = cache_fresh
       self._cache_inmem = cache_inmem
       self._cache_file = os.path.join(os.path.dirname(self._dump_file),
                                       ".%s.cache"
                                         % (os.path.basename(self._dump_file)))
