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
    def test_snp_ovmf_hash_gen(self):
        ovmf_hash = 'cab7e085874b3acfdbe2d96dcaa3125111f00c35c6fc9708464c2ae74bfdb048a198cb9a9ccae0b3e5e1a33f5f249819'
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                snp_ovmf_hash_str=ovmf_hash)
        self.assertEqual(
                ld.hex(),
                'db06fb267824b1ccb56edbe2a9c2ce88841bca5090dc6dac'
                '91d9cd30f3c2c0bf42daccb30d55d6625bfbf0dae5c50c6d')

    # Test of we can a full LD from the OVMF hash
    def test_snp_ovmf_hash_full(self):
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
                snp_ovmf_hash_str=ovmf_hash)
        self.assertEqual(
                ld.hex(),
                'f07864303ad8243132029e8110b92805c78d1135a15da75f'
                '67abb9a711d78740347f24ee76f603e650ec4adf3611cc1e')

    def test_snp_ec2(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                vmm_type=vmm_types.VMMType.ec2)
        self.assertEqual(
                ld.hex(),
                '760b6e51039d2d6c1fc6d38ca5c387967d158e0294883e45'
                '22c36f89bd61bfc9cdb975cd1ceedffbe1b23b1daf4e3f42')

    def test_snp(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "console=ttyS0 loglevel=7")
        self.assertEqual(
                ld.hex(),
                'f07864303ad8243132029e8110b92805c78d1135a15da75f'
                '67abb9a711d78740347f24ee76f603e650ec4adf3611cc1e')

    def test_snp_without_kernel(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                None,
                None,
                None)
        self.assertEqual(
                ld.hex(),
                'e5e6be5a8fa6256f0245666bb237e2d028b7928148ce78d5'
                '1b8a64dc9506c377709a5b5d7ab75554593bced304fcff93')

    def test_snp_with_multiple_vcpus(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                4,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "")
        self.assertEqual(
                ld.hex(),
                '1c784beb8c49aa604b7fd57fbc73b36ec53a3f5fb48a2b89'
                '5ad6cc2ea15d18ee7cc15e3e57c792766b45f944c3e81cfe')

    def test_snp_with_ovmfx64_without_kernel(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_OvmfX64_suffix.bin",
                None,
                None,
                None)
        self.assertEqual(
                ld.hex(),
                '7ef631fa7f659f7250de96c456a0eb7354bd3b9461982f38'
                '6a41c6a6aede87870ad020552a5a0716672d5d6e5b86b8f9')

    def test_snp_with_ovmfx64_and_kernel_should_fail(self):
        with self.assertRaises(RuntimeError) as c:
            guest.calc_launch_digest(
                    SevMode.SEV_SNP,
                    1,
                    vcpu_types.CPU_SIGS["EPYC-v4"],
                    "tests/fixtures/ovmf_OvmfX64_suffix.bin",
                    "/dev/null",
                    "/dev/null",
                    "")
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
                "")
        self.assertEqual(
                ld.hex(),
                '2e91d54814445ad178180af09f881efe4079fc54bfddd0ec1179ecd3cdbdf772')

    def test_seves_with_multiple_vcpus(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_ES,
                4,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_AmdSev_suffix.bin",
                "/dev/null",
                "/dev/null",
                "")
        self.assertEqual(
                ld.hex(),
                'c05d37600072dc5ff24bafc49410f0369ba3a37c130a7bb7055ac6878be300f7')

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
                    "")
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
                "console=ttyS0 loglevel=7")
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
                None)
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
                    "")
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
                None)
        self.assertEqual(
                ld.hex(),
                'af9d6c674b1ff04937084c98c99ca106b25c37b2c9541ac313e6e0c54426314f')

@contextlib.contextmanager
def push_dir(dir: str):
    """Context managed switching of the working directory"""
    previous = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(previous)
