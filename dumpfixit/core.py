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
        if cls is not None:
            cls()
        pass


class Record:
    def __init__(self):
        self._start_addr = None
        self._size = None
        self._hash = None
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

    def _sizeof__(self):
        'Record._sizeof__() -> Physical size in bytes  of the Record in file.'
        return self._size

    def _hashof__(self):
        'Record._hashof__() -> Hash of the Record in file.'
        return self._hash

    def __addrof__(self):
        'Record.__addrof__() -> File pointer to locate the Record in file.'
        return self._start_addr

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

    def update(self, text, addr=None):
        if addr is None:
            raise ValueError

        self._start_addr = addr
        self._size = len(text)

        cache_hash = hashlib.md5()
        cache_hash.update(text)
        self._hash = cache_hash.hexdigest()

        itr = re.finditer("[^\n]*", text)
        for line in itr:
            s = line.group().split(":", 1)
            if len(s) >= 2:
               self[s[0]] = s[1].strip()


class Header(Record):
    pass


class Revision(Record):
    pass


class RevProps(Record):
    pass


class Node(Record):
    pass


class NodeProps(Record):
    pass
