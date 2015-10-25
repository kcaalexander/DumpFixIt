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


__all__ = []

PROPS_END_STR = "PROPS-END"
DUMP_FORMAT_STR = "SVN-fs-dump-format-version"
UUID_STR = "UUID"
REVISION_STR = "Revision-number"
PROP_CONTENTLEN_STR = "Prop-content-length"
TEXT_CONTENTLEN_STR = "Text-content-length"
CONTENTLEN_STR = "Content-length"
NODE_PATH_STR = "Node-path"

NODE_RECORD_HEADERS = [
    NODE_PATH_STR,
    "Node-kind",
    "Node-action",
    "Node-copyfrom-rev",
    "Node-copyfrom-path",
    PROP_CONTENTLEN_STR,
    TEXT_CONTENTLEN_STR,
    "Text-copy-source-md5",
    "Text-copy-source-sha1",
    "Text-content-md5",
    "Text-content-sha1",
    CONTENTLEN_STR
]

REV_RECORD_HEADERS = [
    REVISION_STR,
    PROP_CONTENTLEN_STR,
    CONTENTLEN_STR
]


