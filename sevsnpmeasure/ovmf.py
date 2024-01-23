#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import ctypes
from ctypes import c_uint8, c_uint16, c_uint32
from enum import Enum
import uuid

FOUR_GB = 0x100000000


# Types of sections declared by OVMF SEV Metadata, as appears in:
# https://github.com/tianocore/edk2/blob/edk2-stable202205/OvmfPkg/ResetVector/X64/OvmfSevMetadata.asm
class SectionType(Enum):
    SNP_SEC_MEM = 1
    SNP_SECRETS = 2
    CPUID = 3
    SNP_KERNEL_HASHES = 0x10


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


class OvmfFooterTableEntry(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("size", c_uint16),
        ("guid", c_uint8 * 16),
    ]


class OVMF(object):
    OVMF_TABLE_FOOTER_GUID = "96b582de-1fb2-45f7-baea-a366c55a082d"
    SEV_HASH_TABLE_RV_GUID = "7255371f-3a3b-4b04-927b-1da6efa8d454"
    SEV_ES_RESET_BLOCK_GUID = "00f771de-1a7e-4fcb-890e-68c77e2fb44e"
    OVMF_SEV_META_DATA_GUID = "dc886566-984a-4798-a75e-5585a7bf67cc"

    def __init__(self, _filename: str, end_at: int = FOUR_GB):
        with open(_filename, "rb") as f:
            self._data = f.read()
        self._parse_footer_table()
        self._parse_sev_metadata()
        self._gpa = end_at - len(self._data)

    def data(self) -> bytes:
        return self._data

    def size(self) -> int:
        return len(self._data)

    def end_gpa(self) -> int:
        return self.gpa() + self.size()

    def gpa(self) -> int:
        return self._gpa

    def table_item(self, guid: str) -> bytes:
        return self._table[guid]

    def metadata_items(self):
        return self._metadata_items

    def has_metadata_section(self, section_type: SectionType) -> bool:
        return any(True for s in self.metadata_items() if s.section_type() == section_type)

    def is_sev_hashes_table_supported(self) -> bool:
        return self.SEV_HASH_TABLE_RV_GUID in self._table and self.sev_hashes_table_gpa() != 0

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
        entry_header_size = ctypes.sizeof(OvmfFooterTableEntry)
        # The OVMF table ends 32 bytes before the end of the firmware binary
        start_of_footer_table = size - 32 - entry_header_size
        footer = OvmfFooterTableEntry.from_buffer_copy(self._data[start_of_footer_table:])
        expected_footer_guid = uuid.UUID("{" + self.OVMF_TABLE_FOOTER_GUID + "}").bytes_le
        if bytes(footer.guid) != expected_footer_guid:
            return
        table_size = footer.size - entry_header_size
        if table_size < 0:
            return
        table_bytes = self._data[start_of_footer_table-table_size:start_of_footer_table]
        while len(table_bytes) >= entry_header_size:
            entry = OvmfFooterTableEntry.from_buffer_copy(table_bytes[-entry_header_size:])
            if entry.size < entry_header_size:
                raise RuntimeError("Invalid entry size")
            entry_guid_str = str(uuid.UUID(bytes_le=bytes(entry.guid)))
            entry_data = table_bytes[-entry.size:-entry_header_size]
            self._table[entry_guid_str] = entry_data
            table_bytes = table_bytes[:-entry.size]

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


class SVSM(OVMF):
    SVSM_INFO_GUID = "a789a612-0597-4c4b-a49f-cbb1fe9d1ddd"

    def sev_es_reset_eip(self) -> int:
        # See https://github.com/coconut-svsm/qemu/blob/0e64fb84eeeb86e2b263068c098a64d2f3d5a661/target/i386/sev.c#L2175

        if self.SVSM_INFO_GUID not in self._table:
            raise RuntimeError("Can't find SVSM_INFO_GUID entry in SVSM table")
        entry = self._table[self.SVSM_INFO_GUID]
        return int.from_bytes(entry[:4], byteorder='little') + self.gpa()
