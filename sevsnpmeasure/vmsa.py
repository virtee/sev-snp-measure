#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import ctypes
from ctypes import c_uint8, c_uint16, c_uint32, c_uint64
from typing import Iterator
from .sev_mode import SevMode
from .vmm_types import VMMType


# VMCB Segment (struct vmcb_seg in the linux kernel)
class VmcbSeg(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("selector", c_uint16),
        ("attrib", c_uint16),
        ("limit", c_uint32),
        ("base", c_uint64),
    ]


# VMSA page
#
# The names of the fields are taken from struct sev_es_work_area in the linux kernel:
# https://github.com/AMDESE/linux/blob/sev-snp-v12/arch/x86/include/asm/svm.h#L318
# (following the definitions in AMD APM Vol 2 Table B-4)
class SevEsSaveArea(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("es", VmcbSeg),
        ("cs", VmcbSeg),
        ("ss", VmcbSeg),
        ("ds", VmcbSeg),
        ("fs", VmcbSeg),
        ("gs", VmcbSeg),
        ("gdtr", VmcbSeg),
        ("ldtr", VmcbSeg),
        ("idtr", VmcbSeg),
        ("tr", VmcbSeg),
        ("vmpl0_ssp", c_uint64),
        ("vmpl1_ssp", c_uint64),
        ("vmpl2_ssp", c_uint64),
        ("vmpl3_ssp", c_uint64),
        ("u_cet", c_uint64),
        ("reserved_1", c_uint8 * 2),
        ("vmpl", c_uint8),
        ("cpl", c_uint8),
        ("reserved_2", c_uint8 * 4),
        ("efer", c_uint64),
        ("reserved_3", c_uint8 * 104),
        ("xss", c_uint64),
        ("cr4", c_uint64),
        ("cr3", c_uint64),
        ("cr0", c_uint64),
        ("dr7", c_uint64),
        ("dr6", c_uint64),
        ("rflags", c_uint64),
        ("rip", c_uint64),
        ("dr0", c_uint64),
        ("dr1", c_uint64),
        ("dr2", c_uint64),
        ("dr3", c_uint64),
        ("dr0_addr_mask", c_uint64),
        ("dr1_addr_mask", c_uint64),
        ("dr2_addr_mask", c_uint64),
        ("dr3_addr_mask", c_uint64),
        ("reserved_4", c_uint8 * 24),
        ("rsp", c_uint64),
        ("s_cet", c_uint64),
        ("ssp", c_uint64),
        ("isst_addr", c_uint64),
        ("rax", c_uint64),
        ("star", c_uint64),
        ("lstar", c_uint64),
        ("cstar", c_uint64),
        ("sfmask", c_uint64),
        ("kernel_gs_base", c_uint64),
        ("sysenter_cs", c_uint64),
        ("sysenter_esp", c_uint64),
        ("sysenter_eip", c_uint64),
        ("cr2", c_uint64),
        ("reserved_5", c_uint8 * 32),
        ("g_pat", c_uint64),
        ("dbgctrl", c_uint64),
        ("br_from", c_uint64),
        ("br_to", c_uint64),
        ("last_excp_from", c_uint64),
        ("last_excp_to", c_uint64),
        ("reserved_7", c_uint8 * 80),
        ("pkru", c_uint32),
        ("reserved_8", c_uint8 * 20),
        ("reserved_9", c_uint64),
        ("rcx", c_uint64),
        ("rdx", c_uint64),
        ("rbx", c_uint64),
        ("reserved_10", c_uint64),
        ("rbp", c_uint64),
        ("rsi", c_uint64),
        ("rdi", c_uint64),
        ("r8", c_uint64),
        ("r9", c_uint64),
        ("r10", c_uint64),
        ("r11", c_uint64),
        ("r12", c_uint64),
        ("r13", c_uint64),
        ("r14", c_uint64),
        ("r15", c_uint64),
        ("reserved_11", c_uint8 * 16),
        ("guest_exit_info_1", c_uint64),
        ("guest_exit_info_2", c_uint64),
        ("guest_exit_int_info", c_uint64),
        ("guest_nrip", c_uint64),
        ("sev_features", c_uint64),
        ("vintr_ctrl", c_uint64),
        ("guest_exit_code", c_uint64),
        ("virtual_tom", c_uint64),
        ("tlb_id", c_uint64),
        ("pcpu_id", c_uint64),
        ("event_inj", c_uint64),
        ("xcr0", c_uint64),
        ("reserved_12", c_uint8 * 16),
        ("x87_dp", c_uint64),
        ("mxcsr", c_uint32),
        ("x87_ftw", c_uint16),
        ("x87_fsw", c_uint16),
        ("x87_fcw", c_uint16),
        ("x87_fop", c_uint16),
        ("x87_ds", c_uint16),
        ("x87_cs", c_uint16),
        ("x87_rip", c_uint64),
        ("fpreg_x87", c_uint8 * 80),
        ("fpreg_xmm", c_uint8 * 256),
        ("fpreg_ymm", c_uint8 * 256),
        ("unused", c_uint8 * 2448),
    ]


