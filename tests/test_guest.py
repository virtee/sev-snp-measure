#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from sevsnpmeasure import guest
from sevsnpmeasure import vcpu_types
from sevsnpmeasure import vmm_types
from sevsnpmeasure.sev_mode import SevMode
import pathlib
import tempfile
import contextlib
import os


class TestGuest(unittest.TestCase):

    # Test of we can generate a good OVMF hash
    def test_snp_ovmf_hash_gen_default(self):
        ovmf_hash = 'cab7e085874b3acfdbe2d96dcaa3125111f00c35c6fc9708464c2ae74bfdb048a198cb9a9ccae0b3e5e1a33f5f249819'
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                0x21,
                snp_ovmf_hash_str=ovmf_hash)
        self.assertEqual(
                ld.hex(),
                'aa6f24465c304e3ad553a18069510996fc92a84f48ae2140'
                'cb95dfbd422cdb14087588fb6eec89ef0a65e6d376d9a300')

    def test_snp_ovmf_hash_gen_feature_snp_only(self):
        ovmf_hash = 'cab7e085874b3acfdbe2d96dcaa3125111f00c35c6fc9708464c2ae74bfdb048a198cb9a9ccae0b3e5e1a33f5f249819'
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                0x1,
                snp_ovmf_hash_str=ovmf_hash)
        self.assertEqual(
                ld.hex(),
                '3c018b826531c5f625f10004d51ee51ab5dbfaf1fdd79998'
                'ab649cff11b4afbdb2f50941d2a23b5d77fe00cf988242e7')

    # Test of we can a full LD from the OVMF hash
    def test_snp_ovmf_hash_full_default(self):
        ovmf_hash = guest.calc_snp_ovmf_hash("tests/fixtures/ovmf_AmdSev_suffix.bin").hex()
        self.assertEqual(
                ovmf_hash,
                'edcf6d1c57ce868a167c990f58c8667c698269ef9e080324'
                '6419eea914186343054d557e1f17acd93b032c106bc70d25')

        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "console=ttyS0 loglevel=7",
                0x21,
                snp_ovmf_hash_str=ovmf_hash)
        self.assertEqual(
                ld.hex(),
                '2b9ca4d24c46845280fdca6f0ca0edf0f704bf179243e5c1'
                'b139acf3668ce7bc040e12d16b2ee8738aeaa39faddc8912')

    def test_snp_ovmf_hash_full_feature_snp_only(self):
        ovmf_hash = guest.calc_snp_ovmf_hash("tests/fixtures/ovmf_AmdSev_suffix.bin").hex()
        self.assertEqual(
                ovmf_hash,
                'edcf6d1c57ce868a167c990f58c8667c698269ef9e080324'
                '6419eea914186343054d557e1f17acd93b032c106bc70d25')

        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "console=ttyS0 loglevel=7",
                0x1,
                snp_ovmf_hash_str=ovmf_hash)
        self.assertEqual(
                ld.hex(),
                '72b3f3c1ed0df9e5279eb2317a9861be3b878537e8513b31'
                '8b49c1e184f6228e3ff367d133a8688f430e412ba66f558f'
            )

    def test_snp_ec2_default(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                0x21,
                vmm_type=vmm_types.VMMType.ec2)
        self.assertEqual(
                ld.hex(),
                'cd4a4690a1f679ac8f3d6e446aab8d0061d535cc94615d98'
                'c7d7dbe4b16dbceeaf7fc7944e7874b202e27041f179e7e6')

    def test_snp_ec2_feature_snp_only(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                0x1,
                vmm_type=vmm_types.VMMType.ec2)
        self.assertEqual(
                ld.hex(),
                '760b6e51039d2d6c1fc6d38ca5c387967d158e0294883e45'
                '22c36f89bd61bfc9cdb975cd1ceedffbe1b23b1daf4e3f42')

    def test_snp_default(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "console=ttyS0 loglevel=7",
                0x21)
        self.assertEqual(
                ld.hex(),
                '2b9ca4d24c46845280fdca6f0ca0edf0f704bf179243e5c1'
                'b139acf3668ce7bc040e12d16b2ee8738aeaa39faddc8912')

    def test_snp_guest_feature_snp_only(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "console=ttyS0 loglevel=7",
                0x1)
        self.assertEqual(
                ld.hex(),
                '72b3f3c1ed0df9e5279eb2317a9861be3b878537e8513b31'
                '8b49c1e184f6228e3ff367d133a8688f430e412ba66f558f')

    def test_snp_without_kernel_default(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                None,
                None,
                None,
                0x21)
        self.assertEqual(
                ld.hex(),
                'd35ca073e73701aa476d9d1b2feeee9efd935b7ec9dc43a0'
                '105857f506addb48ba3a1d443e5c10db430ad1a436ac5b2c')

    def test_snp_without_kernel_feature_snp_only(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                None,
                None,
                None,
                0x1)
        self.assertEqual(
                ld.hex(),
                'c4ee889e2ca38dc7137f5a448c56960a1eb5c08919fd2107'
                'a1249eb899afda42be9ba11e417530938cfa8d62a5890557')

    def test_snp_with_multiple_vcpus_default(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                4,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                0x21)
        self.assertEqual(
                ld.hex(),
                '6258fc4d3c60d6964de64811587a903f309b9391efdccd44'
                '8bb8bc39b78c1d153378077ca37e32d06d6ead319a5c7bce')

    def test_snp_with_multiple_vcpus_feature_snp_only(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                4,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                0x1)
        self.assertEqual(
                ld.hex(),
                '74b2f532253c8214df9998ba8df305aa98eb1733c0010014'
                'c5ed728b8d1a9fa83df0a0caf047e9cee14087cc79bbc7c9')

    def test_snp_with_ovmfx64_without_default(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_OvmfX64_suffix.bin",
                None,
                None,
                None,
                0x21)
        self.assertEqual(
                ld.hex(),
                '7b30bdd3f3124ccfceaa882f4b3ab2ff3641bb421bb9bc6d'
                'f6b9be0d8ecde33e6fba86505808ab5257e3e620a2006e53')

    def test_snp_with_ovmfx64_without_kernel_feature_snp_only(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_OvmfX64_suffix.bin",
                None,
                None,
                None,
                0x1)
        self.assertEqual(
                ld.hex(),
                '6ea57de00ffc6f159c6b799f9c053cd165a021efed161467'
                '8b1a0ae24c6b0374387f52ace64e0fbc08d1129a857a0b0c')

    def test_snp_with_ovmfx64_and_kernel_should_fail(self):
        with self.assertRaises(RuntimeError) as c:
            guest.calc_launch_digest(
                    SevMode.SEV_SNP,
                    1,
                    vcpu_types.CPU_SIGS["EPYC-v4"],
                    "tests/fixtures/ovmf_OvmfX64_suffix.bin",
                    "/dev/null",
                    "/dev/null",
                    "",
                    0x21)
        self.assertEqual(str(c.exception),
                         "Kernel specified but OVMF metadata doesn't include SNP_KERNEL_HASHES section")

    def test_seves(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_ES,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                0x1)
        self.assertEqual(
                ld.hex(),
                'c9c378be09902e3d5927a93b73ed383620eea5387e1d16416807cfc949b7f834')

    def test_seves_with_multiple_vcpus(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_ES,
                4,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                0x21)
        self.assertEqual(
                ld.hex(),
                '2806971adf7a9d5bdef59d007f0200af685dec6721781fe1d6efa9236b3361f1')

    def test_seves_dump_vmsa(self):
        """Test that SEV-ES mode creates vmsa files if requrested."""
        fixtures_dir = pathlib.Path('tests/fixtures').absolute()
        with tempfile.TemporaryDirectory() as tmp:
            with push_dir(tmp):
                guest.calc_launch_digest(
                        SevMode.SEV_ES,
                        4,
                        vcpu_types.CPU_SIGS["EPYC-v4"],
                        fixtures_dir / "ovmf_AmdSev_suffix.bin",
                        "/dev/null",
                        "/dev/null",
                        "",
                        0x21,
                        dump_vmsa=True)
                self.assertTrue(pathlib.Path("vmsa0.bin").exists())
                self.assertTrue(pathlib.Path("vmsa1.bin").exists())
                self.assertTrue(pathlib.Path("vmsa2.bin").exists())
                self.assertTrue(pathlib.Path("vmsa3.bin").exists())
                self.assertFalse(pathlib.Path("vmsa4.bin").exists())

    def test_seves_with_ovmfx64_and_kernel_should_fail(self):
        with self.assertRaises(RuntimeError) as c:
            guest.calc_launch_digest(
                    SevMode.SEV_ES,
                    1,
                    None,
                    "tests/fixtures/ovmf_OvmfX64_suffix.bin",
                    "/dev/null",
                    "/dev/null",
                    "",
                    0x21)
        self.assertEqual(str(c.exception),
                         "Kernel specified but OVMF doesn't support kernel/initrd/cmdline measurement")

    def test_sev(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV,
                1,
                None,
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "console=ttyS0 loglevel=7",
                0x21)
        self.assertEqual(
                ld.hex(),
                'f0d92a1fda00249e008820bd40def6abbed2ee65fea8a8bc47e532863ca0cc6a')

    def test_sev_with_kernel_without_initrd_and_append(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV,
                1,
                None,
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                None,
                None,
                0x21)
        self.assertEqual(
                ld.hex(),
                '7332f6ef294f79919b46302e4541900a2dfc96714e2b7b4b5ccdc1899b78a195')

    def test_sev_with_ovmfx64_and_kernel_should_fail(self):
        with self.assertRaises(RuntimeError) as c:
            guest.calc_launch_digest(
                    SevMode.SEV,
                    1,
                    None,
                    "tests/fixtures/ovmf_OvmfX64_suffix.bin",
                    "/dev/null",
                    "/dev/null",
                    "",
                    0x21)
        self.assertEqual(str(c.exception),
                         "Kernel specified but OVMF doesn't support kernel/initrd/cmdline measurement")

    def test_snp_dump_vmsa(self):
        """Test that SEV-SNP mode creates vmsa files if requrested."""
        fixtures_dir = pathlib.Path('tests/fixtures').absolute()
        with tempfile.TemporaryDirectory() as tmp:
            with push_dir(tmp):
                ovmf_hash = 'cab7e085874b3acfdbe2d96dcaa3125111f00c35c6fc9708464c2ae74bfdb048a198cb9a9ccae0b3e5e1a33f5f249819'
                guest.calc_launch_digest(
                        SevMode.SEV_SNP,
                        1,
                        vcpu_types.CPU_SIGS["EPYC-v4"],
                        fixtures_dir / "ovmf_AmdSev_suffix.bin",
                        "/dev/null",
                        "/dev/null",
                        "",
                        0x21,
                        snp_ovmf_hash_str=ovmf_hash,
                        dump_vmsa=True)
                self.assertTrue(pathlib.Path("vmsa0.bin").exists())
                self.assertFalse(pathlib.Path("vmsa1.bin").exists())

    def test_sev_with_ovmfx64_without_kernel(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV,
                1,
                None,
                "tests/fixtures/ovmf_OvmfX64_suffix.bin",
                None,
                None,
                None,
                0x21)
        self.assertEqual(
                ld.hex(),
                'af9d6c674b1ff04937084c98c99ca106b25c37b2c9541ac313e6e0c54426314f')

    def test_snp_svsm_4_vcpus(self):
        """Test that SNP-SVSM mode produces correct measurement value when using 4 vCPUs"""
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP_SVSM,
                4,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                'tests/fixtures/svsm_ovmf.fd',
                None,
                None,
                None,
                0x21,
                None,
                vmm_types.VMMType.QEMU,
                False,
                'tests/fixtures/svsm.bin',
                540672)
        self.assertEqual(
                ld.hex(),
                '27d154c27b7b359c935e250ec6fee72aa0ae8c1225e3b0e1cf46a9567e938066d7d6f94bbdc4a857818bdb79277a44b2')

    def test_snp_svsm_2_vcpus(self):
        """Test that SNP-SVSM mode produces correct measurement value when using 2 vCPUs"""
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP_SVSM,
                2,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                'tests/fixtures/svsm_ovmf.fd',
                None,
                None,
                None,
                0x21,
                None,
                vmm_types.VMMType.QEMU,
                False,
                'tests/fixtures/svsm.bin',
                540672)
        self.assertEqual(
                ld.hex(),
                '9b94745036aafddf4f7f8b00c7513abb5b7703178cb95aaa57928bd963d68d3bfcb715d6019b9167ee2517b11b0d9be7')

    def test_snp_svsm_dump_vmsa(self):
        """Test that SNP-SVSM mode creates vmsa files if requrested."""
        fixtures_dir = pathlib.Path('tests/fixtures').absolute()
        with tempfile.TemporaryDirectory() as tmp:
            with push_dir(tmp):
                guest.calc_launch_digest(
                        SevMode.SEV_SNP_SVSM,
                        2,
                        vcpu_types.CPU_SIGS["EPYC-v4"],
                        fixtures_dir / 'svsm_ovmf.fd',
                        None,
                        None,
                        None,
                        0x21,
                        None,
                        vmm_types.VMMType.QEMU,
                        True,
                        fixtures_dir / 'svsm.bin',
                        540672)
                self.assertTrue(pathlib.Path("vmsa0.bin").exists())
                self.assertTrue(pathlib.Path("vmsa1.bin").exists())
                self.assertFalse(pathlib.Path("vmsa2.bin").exists())


@contextlib.contextmanager
def push_dir(dir: str):
    """Context managed switching of the working directory"""
    previous = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(previous)
