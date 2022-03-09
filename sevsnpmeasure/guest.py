#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import hashlib
from .gctx import GCTX
from .ovmf import OVMF
from .sev_hashes import construct_sev_hashes_page

PAGE_MASK = 0xfff

def calc_launch_digest(ovmf_file, vmsa_file, kernel, initrd, append):
    ovmf = OVMF(ovmf_file)

    with open(vmsa_file, "rb") as fh:
        vmsa_data = fh.read()

    if kernel:
        with open(kernel, 'rb') as fh:
            kernel_hash = hashlib.sha256(fh.read()).digest()

    if initrd:
        with open(initrd, 'rb') as fh:
            initrd_data = fh.read()
    else:
        initrd_data = b''
    initrd_hash = hashlib.sha256(initrd_data).digest()

    if append:
        cmdline = append.encode() + b'\x00'
    else:
        cmdline = b'\x00'
    cmdline_hash = hashlib.sha256(cmdline).digest()

    if kernel:
        sev_hashes_table_gpa = ovmf.sev_hashes_table_gpa()
        offset = sev_hashes_table_gpa & PAGE_MASK
        sev_hashes_page_gpa = sev_hashes_table_gpa & ~PAGE_MASK
        sev_hashes_page = construct_sev_hashes_page(offset, kernel_hash, initrd_hash, cmdline_hash)

    gctx = GCTX()
    gctx.update_normal_pages(ovmf.gpa(), ovmf.data())
    if kernel:
        gctx.update_normal_pages(sev_hashes_page_gpa, sev_hashes_page)

    for desc in ovmf.metadata_items():
        if desc.page_type == 1:
            gctx.update_zero_pages(desc.gpa, desc.size)
        elif desc.page_type == 2:
            gctx.update_secrets_page(desc.gpa)
        elif desc.page_type == 3:
            gctx.update_cpuid_page(desc.gpa)

    # TODO support more than one vcpu
    gctx.update_vmsa_page(vmsa_data)

    return gctx.ld()
