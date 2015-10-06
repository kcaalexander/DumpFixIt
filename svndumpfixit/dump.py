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


import core

@Singleton
class DumpProvider(object):

    _dump_file = None # Absoulte path to dump filename.
    _rm_cache = False # Remove existing cache file.
    _retain_cache = True # In-memory cache, removed on prg exit.

    def __init__(self, dmp_fname = None, rm_cache = False,
                 retain_cache = True):
        # error-out if dmp_fname is None
        # check for exitance/useablity/validation of dmp_fname
        # remove existing cache db if rm_cache is 'True'
        # decide on the db_cache filename.
        # if rm_cache is 'True' and retain_cache is 'True', open db cache
        # if rm_cache is 'True' and retain_cache is 'False', open mem cache
        # if rm_cache is 'False' and retain_cache is 'False', open mem cache
        #
        pass

class DumpRevisionRecordProvier(DumpProvider):
    # Holds both revision record and revision props.
    def __init__(self, revision = None):
        pass

class DumpNodeRecordProvider(DumpRevisionRecordProvier):
    # Holds both node record and node props.

    def __init__(self, revision = None, node-path = None):
        pass

class DumpContentRecordProvider(DumpNodeRecordProvier):

    def __init__(self, revision = None, node-path = None):
        pass

