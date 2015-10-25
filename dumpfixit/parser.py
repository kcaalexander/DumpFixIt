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


__all__ = ["get_header", "get_revision", "get_revisions"]

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


def _find_revprops(fs, rev_record):
    """
    Get a revprops from a given revision record.

    Find the revisional properties (revprops) for a given revision record
    tuple returned by _find_revision(). Will move the file pointer to next
    line following the revision record and read line by lines till the
    'PROPS-END' tag.

    Args:
       fs (file): File object of dumpfile to read
       rev_record (tuple): As returned by _fine_revision().

    Return:
       dict: Containg revprops entries.
    """
    if rev_record[0] is not None and \
       rev_record[1] is not None:
        fs.seek(rev_record[0] + rev_record[1])

    # FIXME: How to be tolerant to malformed dumpfile.
    # What if, if we don't find what we look for in the
    # specific position?
    record = {}

    line = fs.readline()
    while line != "":
        if line.strip() == PROPS_END_STR:
            break

        # Reads K record.
        krec = line.strip().split()
        key = fs.readline().strip()
        if long(krec[1]) != len(key):
          # TODO: raise a warning exception to say key len and actual
          # don't match.
          pass

        # Reads V record.
        line = fs.readline()
        vrec = line.strip().split()
        value = fs.readline().strip()
        if long(vrec[1]) != len(value):
          # TODO: raise a warning exception to say key len and actual don't
          # match.
          pass

        record[key] = value
        line = fs.readline()

    return record


def _find_revision(fs, rev = None, pos = None):
    """
    Get a revision record for given revision.

    Find the given rev revision record from the pos file position. If no
    rev is given, find the next revision record from the pos file position.
    If pos not given revision record is searched from the current file
    position.

    Args:
       fs (file): File object of dumpfile to read
       rev (long): Revision number to get. Default to None.
       pos (long): File pointer in fs where rev will be searched.

    Return:
      tuple: With tuple containing 3 elements. All elements will 'None' if
             revision not found else index for the elements are as follows...
              0) (long) First element is a file pointer to the begining
                        of the revision.
              1) (long) Size of the revision record.
              2) (dict) revision record.
              3) (dict) revprops record for the revision.
    """

    if pos is not None: 
        fs.seek(pos)

    record={}
    filepos = fs.tell()
    found_record = False
    found_pos = 0
    found_size = 0

    line = fs.readline()
    while line != "":
        s = line.split(":", 1)

        if found_record == True and s[0] != '\n':
            record[s[0]] = s[1].strip()

        if (s[0] == REVISION_STR) and (rev is None or long(s[1]) == rev):
            # A revision is found or a requested revision is found.
            found_record = True
            found_pos = filepos
            record[REVISION_STR] = int(s[1])

        if found_record == True:
            found_size += len(line)

        if found_record == True and s[0] == '\n':
            found_record = False
            return (found_pos, found_size, record)

        filepos = fs.tell()
        line = fs.readline()

    # Noting to return.
    return (None, None, {})


def get_header(fs):
    """
    Reads header lines from a give dumpfile.

    Args:
       fs (file): File object of dumpfile to read

    Returns:
       dict: Header record.
    """

    record={}
    fs.seek(0)
    line = fs.readline()
    while line != "":
        s = line.split(":", 1)
        # WARNING: Dump version stamp must be the first line, if not
        # "Malformed dumpfile header" error occurs. But we do ignore
        # this rule, because anyhow we will regenerate the dump file
        # correctly.
        if s[0] == DUMP_FORMAT_STR:
            record[DUMP_FORMAT_STR] = int(s[1])

        if s[0] == UUID_STR:
            record[UUID_STR] = s[1].strip()
            # returns as soon as the uuid is found.
            break

        if record.has_key(DUMP_FORMAT_STR) and \
           record[DUMP_FORMAT_STR] < 2:
            # UUID won't exist for version below 2.
            break

        line = fs.readline()

    return record


def get_revision(fs, rev = None):
    """
    Get a revision record.

    Get revision details including revprops and node record for a given
    revision from the dump file and returns.

    Args:
       fs (file): File object of dumpfile to read
       rev (long): Revision number to get. Default to None.

    Returns:
       tuple: With 5 elements, index as follows...
              0) (long) First element is a file pointer to the begining
                        of the revision.
              1) (long) Size of the revision record.
              2) (dict) revision record.
              3) (dict) revprops record for the revision.
              4) (iter) node records for the revision.
    """

    if rev is None:
        return None
    # Rewinds the file pointer everytime to top of the file
    # when you call the generator.
    fs.seek(0)

    # Finds the next revision record.
    rev_record = _find_revision(fs, rev=rev)
    # Finds the revprops for revision.
    rev_record += (_find_revprops(fs, rev_record),)
    # TODO: Include node generator part of rev_record.

    return rev_record


def get_revisions(fs, rev=0):
    """
    Generator for revision records.

    Create a iterator for revision records which includes revision,
    revprops, nodes starting from a given revision to the last revision.

    Args:
       fs (file): File object of dumpfile to read
       rev (long): Revision number to get. Default to 0.

    Returns:
       tuple: With 5 elements, index as follows...
              0) (long) First element is a file pointer to the begining
                        of the revision.
              1) (long) Size of the revision record.
              2) (dict) revision record.
              3) (dict) revprops record for the revision.
              4) (iter) node records for the revision.

    Raises:
       StopIteration: When no more revision records to iterate.
    """

    # Rewinds the file pointer everytime to top of the file
    # when you call the generator.
    fs.seek(0)
    revision = rev

    while True:
         # Finds the next revision record.
         rev_record = _find_revision(fs, rev=revision)
         # Finds the revprops for revision.
         rev_record += (_find_revprops(fs, rev_record),)
         # TODO: Include node generator part of rev_record.

         yield rev_record
         # Move to next rev.
         revision += 1


