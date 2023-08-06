# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=88 et ai si
#
# Copyright (c) 2012-2014 Intel, Inc.
# License: GPLv2
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#
# Modified by Romain Gantois <romain.gantois@bootlin.com> in 2023
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

"""
This module implements the block map (bmap) creation functionality and provides
the corresponding API in form of the 'BmapCreate' class.

The idea is that while images files may generally be very large (e.g., 4GiB),
they may nevertheless contain only little real data, e.g., 512MiB. This data
are files, directories, file-system meta-data, partition table, etc. When
copying the image to the target device, you do not have to copy all the 4GiB of
data, you can copy only 512MiB of it, which is 4 times less, so copying should
presumably be 4 times faster.

The block map file is an XML file which contains a list of blocks which have to
be copied to the target device. The other blocks are not used and there is no
need to copy them. The XML file also contains some additional information like
block size, image size, count of mapped blocks, etc. There are also many
commentaries, so it is human-readable.

The image has to be a sparse file. Generally, this means that when you generate
this image file, you should start with a huge sparse file which contains a
single hole spanning the entire file. Then you should partition it, write all
the data (probably by means of loop-back mounting the image or parts of it),
etc. The end result should be a sparse file where mapped areas represent useful
parts of the image and holes represent useless parts of the image, which do not
have to be copied when copying the image to the target device.

This module uses the FIEMAP ioctl to detect holes.
"""

# Disable the following pylint recommendations:
#   *  Too many instance attributes - R0902
#   *  Too few public methods - R0903
# pylint: disable=R0902,R0903

import hashlib
from snagflash.bmaptools.BmapHelpers import human_size
from snagflash.bmaptools import Filemap

# The bmap format version we generate.
#
# Changelog:
# o 1.3 -> 2.0:
#   Support SHA256 and SHA512 checksums, in 1.3 only SHA1 was supported.
#   "BmapFileChecksum" is used instead of "BmapFileSHA1", and "chksum="
#   attribute is used instead "sha1=". Introduced "ChecksumType" tag. This is
#   an incompatible change.
#   Note, bmap format 1.4 is identical to 2.0. Version 1.4 was a mistake,
#   instead of incrementing the major version number, we incremented minor
#   version number. Unfortunately, the mistake slipped into bmap-tools version
#   3.0, and was only fixed in bmap-tools v3.1.
SUPPORTED_BMAP_VERSION = "2.0"

_BMAP_START_TEMPLATE = """<?xml version="1.0" ?>
<!-- This file contains the block map for an image file, which is basically
     a list of useful (mapped) block numbers in the image file. In other words,
     it lists only those blocks which contain data (boot sector, partition
     table, file-system metadata, files, directories, extents, etc). These
     blocks have to be copied to the target device. The other blocks do not
     contain any useful data and do not have to be copied to the target
     device.

     The block map an optimization which allows to copy or flash the image to
     the image quicker than copying of flashing the entire image. This is
     because with bmap less data is copied: <MappedBlocksCount> blocks instead
     of <BlocksCount> blocks.

     Besides the machine-readable data, this file contains useful commentaries
     which contain human-readable information like image size, percentage of
     mapped data, etc.

     The 'version' attribute is the block map file format version in the
     'major.minor' format. The version major number is increased whenever an
     incompatible block map format change is made. The minor number changes
     in case of minor backward-compatible changes. -->

<bmap version="%s">
    <!-- Image size in bytes: %s -->
    <ImageSize> %u </ImageSize>

    <!-- Size of a block in bytes -->
    <BlockSize> %u </BlockSize>

    <!-- Count of blocks in the image file -->
    <BlocksCount> %u </BlocksCount>

"""


class Error(Exception):
    """
    A class for exceptions generated by this module. We currently support only
    one type of exceptions, and we basically throw human-readable problem
    description in case of errors.
    """

    pass