class VMSA(object):
    BSP_EIP = 0xfffffff0

    @staticmethod
    def build_save_area(eip: int, sev_features: int, vcpu_sig: int, vmm_type: VMMType = VMMType.QEMU):
        # QEMU and EC2 differ slightly on initial register state
        if vmm_type == VMMType.QEMU:
            cs_flags = 0x9b
            ss_flags = 0x93
            tr_flags = 0x8b
            rdx = vcpu_sig
        elif vmm_type == VMMType.ec2:
            cs_flags = 0x9b
            if eip == 0xfffffff0:
                cs_flags = 0x9a
            ss_flags = 0x92
            tr_flags = 0x83
            rdx = 0
        else:
            raise ValueError("unknown VMM type")

        return SevEsSaveArea(
            es=VmcbSeg(0, 0x93, 0xffff, 0),
            cs=VmcbSeg(0xf000, cs_flags, 0xffff, eip & 0xffff0000),
            ss=VmcbSeg(0, ss_flags, 0xffff, 0),
            ds=VmcbSeg(0, 0x93, 0xffff, 0),
            fs=VmcbSeg(0, 0x93, 0xffff, 0),
            gs=VmcbSeg(0, 0x93, 0xffff, 0),
            gdtr=VmcbSeg(0, 0, 0xffff, 0),
            idtr=VmcbSeg(0, 0, 0xffff, 0),
            ldtr=VmcbSeg(0, 0x82, 0xffff, 0),
            tr=VmcbSeg(0, tr_flags, 0xffff, 0),
            efer=0x1000,  # KVM enables EFER_SVME
            cr4=0x40,     # KVM enables X86_CR4_MCE
            cr0=0x10,
            dr7=0x400,
            dr6=0xffff0ff0,
            rflags=0x2,
            rip=eip & 0xffff,
            g_pat=0x7040600070406,  # PAT MSR: See AMD APM Vol 2, Section A.3
            rdx=rdx,
            sev_features=sev_features,
            xcr0=0x1,
        )

    def __init__(self, sev_mode: SevMode, ap_eip: int, vcpu_sig: int, vmm_type: VMMType = VMMType.QEMU):
        if sev_mode == SevMode.SEV_SNP:
            sev_features = 0x1
        else:
            sev_features = 0x0

        self.bsp_save_area = VMSA.build_save_area(self.BSP_EIP, sev_features, vcpu_sig, vmm_type)
        if ap_eip:
            self.ap_save_area = VMSA.build_save_area(ap_eip, sev_features, vcpu_sig, vmm_type)

    def pages(self, vcpus: int) -> Iterator[bytes]:
        """
        Generate VMSA pages
        """
        for i in range(vcpus):
            if i == 0:
                yield bytes(self.bsp_save_area)
            else:
                yield bytes(self.ap_save_area)


class VMSA_SVSM(object):
    BSP_EIP = 0xfffffff0

    @staticmethod
    def build_save_area(eip: int, sev_features: int, vcpu_sig: int, vmm_type: VMMType = VMMType.QEMU):
        return SevEsSaveArea(
            es=VmcbSeg(16, 0xc93, 0xffffffff, 0),
            cs=VmcbSeg(8, 0xc9b, 0xffffffff, 0),
            ss=VmcbSeg(16, 0xc93, 0xffffffff, 0),
            ds=VmcbSeg(16, 0xc93, 0xffffffff, 0),
            fs=VmcbSeg(16, 0xc93, 0xffffffff, 0),
            gs=VmcbSeg(0, 0x093, 0xffff, 0),
            gdtr=VmcbSeg(0, 0, 0xffff, 0),
            idtr=VmcbSeg(0, 0, 0xffff, 0),
            ldtr=VmcbSeg(0, 0x82, 0xffff, 0),
            tr=VmcbSeg(0, 0x8b, 0xffff, 0),
            efer=0x1000,
            cr4=0x40,
            cr0=0x11,
            dr7=0x400,
            dr6=0xffff0ff0,
            rflags=0x2,
            rip=eip,
            g_pat=0x7040600070406,  # PAT MSR: See AMD APM Vol 2, Section A.3
            rdx=vcpu_sig,
            sev_features=sev_features,
            xcr0=0x1,
        )

    def __init__(self, ap_eip: int, vcpu_sig: int, vmm_type: VMMType = VMMType.QEMU):
        sev_features = 0x1
        self.save_area = VMSA_SVSM.build_save_area(ap_eip, sev_features, vcpu_sig, vmm_type)

    def pages(self, vcpus: int) -> Iterator[bytes]:
        """
        Generate VMSA pages
        """
        for i in range(vcpus):
            yield bytes(self.save_area)
