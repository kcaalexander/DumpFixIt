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

__all__ = ["CommandProvider", "Singleton", "ConstNames",
           "Header", "Revision", "RevProps", "Node", "NodeProps"]

import re
import error
import hashlib

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
        if cls is not None:
            cls()
        pass


class ConstNames:
    PROPS_END_STR = "PROPS-END"
    DUMP_FORMAT_STR = "SVN-fs-dump-format-version"
    UUID_STR = "UUID"
    REVISION_STR = "Revision-number"
    PROP_CONTENTLEN_STR = "Prop-content-length"
    TEXT_CONTENTLEN_STR = "Text-content-length"
    CONTENTLEN_STR = "Content-length"
    NODE_PATH_STR = "Node-path"
    NODE_KIND_STR = "Node-kind"
    NODE_ACTION_STR = "Node-action"
    NODE_COPYFROM_REV = "Node-copyfrom-rev"
    NODE_COPYFROM_PATH = "Node-copyfrom-path"
    TEXT_COPY_SOURCE_MD5 = "Text-copy-source-md5"
    TEXT_COPY_SOURCE_SHA1 = "Text-copy-source-sha1"
    TEXT_CONTENT_MD5 = "Text-content-md5"
    TEXT_CONTENT_SHA1 = "Text-content-sha1"

    NODE_RECORD_HEADERS = [
        NODE_PATH_STR,
        NODE_KIND_STR,
        NODE_ACTION_STR,
        NODE_COPYFROM_REV,
        NODE_COPYFROM_PATH,
        PROP_CONTENTLEN_STR,
        TEXT_CONTENTLEN_STR,
        TEXT_COPY_SOURCE_MD5,
        TEXT_COPY_SOURCE_SHA1,
        TEXT_CONTENT_MD5,
        TEXT_CONTENT_SHA1,
        CONTENTLEN_STR
    ]

    REV_RECORD_HEADERS = [
        REVISION_STR,
        PROP_CONTENTLEN_STR,
        CONTENTLEN_STR
    ]


class Record(object):
    def __init__(self, offset=None):
        self._start_addr = offset
        self._size = None
        self._hash = hashlib.md5()
        self._entries = {}

    def __eq__(self, other):
        'Record.__eq__(y) <==> Record == y'
        # Comparison to another Record against the __entires.
        if not (isinstance(self, Record) or \
           isinstance(other, Record)):
            return False
        return (self._entries == other._entries)

    def __ne__(self, other):
        'Record.__ne__(y) <==> Record != y'
        # Compares to another Record against the _entries for not equal.
        if not (isinstance(self, Record) or \
           isinstance(other, Record)):
            return True
        return (self._entries != other._entries)

    def __sizeof__(self):
        'Record.__sizeof__() -> Physical size in bytes of the Record in file.'
        return self._size if self._size is not None else 0

    def __hashof__(self):
        'Record.__hashof__() -> Hash of the Record in file.'
        return self._hash.hexdigest()

    def __addrof__(self):
        'Record.__addrof__() -> File pointer to locate the Record in file.'
        return self._start_addr if self._start_addr is not None else 0

    def copy(self):
        'Record.copy() -> a shallow copy of Record.'
        import copy
        c = copy.copy(self)
        c._entries = self._entries.copy()
        return c

    def clear(self):
        'Record.clear() -> Cleans up the Record.'
        self._entries.clear()
        self._start_addr = None
        self._size = None
        self._hash = None

    def __contains__(self, key):
        'Record.__contains__(i, y) <==> y in Record'
        # Return True/False if key is in or not in self._entries.
        return key in self._entries

    def __setitem__(self, key, value):
        'Record.__setitem__(i, y) <==> Record[i]=y'
        # Setting a new item creates a new properties entrie by adding in the
        # self._entries dictionary.
        return dict.__setitem__(self._entries, key, value)

    def __delitem__(self, key):
        'Record.__delitem__(y) <==> del Record[y]'
        # Deleting an existing item in self._entries by key.
        dict.__delitem__(self._entries, key)

    def __getitem__(self, key):
        'Record.__getitem__(y) <==> Record[y]'
        # Getting an existing item in self._entries by key.
        return dict.__getitem__(self._entries, key)

    def __iter__(self):
        'Record.iterkeys() -> an iterator over the keys in Record'
        # Return a iterator to iterate over the keys in Record
        return dict.__iter__(self._entries)

    def __str__(self):
        'Record.__str__(i) <==> str(Record)'
        # Return string representation of self._entries.
        return str(dict(self._entries))

    def __repr__(self):
        'Record.__repr__(i) <==> repr(Record)'
        # Return string representation of self._entries.
        return '"%s"' % (repr(dict(self._entries)))

    def __len__(self):
        return len(self._entries)

    def keys(self):
        'Record.keys() -> list of keys in Record.'
        # Return a list of keys in Record.
        return list(self)

    def values(self):
        'Record.values() -> list of values in Record'
        # Return a list of values in Record.
        return [self[key] for key in self]

    def items(self):
        'Record.items() -> list of (key, value) pairs in Record'
        # Return a list of (keys, value) pair in Record.
        return [(key, self._entries[key]) for key in self._entries]

    'Record.iterkeys -> an iterator over the keys in Record'
    # Return a iterator to iterate over the keys in Record
    iterkeys = __iter__

    def itervalues(self):
        'Record.itervalues -> an iterator over the values in Record'
        # Return a iterator to iterate over the values in Record
        for k in self._entries:
            yield self._entries[k]

    def iteritems(self):
        'Record.iteritems -> an iterator over the (key, value) pairs in Record'
        # Return a iterator to iterate over the (key, value) pairs in Record
        for k in self._entries:
            yield (k, self._entries[k])

    def has_key(self, key):
        'Record.has_key(i, y) -> looks up self._entries for key'
        # Returns True/False by looking up self._entries for key.'
        try:
           self._entries[key]
        except KeyError:
           return False
        return True

    def has_value(self, value):
        'Record.has_value(i, y) -> looks up self._entries for value'
        # Returns True/False by looking up self._entries for value.'
        try:
           return value in self.values()
        except KeyError:
           return False
        return True

    def set_offset(self, offset=None):
        # Expects to call offset with non-None arg for the first time.
        if offset is None :
            if self._start_addr is None:
                raise ValueError('must be a non-None value.')
            else:
                self._start_addr = offset
        else:
            self._start_addr = offset

        return

    def update(self, text=None, offset=None):
        if text is None:
            raise ValueError('must be a non-None value.')

        self.set_offset(offset)

        if self._size is None:
            self._size = len(text)
        else:
            self._size += len(text)
        self._hash.update(text)

        itr = re.finditer("[^\n]*", text)
        for line in itr:
            s = line.group().split(":", 1)
            if len(s) >= 2:
               self[s[0]] = s[1].strip()

        return


