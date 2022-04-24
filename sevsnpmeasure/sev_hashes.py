#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import hashlib
import uuid


def guid_to_le(guid_str):
    return uuid.UUID("{" + guid_str + "}").bytes_le


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
    def construct_table(self):
        # TODO use struct.pack
        entries = 3
        ht_len = 16 + 2 + entries * (16 + 2 + 32)
        ht_len_aligned = (ht_len + 15) & ~15
        ht = bytearray(ht_len_aligned)

        # Table header
        ht[0:16] = guid_to_le(self.SEV_HASH_TABLE_HEADER_GUID)
        ht[16:18] = ht_len.to_bytes(2, byteorder='little')

        # Entry 0: kernel command-line
        e = 18
        ht[e:e+16] = guid_to_le(self.SEV_CMDLINE_ENTRY_GUID)
        ht[e+16:e+18] = (16 + 2 + 32).to_bytes(2, byteorder='little')
        ht[e+18:e+18+32] = self.cmdline_hash

        # Entry 1: initrd
        e = e+18+32
        ht[e:e+16] = guid_to_le(self.SEV_INITRD_ENTRY_GUID)
        ht[e+16:e+18] = (16 + 2 + 32).to_bytes(2, byteorder='little')
        ht[e+18:e+18+32] = self.initrd_hash

        # Entry 2: kernel
        e = e+18+32
        ht[e:e+16] = guid_to_le(self.SEV_KERNEL_ENTRY_GUID)
        ht[e+16:e+18] = (16 + 2 + 32).to_bytes(2, byteorder='little')
        ht[e+18:e+18+32] = self.kernel_hash

        return ht

    def construct_page(self, offset):
        assert offset < 4096
        hashes_table = self.construct_table()
        page = bytes(offset) + hashes_table + bytes(4096 - offset - len(hashes_table))
        assert len(page) == 4096
        return page
