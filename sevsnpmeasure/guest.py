#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import hashlib
from typing import Optional

from .gctx import GCTX
from .ovmf import OVMF, SectionType, OvmfSevMetadataSectionDesc
from .sev_hashes import SevHashes
from .vmsa import VMSA
from .sev_mode import SevMode
from .vmm_types import VMMType

PAGE_MASK = 0xfff


def calc_launch_digest(mode: SevMode, vcpus: int, vcpu_sig: int, ovmf_file: str,
                       kernel: str, initrd: str, append: str, snp_ovmf_hash_str: str = '',
                       vmm_type: VMMType = VMMType.QEMU) -> bytes:
    if snp_ovmf_hash_str and mode != SevMode.SEV_SNP:
        raise ValueError("SNP OVMF hash only works with SNP")

    if mode == SevMode.SEV_SNP:
        return snp_calc_launch_digest(vcpus, vcpu_sig, ovmf_file, kernel, initrd, append, snp_ovmf_hash_str, vmm_type)
    elif mode == SevMode.SEV_ES:
        return seves_calc_launch_digest(vcpus, vcpu_sig, ovmf_file, kernel, initrd, append, vmm_type=vmm_type)
    elif mode == SevMode.SEV:
        return sev_calc_launch_digest(ovmf_file, kernel, initrd, append)
    else:
        raise ValueError("unknown mode")


def snp_update_kernel_hashes(gctx: GCTX, ovmf: OVMF, sev_hashes: Optional[SevHashes], gpa: int, size: int) -> None:
    if sev_hashes:
        sev_hashes_table_gpa = ovmf.sev_hashes_table_gpa()
        offset_in_page = sev_hashes_table_gpa & PAGE_MASK
        sev_hashes_page = sev_hashes.construct_page(offset_in_page)
        assert size == len(sev_hashes_page)
        gctx.update_normal_pages(gpa, sev_hashes_page)
    else:
        gctx.update_zero_pages(gpa, size)


def snp_update_section(desc: OvmfSevMetadataSectionDesc, gctx: GCTX, ovmf: OVMF,
                       sev_hashes: Optional[SevHashes], vmm_type: VMMType) -> None:
    if desc.section_type() == SectionType.SNP_SEC_MEM:
        gctx.update_zero_pages(desc.gpa, desc.size)
    elif desc.section_type() == SectionType.SNP_SECRETS:
        gctx.update_secrets_page(desc.gpa)
    elif desc.section_type() == SectionType.CPUID:
        if not vmm_type == VMMType.ec2:
            gctx.update_cpuid_page(desc.gpa)
    elif desc.section_type() == SectionType.SNP_KERNEL_HASHES:
        snp_update_kernel_hashes(gctx, ovmf, sev_hashes, desc.gpa, desc.size)
    else:
        raise ValueError("unknown OVMF metadata section type")


def snp_update_metadata_pages(gctx: GCTX, ovmf: OVMF, sev_hashes: Optional[SevHashes], vmm_type: VMMType) -> None:
    for desc in ovmf.metadata_items():
        snp_update_section(desc, gctx, ovmf, sev_hashes, vmm_type)

    if vmm_type == VMMType.ec2:
        for desc in ovmf.metadata_items():
            if desc.section_type() == SectionType.CPUID:
                gctx.update_cpuid_page(desc.gpa)

    if sev_hashes is not None and not ovmf.has_metadata_section(SectionType.SNP_KERNEL_HASHES):
        raise RuntimeError("Kernel specified but OVMF metadata doesn't include SNP_KERNEL_HASHES section")


def calc_snp_ovmf_hash(ovmf_file: str) -> bytes:
    ovmf = OVMF(ovmf_file)

    gctx = GCTX()
    gctx.update_normal_pages(ovmf.gpa(), ovmf.data())
    return gctx.ld()


def snp_calc_launch_digest(vcpus: int, vcpu_sig: int, ovmf_file: str,
                           kernel: str, initrd: str, append: str, ovmf_hash_str: str,
                           vmm_type: VMMType = VMMType.QEMU) -> bytes:

    gctx = GCTX()
    ovmf = OVMF(ovmf_file)

    # Allow users to provide a precalculated OVMF hash.
    # Ignores the contents of the OVMF file in front of us.
    if ovmf_hash_str:
        ovmf_hash = bytearray.fromhex(ovmf_hash_str)
        gctx = GCTX(seed=ovmf_hash)
    else:
        gctx.update_normal_pages(ovmf.gpa(), ovmf.data())

    sev_hashes = None
    if kernel:
        sev_hashes = SevHashes(kernel, initrd, append)

    snp_update_metadata_pages(gctx, ovmf, sev_hashes, vmm_type)

    vmsa = VMSA(SevMode.SEV_SNP, ovmf.sev_es_reset_eip(), vcpu_sig, vmm_type)
    for vmsa_page in vmsa.pages(vcpus):
        gctx.update_vmsa_page(vmsa_page)

    return gctx.ld()


def seves_calc_launch_digest(vcpus: int, vcpu_sig: int, ovmf_file: str, kernel: str, initrd: str, append: str,
                             vmm_type: VMMType = VMMType.QEMU) -> bytes:
    ovmf = OVMF(ovmf_file)
    launch_hash = hashlib.sha256(ovmf.data())
    if kernel:
        if not ovmf.is_sev_hashes_table_supported():
            raise RuntimeError("Kernel specified but OVMF doesn't support kernel/initrd/cmdline measurement")
        sev_hashes_table = SevHashes(kernel, initrd, append).construct_table()
        launch_hash.update(sev_hashes_table)
    vmsa = VMSA(SevMode.SEV_ES, ovmf.sev_es_reset_eip(), vcpu_sig, vmm_type)
    for vmsa_page in vmsa.pages(vcpus):
        launch_hash.update(vmsa_page)
    return launch_hash.digest()


def sev_calc_launch_digest(ovmf_file: str, kernel: str, initrd: str, append: str) -> bytes:
    ovmf = OVMF(ovmf_file)
    launch_hash = hashlib.sha256(ovmf.data())
    if kernel:
        if not ovmf.is_sev_hashes_table_supported():
            raise RuntimeError("Kernel specified but OVMF doesn't support kernel/initrd/cmdline measurement")
        sev_hashes_table = SevHashes(kernel, initrd, append).construct_table()
        launch_hash.update(sev_hashes_table)
    return launch_hash.digest()
