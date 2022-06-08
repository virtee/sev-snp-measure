#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import ctypes
from ctypes import c_uint8, c_uint16
import hashlib
import uuid


Sha256Hash = c_uint8 * hashlib.sha256().digest_size


class GuidLe(ctypes.Array):
    _length_ = 16
    _type_ = c_uint8

    @staticmethod
    def from_str(guid_str: str):
        return GuidLe.from_buffer_copy(uuid.UUID("{" + guid_str + "}").bytes_le)


class SevHashTableEntry(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("guid", GuidLe),
        ("length", c_uint16),
        ("hash", Sha256Hash),
    ]


class SevHashTable(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("guid", GuidLe),
        ("length", c_uint16),
        ("cmdline", SevHashTableEntry),
        ("initrd", SevHashTableEntry),
        ("kernel", SevHashTableEntry),
    ]


class PaddedSevHashTable(ctypes.LittleEndianStructure):
    _PADDING_SIZE = ((ctypes.sizeof(SevHashTable) + 15) & ~15) - ctypes.sizeof(SevHashTable)
    _pack_ = 1
    _fields_ = [
        ("ht", SevHashTable),
        ("padding", c_uint8 * _PADDING_SIZE),
    ]


class SevHashes:
    SEV_HASH_TABLE_HEADER_GUID = "9438d606-4f22-4cc9-b479-a793d411fd21"

    SEV_KERNEL_ENTRY_GUID = "4de79437-abd2-427f-b835-d5b172d2045b"
    SEV_INITRD_ENTRY_GUID = "44baf731-3a2f-4bd7-9af1-41e29169781d"
    SEV_CMDLINE_ENTRY_GUID = "97d02dd8-bd20-4c94-aa78-e7714d36ab2a"

    def __init__(self, kernel: str, initrd: str, append: str):
        with open(kernel, 'rb') as fh:
            self.kernel_hash = hashlib.sha256(fh.read()).digest()

        if initrd:
            with open(initrd, 'rb') as fh:
                initrd_data = fh.read()
        else:
            initrd_data = b''
        self.initrd_hash = hashlib.sha256(initrd_data).digest()

        if append:
            cmdline = append.encode() + b'\x00'
        else:
            cmdline = b'\x00'
        self.cmdline_hash = hashlib.sha256(cmdline).digest()

    #
    # Generate the SEV hashes area - this must be *identical* to the way QEMU
    # generates this info in order for the measurement to match.
    #
    def construct_table(self) -> bytes:
        padded_ht = PaddedSevHashTable(
            ht=SevHashTable(
                guid=GuidLe.from_str(self.SEV_HASH_TABLE_HEADER_GUID),
                length=ctypes.sizeof(SevHashTable),
                cmdline=SevHashTableEntry(
                    guid=GuidLe.from_str(self.SEV_CMDLINE_ENTRY_GUID),
                    length=ctypes.sizeof(SevHashTableEntry),
                    hash=Sha256Hash.from_buffer_copy(self.cmdline_hash),
                ),
                initrd=SevHashTableEntry(
                    guid=GuidLe.from_str(self.SEV_INITRD_ENTRY_GUID),
                    length=ctypes.sizeof(SevHashTableEntry),
                    hash=Sha256Hash.from_buffer_copy(self.initrd_hash),
                ),
                kernel=SevHashTableEntry(
                    guid=GuidLe.from_str(self.SEV_KERNEL_ENTRY_GUID),
                    length=ctypes.sizeof(SevHashTableEntry),
                    hash=Sha256Hash.from_buffer_copy(self.kernel_hash),
                ),
            )
        )
        return bytes(padded_ht)

    def construct_page(self, offset: int) -> bytes:
        assert offset < 4096
        hashes_table = self.construct_table()
        page = bytes(offset) + hashes_table + bytes(4096 - offset - len(hashes_table))
        assert len(page) == 4096
        return page