class Header(Record, ConstNames):
    def set_format(self, version):
        'Header.set_format(x) -> Header["SVN-fs-dump-format-version"] = x'
        # Sets an integer dump file version.
        if type(version) is not int:
            raise ValueError

        self[self.DUMP_FORMAT_STR] = int(version)
        return self[self.DUMP_FORMAT_STR]

    def get_format(self):
        'Header.get_format() -> Header["SVN-fs-dump-format-version"]'
        # Returns integer dump file version. If not found returns None.
        try:
            version = self._entries[self.DUMP_FORMAT_STR]
        except KeyError:
           return None
        return int(version)

    def set_uuid(self, uuid):
        'Header.get_uuid(x) -> Header["UUID"] = x'
        # Sets UUID to dump file.

        if type(uuid) is not str:
            raise ValueError
        #TODO: Validate UUID.

        self[self.UUID_STR] = uuid
        return self[self.UUID_STR]

    def get_uuid(self):
        'Header.get_uuid() -> Header["UUID"]'
        # Returns string UUID of dump file. If not found returns None.
        try:
            uuid = self._entries[self.UUID_STR]
        except KeyError:
           return None
        return uuid

    def update(self, text=None, offset=None):
        if text is None:
            raise ValueError('must be a non-None value.')

        self.set_offset(offset)

        if self._size is None:
            self._size = len(text)
        else:
            self._size += len(text)
        self._hash.update(text)

        itr = re.finditer("[^\n]*", text)
        for line in itr:
            s = line.group().split(":", 1)
            if len(s) < 2:
                continue
            if s[0] == self.DUMP_FORMAT_STR:
                self[self.DUMP_FORMAT_STR] = int(s[1])

            if s[0] == self.UUID_STR:
                self[self.UUID_STR] = s[1].strip()
                # returns as soon as the uuid is found.
                break

            if self.has_key(self.DUMP_FORMAT_STR) and \
               self[self.DUMP_FORMAT_STR] < 2:
                # UUID won't exist for version below 2.
                break
        return


class Revision(Record, ConstNames):
    def __init__(self, offset=None):
        super(Revision, self).__init__(offset)
        self._revprops = None
        self._nodes = None

    def set_revision(self, rev):
        'Revision.set_revision(x) -> Revision["Revision-number"] = x'
        # Sets an integer revision number.
        if type(rev) is not int:
            raise ValueError

        self[self.REVISION_STR] = int(rev)
        return self[self.REVISION_STR]

    def get_revision(self):
        'Revision.get_format() -> Revision["Revision-number"]'
        # Returns integer revision number. If not found returns None.
        try:
            rev = self._entries[self.REVISION_STR]
        except KeyError:
           return None
        return int(rev)

    def update(self, text=None, offset=None):
        if text is None:
            raise ValueError('must be a non-None value.')

        self.set_offset(offset)

        if self._size is None:
            self._size = len(text)
        else:
            self._size += len(text)
        self._hash.update(text)

        itr = re.finditer("[^\n]*", text)
        for line in itr:
            s = line.group().split(":", 1)
            if len(s) < 2:
                continue
            if s[0] in self.REV_RECORD_HEADERS:
                self[s[0]] = int(s[1])
        return


class RevProps(Record, ConstNames):
    pass


class Node(Record, ConstNames):
    pass


class NodeProps(Record):
    pass
