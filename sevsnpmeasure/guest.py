#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import hashlib

from .gctx import GCTX
from .ovmf import OVMF
from .sev_hashes import SevHashes
from .vmsa import VMSA
from .sev_mode import SevMode

PAGE_MASK = 0xfff


def calc_launch_digest(mode: SevMode, vcpus: int, vcpu_sig: int, ovmf_file: str,
                       kernel: str, initrd: str, append: str) -> bytes:
    if mode == SevMode.SEV_SNP:
        return snp_calc_launch_digest(vcpus, vcpu_sig, ovmf_file, kernel, initrd, append)
    elif mode == SevMode.SEV_ES:
        return seves_calc_launch_digest(vcpus, vcpu_sig, ovmf_file, kernel, initrd, append)
    elif mode == SevMode.SEV:
        return sev_calc_launch_digest(ovmf_file, kernel, initrd, append)
    else:
        raise ValueError("unknown mode")


def snp_update_metadata_pages(gctx, ovmf) -> None:
    for desc in ovmf.metadata_items():
        if desc.page_type == 1:
            gctx.update_zero_pages(desc.gpa, desc.size)
        elif desc.page_type == 2:
            gctx.update_secrets_page(desc.gpa)
        elif desc.page_type == 3:
            gctx.update_cpuid_page(desc.gpa)


def snp_calc_launch_digest(vcpus: int, vcpu_sig: int, ovmf_file: str, kernel: str, initrd: str, append: str) -> bytes:
    ovmf = OVMF(ovmf_file)

    gctx = GCTX()
    gctx.update_normal_pages(ovmf.gpa(), ovmf.data())

    if kernel:
        sev_hashes_table_gpa = ovmf.sev_hashes_table_gpa()
        offset_in_page = sev_hashes_table_gpa & PAGE_MASK
        sev_hashes_page_gpa = sev_hashes_table_gpa & ~PAGE_MASK
        sev_hashes = SevHashes(kernel, initrd, append)
        sev_hashes_page = sev_hashes.construct_page(offset_in_page)
        gctx.update_normal_pages(sev_hashes_page_gpa, sev_hashes_page)

    snp_update_metadata_pages(gctx, ovmf)

    vmsa = VMSA(SevMode.SEV_SNP, ovmf.sev_es_reset_eip(), vcpu_sig)
    for vmsa_page in vmsa.pages(vcpus):
        gctx.update_vmsa_page(vmsa_page)

    return gctx.ld()


def seves_calc_launch_digest(vcpus: int, vcpu_sig: int, ovmf_file: str, kernel: str, initrd: str, append: str) -> bytes:
    ovmf = OVMF(ovmf_file)
    launch_hash = hashlib.sha256(ovmf.data())
    if kernel:
        sev_hashes_table = SevHashes(kernel, initrd, append).construct_table()
        launch_hash.update(sev_hashes_table)
    vmsa = VMSA(SevMode.SEV_ES, ovmf.sev_es_reset_eip(), vcpu_sig)
    for vmsa_page in vmsa.pages(vcpus):
        launch_hash.update(vmsa_page)
    return launch_hash.digest()


def sev_calc_launch_digest(ovmf_file: str, kernel: str, initrd: str, append: str) -> bytes:
    ovmf = OVMF(ovmf_file)
    launch_hash = hashlib.sha256(ovmf.data())
    if kernel:
        sev_hashes_table = SevHashes(kernel, initrd, append).construct_table()
        launch_hash.update(sev_hashes_table)
    return launch_hash.digest()
