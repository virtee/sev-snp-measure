#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import hashlib
from .gctx import GCTX
from .ovmf import OVMF
from .sev_hashes import construct_sev_hashes_page
from .vmsa import VMSA
from .sev_mode import SevMode

PAGE_MASK = 0xfff


def add_kernel_hashes(gctx, ovmf, kernel_hash, initrd_hash, cmdline_hash):
    sev_hashes_table_gpa = ovmf.sev_hashes_table_gpa()
    offset = sev_hashes_table_gpa & PAGE_MASK
    sev_hashes_page_gpa = sev_hashes_table_gpa & ~PAGE_MASK
    sev_hashes_page = construct_sev_hashes_page(offset, kernel_hash, initrd_hash, cmdline_hash)
    gctx.update_normal_pages(sev_hashes_page_gpa, sev_hashes_page)


def update_metadata_pages(gctx, ovmf):
    for desc in ovmf.metadata_items():
        if desc.page_type == 1:
            gctx.update_zero_pages(desc.gpa, desc.size)
        elif desc.page_type == 2:
            gctx.update_secrets_page(desc.gpa)
        elif desc.page_type == 3:
            gctx.update_cpuid_page(desc.gpa)


def calc_launch_digest(vcpus: int, ovmf_file: str, kernel: str, initrd: str, append: str):
    ovmf = OVMF(ovmf_file)

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

    gctx = GCTX()
    gctx.update_normal_pages(ovmf.gpa(), ovmf.data())

    if kernel:
        add_kernel_hashes(gctx, ovmf, kernel_hash, initrd_hash, cmdline_hash)

    update_metadata_pages(gctx, ovmf)

    vmsa = VMSA(SevMode.SEV_SNP, ovmf.sev_es_reset_eip())
    for i in range(vcpus):
        if i == 0:
            vmsa_page = vmsa.bytes_bsp()
        else:
            vmsa_page = vmsa.bytes_ap()
        gctx.update_vmsa_page(vmsa_page)

    return gctx.ld()
