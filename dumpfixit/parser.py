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

import pdb
import hashlib
from core import ConstNames
from core import Header, Revision, RevProps

__all__ = ["DumpParser"]

class DumpParser(object, ConstNames):

    CACHE_HASH = "CACHE-HASH"
    CACHE_SIZE = "CACHE-SIZE"

    # FIXME: How to be tolerant to malformed dumpfile.
    # What if, if we don't find what we look for in the
    # specific position?

    def _get_nodeprops(self, node_record):
        """
        Get a nodeprops from a given node record.

        Find the node properties (nodprops) for a given node record tuple
        returned by _get_node(). Will move the file pointer to next line
        following the revision record and read line by lines till the
        'PROPS-END' tag.

        Args:
           node_record (tuple): As returned by _get_node().

        Return:
           dict: Containg revprops entries.
        """ 
        fs = self._dump_fptr

        if node_record[0] is not None and \
           node_record[1] is not None:
            fs.seek(node_record[0] + node_record[1])

        record = {}

        line = fs.readline()
        while line != "":
            if line.strip() == self.PROPS_END_STR:
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
        pass


    def get_node_content(self, node_record, skip = False, size=4096):
        """
        Gets node content from a given node record.

        Returns content of a node as iterator. Each time next() of
        iterator is called 4K chunk is returned. Default 4K chunk
        size can be customized with SIZE arg. If SKIP is set True,
        the file pointer will be moved passed content without returning
        content.

        Args:
           node_record (tuple): As returned by _get_node().
           skip (boolean): A True will skip the content by just moving the
                   file pointer. Defaults to False
           size (long): Content size in bytes to return.

        Returns:
           string: Returns SIZE or less long bytes, if SKIP is set to FALSE.
                   Returns None if SKIP is set to TRUE.

        Raises:
           StopIteration: When no more content to iterate.
        """
        fs = self._dump_fptr

        def get_node_content_iter(fs, node_record, size):
            """
            Generator yielding iterator to iterate SIZE or less
            chuck on call to next().
            """
            content_len = long(node_record[2][self.CONTENTLEN_STR])

            while content_len > 0:
                if content_len >= size:
                   read_size = size
                else:
                   read_size = content_len

                yield fs.read(read_size)
                content_len -= read_size


        if node_record[0] is not None and \
           node_record[1] is not None:
            fs.seek(node_record[0] + node_record[1])

        # On Skip, just skip content and return none.
        if node_record[2].has_key(self.CONTENTLEN_STR) and skip == True:
            fs.seek(long(node_record[2][self.CONTENTLEN_STR]), 1)
            return None

        # On !Skip, reads content with a iterator.
        if node_record[2].has_key(self.CONTENTLEN_STR) and skip == False:
            return self.get_node_content_iter(fs, node_record, size)


    def _get_node(self):
        """
        Get a node record.

        Everytime called will find the next node record, which starts
        with 'Node-path:" and ends with new line ("\n"). Function won't
        search for node record beyond a Revision boundry (if it encounters
        a "Revision-number:" tag). Returns a tuple if a node record is
        found or else a None tuple.

        Return:
          tuple: With tuple containing 3 elements. All elements will 'None' if
                 node not found else index for the elements are as follows...
                  0) (long) First element is a file pointer to the begining
                            of the revision.
                  1) (long) Size of the revision record.
                  2) (dict) node record.
        """
        fs = self._dump_fptr
        record = {}
        filepos = fs.tell()
        found_record = False
        found_pos = 0
        found_size = 0
        cache_hash = hashlib.md5()

        # Node record starts of with the "Node-path:" and ends with
        # new line "\n".
        line = fs.readline()

        while line != "":
            if line.find(self.REVISION_STR) >= 0:
                fs.seek(filepos)
                break

            s = line.split(":", 1)

            if found_record == True and s[0] != '\n':
                record[s[0]] = s[1].strip()

            if (s[0] == self.NODE_PATH_STR):
                # A node is found.
                found_record = True
                found_pos = filepos
                record[self.NODE_PATH_STR] = s[1].strip()

            if found_record == True:
                cache_hash.update(line)
                found_size += len(line)

            if found_record == True and s[0] == '\n':
                found_record = False
                record[self.CACHE_HASH] = cache_hash.hexdigest()
                record[self.CACHE_SIZE] = found_size
                return (found_pos, found_size, record)

            filepos = fs.tell()
            line = fs.readline()

        # Noting to return.
        return (None, None, {})


    def get_node_iter(self, rev_record):
        """
        Return a generator yielding a node record.

        Create a iterator for node records which includes node, nodeprops
        from a given revision record returned by get_revision() or by
        get_revision_iter().

        Args:
           rev_record (tuple): As returned by get_revision() or
                               get_revision_iter()

        Returns:
           tuple: With 5 elements, index as follows...
                  0) (long) First element is a file pointer to the begining
                            of the revision.
                  1) (long) Size of the revision record.
                  2) (dict) revision record.
                  3) (dict) revprops record for the revision.
                  4) (iter) node records for the revision.

        Raises:
           StopIteration: When no more node records to iterate.
        """
        fs = self._dump_fptr

        if rev_record[0] is not None and \
           rev_record[1] is not None:
            fs.seek(rev_record[0] + rev_record[1])

        if rev_record[2] and \
           rev_record[2].has_key(self.CONTENTLEN_STR):
            fs.seek(long(rev_record[2][self.CONTENTLEN_STR]) + 1, 1)

        while True:
             # Finds the next node record.
             node_record = self._get_node(fs)
             if node_record[0] is None:
                 break

             # Finds the nodeprops for node.
             if node_record[2].has_key(self.PROP_CONTENTLEN_STR):
                 node_record += (self._get_nodeprops(fs, node_record),)

             if node_record[2].has_key(self.CONTENTLEN_STR):
                 self.get_node_content(fs, node_record, True)

             fs.seek(2, 1)

             yield node_record


    def _get_revprops(self, rev_record):
        """
        Get a revprops from a given revision record.

        Find the revisional properties (revprops) for a given revision record
        tuple returned by _get_revision(). Will move the file pointer to next
        line following the revision record and read line by lines till the
        'PROPS-END' tag.

        Args:
           rev_record (tuple): As returned by _get_revision().

        Return:
           dict: Containg revprops entries.
        """
        fs = self._dump_fptr
        rev_startaddr = rev_record.__addrof__()
        rev_sizeof = rev_record.__sizeof__()
        fs.seek(rev_startaddr + rev_sizeof)

        rprec = RevProps(fs.tell())

        if (rev_record.has_key(self.PROP_CONTENTLEN_STR)):
            lines = fs.read(rev_record[self.PROP_CONTENTLEN_STR])
            rprec.update(lines)

        return rprec

    def _get_revision(self, rev = None, pos = None):
        """
        Get a revision record for given revision.

        Find the given rev revision record from the pos file position. If no
        rev is given, find the next revision record from the pos file position.
        If pos not given revision record is searched from the current file
        position.

        Args:
           rev (long): Revision number to get. Default to None.
           pos (long): File pointer in fs where rev will be searched.

        Return:
          tuple: With tuple containing 3 elements. All elements will 'None' if
                 revision not found else index for the elements are as follows...
                  0) (long) First element is a file pointer to the begining
                            of the revision.
                  1) (long) Size of the revision record.
                  2) (dict) revision record.
        """
        fs = self._dump_fptr
        if pos is not None:
            fs.seek(pos)

        rrec = Revision()
        filepos = fs.tell()
        found_record = False
        found_pos = 0

        # Revision record starts of with the "Revision-number:" and ends with
        # new line "\n".
        line = fs.readline()
        while line != "":
            s = line.split(":", 1)

            if (s[0] == self.REVISION_STR) and \
               (rev is None or long(s[1]) == rev):
                # A revision is found or a requested revision is found.
                found_record = True
                found_pos = filepos

            if found_record == True:
                rrec.update(line, 0)

            if found_record == True and s[0] == '\n':
                found_record = False
                rrec.set_offset(found_pos)
                return rrec

            filepos = fs.tell()
            line = fs.readline()

        # Nothing to return.
        return None


    def get_header(self):
        """
        Reads header lines from a give dumpfile.

        Returns:
           dict: Header record.
        """

        fs = self._dump_fptr
        hrec = Header(0)
        fs.seek(0)

        line = fs.readline()
        while line != "":
            # WARNING: Dump version stamp must be the first line, if not
            # "Malformed dumpfile header" error occurs. But we do ignore
            # this rule, because anyhow we will regenerate the dump file
            # correctly.
            hrec.update(line, 0)
            s = line.split(":", 1)
            if s[0] == self.UUID_STR:
                # returns as soon as the uuid is found.
                break

            if s[0] == self.DUMP_FORMAT_STR and \
               int(s[1]) < 2:
                # UUID won't exist for version below 2.
                break

            line = fs.readline()

        return hrec


    def get_revision(self, rev = None):
        """
        Get a revision record.

        Get revision details including revprops and node record for a given
        revision from the dump file and returns a tuple. If no revision is
        given then None is returned.

        Args:
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

        fs = self._dump_fptr

        if rev is None:
            return None

        # Rewinds the file pointer everytime to top of the file
        # when you call the generator.
        fs.seek(0)

        # Finds the next revision record.
        rev_record = self._get_revision(rev=rev)
        # Finds the revprops for revision.
        rev_record += (self._get_revprops(rev_record),)
        # Including node generator part of rev_record.
        rev_record += (self.get_node_iter(rev_record),)

        return rev_record


    def get_revision_iter(self, rev=0):
        """
        Return a generator yielding a revision record.

        Create a iterator for revision records which includes revision,
        revprops, nodes starting from a given revision to the last revision.

        Args:
           rev (long): Revision number from where the iterator starts.
                       Default to 0.

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
        fs = self._dump_fptr
        fs.seek(0)
        revision = rev

        while True:
             # Finds the next revision record.
             rev_record = self._get_revision(rev=revision)
             if rev_record is None:
                 break
             # Finds the revprops for revision.
             revp_record = self._get_revprops(rev_record)
             # Included node generator part of rev_record.
             node_record = self.get_node_iter(rev_record)

             yield rev_record
             # Move to next rev.
             revision += 1


