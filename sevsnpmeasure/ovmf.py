#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import collections
import struct
import uuid

OvmfSevMetadataDesc = collections.namedtuple('OvmfSevMetadataDesc', ['gpa', 'size', 'page_type'])


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
        offset = int.from_bytes(entry[:4], byteorder='little')
        start = len(self._data)-offset
        metadata_header = self._data[start:start+16]
        # TODO use struct.unpack
        if metadata_header[:4] != b'ASEV':
            raise RuntimeError("Wrong SEV metadata signature")
        metadata_len = int.from_bytes(metadata_header[4:8], byteorder='little')
        _ = int.from_bytes(metadata_header[8:12], byteorder='little')  # metadata version
        num_desc = int.from_bytes(metadata_header[12:16], byteorder='little')
        all_desc_bytes = self._data[start+16:start+metadata_len]
        desc_bytes_size = struct.calcsize("<III")
        for i in range(num_desc):
            desc_bytes = all_desc_bytes[i*desc_bytes_size:(i+1)*desc_bytes_size]
            gpa, size, page_type = struct.unpack("<III", desc_bytes)
            item = OvmfSevMetadataDesc(gpa, size, page_type)
            self._metadata_items.append(item)