class BmapCreate(object):
    """
    This class implements the bmap creation functionality. To generate a bmap
    for an image (which is supposedly a sparse file), you should first create
    an instance of 'BmapCreate' and provide:

    * full path or a file-like object of the image to create bmap for
    * full path or a file object to use for writing the results to

    Then you should invoke the 'generate()' method of this class. It will use
    the FIEMAP ioctl to generate the bmap.
    """

    def __init__(self, image, bmap, chksum_type="sha256"):
        """
        Initialize a class instance:
        * image  - full path or a file-like object of the image to create bmap
                   for
        * bmap   - full path or a file object to use for writing the resulting
                   bmap to
        * chksum - type of the check sum to use in the bmap file (all checksum
                   types which python's "hashlib" module supports are allowed).
        """

        self.image_size = None
        self.image_size_human = None
        self.block_size = None
        self.blocks_cnt = None
        self.mapped_cnt = None
        self.mapped_size = None
        self.mapped_size_human = None
        self.mapped_percent = None

        self._mapped_count_pos1 = None
        self._mapped_count_pos2 = None
        self._chksum_pos = None

        self._f_image_needs_close = False
        self._f_bmap_needs_close = False

        self._cs_type = chksum_type.lower()
        try:
            self._cs_len = len(hashlib.new(self._cs_type).hexdigest())
        except ValueError as err:
            raise Error(
                'cannot initialize hash function "%s": %s' % (self._cs_type, err)
            )

        if hasattr(image, "read"):
            self._f_image = image
            self._image_path = image.name
        else:
            self._image_path = image
            self._open_image_file()

        if hasattr(bmap, "read"):
            self._f_bmap = bmap
            self._bmap_path = bmap.name
        else:
            self._bmap_path = bmap
            self._open_bmap_file()

        try:
            self.filemap = Filemap.filemap(self._f_image)
        except (Filemap.Error, Filemap.ErrorNotSupp) as err:
            raise Error(
                "cannot generate bmap for file '%s': %s" % (self._image_path, err)
            )

        self.image_size = self.filemap.image_size
        self.image_size_human = human_size(self.image_size)
        if self.image_size == 0:
            raise Error(
                "cannot generate bmap for zero-sized image file '%s'" % self._image_path
            )

        self.block_size = self.filemap.block_size
        self.blocks_cnt = self.filemap.blocks_cnt

    def __del__(self):
        """The class destructor which closes the opened files."""
        if self._f_image_needs_close:
            self._f_image.close()
        if self._f_bmap_needs_close:
            self._f_bmap.close()

    def _open_image_file(self):
        """Open the image file."""
        try:
            self._f_image = open(self._image_path, "rb")
        except IOError as err:
            raise Error("cannot open image file '%s': %s" % (self._image_path, err))

        self._f_image_needs_close = True

    def _open_bmap_file(self):
        """Open the bmap file."""
        try:
            self._f_bmap = open(self._bmap_path, "w+")
        except IOError as err:
            raise Error("cannot open bmap file '%s': %s" % (self._bmap_path, err))

        self._f_bmap_needs_close = True

    def _bmap_file_start(self):
        """
        A helper function which generates the starting contents of the block
        map file: the header comment, image size, block size, etc.
        """

        # We do not know the amount of mapped blocks at the moment, so just put
        # whitespaces instead of real numbers. Assume the longest possible
        # numbers.

        xml = _BMAP_START_TEMPLATE % (
            SUPPORTED_BMAP_VERSION,
            self.image_size_human,
            self.image_size,
            self.block_size,
            self.blocks_cnt,
        )
        xml += "    <!-- Count of mapped blocks: "

        self._f_bmap.write(xml)
        self._mapped_count_pos1 = self._f_bmap.tell()

        xml = "%s or %s   -->\n" % (
            " " * len(self.image_size_human),
            " " * len("100.0%"),
        )
        xml += "    <MappedBlocksCount> "

        self._f_bmap.write(xml)
        self._mapped_count_pos2 = self._f_bmap.tell()

        xml = "%s </MappedBlocksCount>\n\n" % (" " * len(str(self.blocks_cnt)))

        # pylint: disable=C0301
        xml += "    <!-- Type of checksum used in this file -->\n"
        xml += "    <ChecksumType> %s </ChecksumType>\n\n" % self._cs_type

        xml += "    <!-- The checksum of this bmap file. When it is calculated, the value of\n"
        xml += '         the checksum has be zero (all ASCII "0" symbols).  -->\n'
        xml += "    <BmapFileChecksum> "

        self._f_bmap.write(xml)
        self._chksum_pos = self._f_bmap.tell()

        xml = "0" * self._cs_len + " </BmapFileChecksum>\n\n"
        xml += (
            "    <!-- The block map which consists of elements which may either be a\n"
        )
        xml += "         range of blocks or a single block. The 'chksum' attribute\n"
        xml += "         (if present) is the checksum of this blocks range. -->\n"
        xml += "    <BlockMap>\n"
        # pylint: enable=C0301

        self._f_bmap.write(xml)

    def _bmap_file_end(self):
        """
        A helper function which generates the final parts of the block map
        file: the ending tags and the information about the amount of mapped
        blocks.
        """

        xml = "    </BlockMap>\n"
        xml += "</bmap>\n"

        self._f_bmap.write(xml)

        self._f_bmap.seek(self._mapped_count_pos1)
        self._f_bmap.write(
            "%s or %.1f%%" % (self.mapped_size_human, self.mapped_percent)
        )

        self._f_bmap.seek(self._mapped_count_pos2)
        self._f_bmap.write("%u" % self.mapped_cnt)

        self._f_bmap.seek(0)
        hash_obj = hashlib.new(self._cs_type)
        hash_obj.update(self._f_bmap.read().encode())
        chksum = hash_obj.hexdigest()
        self._f_bmap.seek(self._chksum_pos)
        self._f_bmap.write("%s" % chksum)

    def _calculate_chksum(self, first, last):
        """
        A helper function which calculates checksum for the range of blocks of
        the image file: from block 'first' to block 'last'.
        """

        start = first * self.block_size
        end = (last + 1) * self.block_size

        self._f_image.seek(start)
        hash_obj = hashlib.new(self._cs_type)

        chunk_size = 1024 * 1024
        to_read = end - start
        read = 0

        while read < to_read:
            if read + chunk_size > to_read:
                chunk_size = to_read - read
            chunk = self._f_image.read(chunk_size)
            hash_obj.update(chunk)
            read += chunk_size

        return hash_obj.hexdigest()

    def generate(self, include_checksums=True):
        """
        Generate bmap for the image file. If 'include_checksums' is 'True',
        also generate checksums for block ranges.
        """

        # Save image file position in order to restore it at the end
        image_pos = self._f_image.tell()

        self._bmap_file_start()

        # Generate the block map and write it to the XML block map
        # file as we go.
        self.mapped_cnt = 0
        for first, last in self.filemap.get_mapped_ranges(0, self.blocks_cnt):
            self.mapped_cnt += last - first + 1
            if include_checksums:
                chksum = self._calculate_chksum(first, last)
                chksum = ' chksum="%s"' % chksum
            else:
                chksum = ""

            if first != last:
                self._f_bmap.write(
                    "        <Range%s> %s-%s </Range>\n" % (chksum, first, last)
                )
            else:
                self._f_bmap.write("        <Range%s> %s </Range>\n" % (chksum, first))

        self.mapped_size = self.mapped_cnt * self.block_size
        self.mapped_size_human = human_size(self.mapped_size)
        self.mapped_percent = (self.mapped_cnt * 100.0) / self.blocks_cnt

        self._bmap_file_end()

        try:
            self._f_bmap.flush()
        except IOError as err:
            raise Error("cannot flush the bmap file '%s': %s" % (self._bmap_path, err))

        self._f_image.seek(image_pos)
