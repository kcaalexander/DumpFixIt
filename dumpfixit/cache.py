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
                             RecLen INTEGER,
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
                           NodeID INTEGER PRIMARY KEY,
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
                           Checksum TEXT)""",
      """DROP TABLE IF EXISTS NodeProps""",
      """CREATE TABLE NodeProps(Rev INTEGER NOT NULL,
                                NodeID INTEGER NOT NULL,
                                Key TEXT,
                                VALUE TEXT,
                                FOREIGN KEY(NodeID)
                                REFERENCES Node(NodeID))"""
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

        self.__open()


    def __open(self):
        ### FIXME: Should we convert a exiting in-file cache to
        ###        in-memory, rather than deleting it?
        ###        For now we delete the in-file cache if in-memory
        ###        cache is opted for second time.

        # Remove existing cache file, if asked to create fresh or
        # for in-memory.
        if (os.path.exists(self._cache_file) and \
            (self._cache_fresh is True or self._cache_inmem is True)):
            os.remove(self._cache_file)

        # Connect to a cache.
        if self._cache_inmem is True:
            self._cache_conn = sqlite3.connect(":memory:")
        else:
            self._cache_conn = sqlite3.connect(self._cache_file)

        cur = self._cache_conn.cursor()
        cur.execute('PRAGMA user_version')
        schema_version = int(cur.fetchone()[0])

        for i in range(schema_version+1, len(self._CACHE_SCHEMA)):
            for j in self._CACHE_SCHEMA[i]:
                cur.execute(j)

            cur.execute('PRAGMA user_version = %d' %(i))

        self._cache_conn.commit()
        cur.close()


    def cache_store_header(self, header):
        """
        Stores header into cache.

        Takes a header record and store the header entries into the cache.

        Args:
           header: Dict of header record.

        Returns:
           None
        """

        cur = self._cache_conn.cursor()
        cur.execute("INSERT INTO Header (DumpVersion, Uuid, RecLen, Checksum) " \
                    "VALUES ('%d', '%s', '%d', '%s')" % \
                    (header[self.DUMP_FORMAT_STR], header[self.UUID_STR], \
                     header[self.CACHE_SIZE], header[self.CACHE_HASH]))
        self._cache_conn.commit()
        cur.close()


    def cache_fetch_header(self):
        """
        Retrives header from cache.

        Reads header entries from cache and store in a header record and returns.

        Args:
           None

        Returns:
           Dict of header record.
        """
        record = {}
        cur = self._cache_conn.execute("SELECT DumpVersion, Uuid, RecLen, " \
                                       "Checksum FROM Header")
        row = cur.fetchone()
        record[self.DUMP_FORMAT_STR] = row[0]
        record[self.UUID_STR] = row[1]
        record[self.CACHE_SIZE] = row[2]
        record[self.CACHE_HASH] = row[3]
        cur.close()

        return record


    def cache_store_revision(self, revision):
        """
        Stores revision into cache.

        Takes a revision record and store the revision entries including
        revprops into the cache.

        Args:
           revision: Dict of revision record.

        Returns:
           None
        """

        cur = self._cache_conn.cursor()
        cur.execute("INSERT INTO Revision (Rev, PropContentLen, ContentLen, " \
                    "FilePos, RecLen, Checksum) VALUES ('%d', '%s', '%s', " \
                    "'%d', '%d', '%s')" % (revision[2][self.REVISION_STR],
                     revision[2][self.PROP_CONTENTLEN_STR],
                     revision[2][self.CONTENTLEN_STR],
                     revision[0],
                     revision[2][self.CACHE_SIZE],
                     revision[2][self.CACHE_HASH]))
        for prop in revision[3]:
            cur.execute("INSERT INTO RevisionProps(Rev, Key, Value) " \
                        "VALUES ('%d', '%s', '%s')" %
                        (revision[2][self.REVISION_STR],
                         prop, revision[3][prop]))
        self._cache_conn.commit()
        cur.close()


    def cache_store_node(self, revision, node):
        """
        Stores node into cache.

        Takes a revision & node record and store the node entries including
        nodeprops into the cache.

        Args:
           revision: Dict of revision record.
           node: Dict of revision record.

        Returns:
           None
        """

        cur = self._cache_conn.cursor()
        cur.execute("INSERT INTO Node(Rev, NodePath, NodeKind, NodeAction, " \
                    "NodeCopyFromRev, NodeCopyFromPath, PropContentLen, " \
                    "TextContentLen, TextCopySrcMD5, TextCopySrcSHA1, " \
                    "TextContentMD5, TextContentSHA1, ContentLen, FilePos, " \
                    "RecLen, Checksum) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, " \
                    "?, ?, ?, ?, ?, ?, ?)", (revision[2][self.REVISION_STR],
                     node[2].has_key(self.NODE_PATH_STR) and
                                       node[2][self.NODE_PATH_STR] or None,
                     node[2].has_key(self.NODE_KIND_STR) and
                                       node[2][self.NODE_KIND_STR] or None,
                     node[2].has_key(self.NODE_ACTION_STR) and
                                     node[2][self.NODE_ACTION_STR] or None,
                     node[2].has_key(self.NODE_COPYFROM_REV) and
                                   node[2][self.NODE_COPYFROM_REV] or None,
                     node[2].has_key(self.NODE_COPYFROM_PATH) and
                                  node[2][self.NODE_COPYFROM_PATH] or None,
                     node[2].has_key(self.PROP_CONTENTLEN_STR) and
                                 node[2][self.PROP_CONTENTLEN_STR] or None,
                     node[2].has_key(self.TEXT_CONTENTLEN_STR) and
                                 node[2][self.TEXT_CONTENTLEN_STR] or None,
                     node[2].has_key(self.TEXT_COPY_SOURCE_MD5) and
                                node[2][self.TEXT_COPY_SOURCE_MD5] or None,
                     node[2].has_key(self.TEXT_COPY_SOURCE_SHA1) and
                               node[2][self.TEXT_COPY_SOURCE_SHA1] or None,
                     node[2].has_key(self.TEXT_CONTENT_MD5) and
                                    node[2][self.TEXT_CONTENT_MD5] or None,
                     node[2].has_key(self.TEXT_CONTENT_SHA1) and
                                   node[2][self.TEXT_CONTENT_SHA1] or None,
                     node[2].has_key(self.CONTENTLEN_STR) and
                                   node[2][self.CONTENTLEN_STR] or None,
                     node[0], node[2][self.CACHE_SIZE],
                     node[2][self.CACHE_HASH],))

        node_id = cur.lastrowid
        if node[2].has_key(self.PROP_CONTENTLEN_STR):
            for prop in node[3]:
                cur.execute("INSERT INTO NodeProps(Rev, NodeID, Key, Value) " \
                            "VALUES (?, ?, ?, ?)", 
                            (revision[2][self.REVISION_STR], node_id,
                             prop, node[3][prop]))
        self._cache_conn.commit()
        cur.close()


    def cache_store_revisionall(self, revision):
        """
        Stores full revision into cache.

        Takes a revision record and store the revision entries including
        revprops, node, nodeprops entries into the cache.

        Args:
           revision: Dict of revision record.

        Returns:
           None
        """

        self.cache_store_revision(revision)
        if revision[4] is not None:
            while True:
                try:
                    node = revision[4].next()
                    self.cache_store_node(revision, node)
                except StopIteration:
                    break;
