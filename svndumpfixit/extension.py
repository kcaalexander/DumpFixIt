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

def Singleton(cls):
    _instances_ = {}

    def CreateInstance(*args, **kwargs):
        if cls not in _instances_:
           _instances_[cls] = cls(*args, **kwargs)

        return _instances_[cls]

    return CreateInstance


class RegisterExtension(type):
    def __new__(cls, name, baseclass, attributes):

        klass = type.__new__(cls, name, baseclass, attributes)
        try:
            ExtensionProvider
        except NameError:
            klass.registry = {}
        else:
            if attributes.has_key('command'):
                command = attributes['command']
                ExtensionProvider.registry[command] = klass

        return klass

    def __init__(cls, name, baseclass, attributes):
        pass


class ExtensionUtils(object):
   def __init__(self):
       pass
       
   def LoadExtension(self):
       pass


class ExtensionProvider(ExtensionUtils):
    __metaclass__ = RegisterExtension
