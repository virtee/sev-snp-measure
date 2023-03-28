#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import hashlib

LD_SIZE = hashlib.sha384().digest_size
ZEROS = bytes(LD_SIZE)


def le8(n: int) -> bytes:
    return n.to_bytes(1, byteorder='little')


def le16(n: int) -> bytes:
    return n.to_bytes(2, byteorder='little')


def le32(n: int) -> bytes:
    return n.to_bytes(4, byteorder='little')


def le64(n: int) -> bytes:
    return n.to_bytes(8, byteorder='little')


def sha384(buf: bytes) -> bytes:
    return hashlib.sha384(buf).digest()


class GCTX(object):
    """
    SNP Guest Context
    """

    # VMSA page is recorded in the RMP table with GPA (u64)(-1).
    # However, the address is page-aligned, and also all the bits above
    # 51 are cleared.
    VMSA_GPA = 0xFFFFFFFFF000

    def __init__(self, seed: bytes = ZEROS):
        self._ld = seed

    def ld(self) -> bytes:
        return self._ld

    def hex_ld(self) -> str:
        return self._ld.hex()

    def _update(self, page_type, gpa, contents):
        assert len(contents) == LD_SIZE
        page_info_len = 0x70
        is_imi = 0
        vmpl3_perms = vmpl2_perms = vmpl1_perms = 0
        # SNP spec 8.17.2 Table 67 Layout of the PAGE_INFO structure
        page_info = self._ld + contents
        page_info += le16(page_info_len) + le8(page_type) + le8(is_imi)
        page_info += le8(vmpl3_perms) + le8(vmpl2_perms) + le8(vmpl1_perms) + le8(0)
        page_info += le64(gpa)
        assert len(page_info) == page_info_len
        # Update the launch digest
        self._ld = sha384(page_info)

    def update_normal_pages(self, start_gpa, data):
        assert len(data) % 4096 == 0
        offset = 0
        while offset < len(data):
            page_data = data[offset:offset+4096]
            self._update(0x01, start_gpa + offset, sha384(page_data))
            offset += 4096

    def update_vmsa_page(self, data):
        assert len(data) == 4096
        self._update(0x02, self.VMSA_GPA, sha384(data))

    def update_zero_pages(self, gpa, length_bytes):
        assert length_bytes % 4096 == 0
        offset = 0
        while offset < length_bytes:
            self._update(0x03, gpa + offset, ZEROS)
            offset += 4096

    def update_unmeasured_page(self, gpa):
        self._update(0x04, gpa, ZEROS)

    def update_secrets_page(self, gpa):
        self._update(0x05, gpa, ZEROS)

    def update_cpuid_page(self, gpa):
        self._update(0x06, gpa, ZEROS)
