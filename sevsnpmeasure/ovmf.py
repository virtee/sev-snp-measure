#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import ctypes
from ctypes import c_uint8, c_uint32
from enum import Enum
import uuid


# Types of sections declared by OVMF SEV Metadata, as appears in:
# https://github.com/tianocore/edk2/blob/edk2-stable202205/OvmfPkg/ResetVector/X64/OvmfSevMetadata.asm
class SectionType(Enum):
    SNP_SEC_MEM = 1
    SNP_SECRETS = 2
    CPUID = 3


class OvmfSevMetadataSectionDesc(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("gpa", c_uint32),
        ("size", c_uint32),
        ("section_type_int", c_uint32),
    ]

    def section_type(self) -> SectionType:
        return SectionType(self.section_type_int)


class OvmfSevMetadataHeader(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("signature", c_uint8 * 4),
        ("size", c_uint32),
        ("version", c_uint32),
        ("num_items", c_uint32),
    ]

    def verify(self):
        if bytes(self.signature) != b'ASEV':
            raise RuntimeError("Wrong SEV metadata signature")
        if self.version != 1:
            raise RuntimeError("Wrong SEV metadata version")


class OVMF(object):
    FOUR_GB = 0x100000000
    OVMF_TABLE_FOOTER_GUID = "96b582de-1fb2-45f7-baea-a366c55a082d"
    SEV_HASH_TABLE_RV_GUID = "7255371f-3a3b-4b04-927b-1da6efa8d454"
    SEV_ES_RESET_BLOCK_GUID = "00f771de-1a7e-4fcb-890e-68c77e2fb44e"
    OVMF_SEV_META_DATA_GUID = "dc886566-984a-4798-a75e-5585a7bf67cc"

    def __init__(self, _filename: str):
        with open(_filename, "rb") as f:
            self._data = f.read()
        self._parse_footer_table()
        self._parse_sev_metadata()

    def data(self) -> bytes:
        return self._data

    def gpa(self) -> int:
        return self.FOUR_GB - len(self._data)

    def table_item(self, guid: str) -> bytes:
        return self._table[guid]

    def metadata_items(self):
        return self._metadata_items

    def sev_hashes_table_gpa(self) -> int:
        if self.SEV_HASH_TABLE_RV_GUID not in self._table:
            raise RuntimeError("Can't find SEV_HASH_TABLE_RV_GUID entry in OVMF table")
        entry = self._table[self.SEV_HASH_TABLE_RV_GUID]
        return int.from_bytes(entry[:4], byteorder='little')

    def sev_es_reset_eip(self) -> int:
        if self.SEV_ES_RESET_BLOCK_GUID not in self._table:
            raise RuntimeError("Can't find SEV_ES_RESET_BLOCK_GUID entry in OVMF table")
        entry = self._table[self.SEV_ES_RESET_BLOCK_GUID]
        return int.from_bytes(entry[:4], byteorder='little')

    def _parse_footer_table(self) -> None:
        self._table = {}
        size = len(self._data)
        footer_guid = self._data[size-48:size-32]
        expected_footer_guid = uuid.UUID("{" + self.OVMF_TABLE_FOOTER_GUID + "}").bytes_le
        if footer_guid != expected_footer_guid:
            return
        # TODO use struct.unpack
        full_table_size = int.from_bytes(self._data[size-50:size-48], byteorder='little')
        table_size = full_table_size - 16 - 2
        if table_size < 0:
            return
        table_bytes = self._data[size-50-table_size:size-50]
        while len(table_bytes) >= (16 + 2):
            entry_guid = table_bytes[len(table_bytes)-16:]
            entry_size = int.from_bytes(table_bytes[len(table_bytes)-18:len(table_bytes)-16], byteorder='little')
            if entry_size < (16 + 2):
                raise RuntimeError("Invalid entry size")
            entry_data = table_bytes[len(table_bytes)-entry_size:len(table_bytes)-18]
            entry_guid_str = str(uuid.UUID(bytes_le=entry_guid))
            self._table[entry_guid_str] = entry_data
            table_bytes = table_bytes[:len(table_bytes)-entry_size]

    def _parse_sev_metadata(self) -> None:
        self._metadata_items = []
        if self.OVMF_SEV_META_DATA_GUID not in self._table:
            return
        entry = self._table[self.OVMF_SEV_META_DATA_GUID]
        offset_from_end = int.from_bytes(entry[:4], byteorder='little')
        start = len(self._data) - offset_from_end
        header = OvmfSevMetadataHeader.from_buffer_copy(self._data, start)
        header.verify()
        items = self._data[start+ctypes.sizeof(OvmfSevMetadataHeader):start+header.size]
        for i in range(header.num_items):
            offset = i * ctypes.sizeof(OvmfSevMetadataSectionDesc)
            item = OvmfSevMetadataSectionDesc.from_buffer_copy(items, offset)
            self._metadata_items.append(item)
