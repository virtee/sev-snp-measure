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
                'a076e1b0e6cf55fd94c82e2c25245f8c15f76690b941ba37'
                '9b31527f82eafe7ad489777ff510d080bac9cd14d41bc205')

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
                'db06fb267824b1ccb56edbe2a9c2ce88841bca5090dc6dac'
                '91d9cd30f3c2c0bf42daccb30d55d6625bfbf0dae5c50c6d')

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
                '314e4f0794187ffef05702a36546ea5fe02698041b7f7f17'
                'd9f418da2d5e4d5cff25256cef9d34888a0dd64dea438780')

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
                'f07864303ad8243132029e8110b92805c78d1135a15da75f'
                '67abb9a711d78740347f24ee76f603e650ec4adf3611cc1e'
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
                '314e4f0794187ffef05702a36546ea5fe02698041b7f7f17'
                'd9f418da2d5e4d5cff25256cef9d34888a0dd64dea438780')

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
                'f07864303ad8243132029e8110b92805c78d1135a15da75f'
                '67abb9a711d78740347f24ee76f603e650ec4adf3611cc1e')

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
                '6d9054ed9872a64c968cfbcfa1247cafa792e3f9a395306d'
                '95c9937aaa081c643d25f369ccbd34409dafcae90bff55f3')

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
                'e5e6be5a8fa6256f0245666bb237e2d028b7928148ce78d5'
                '1b8a64dc9506c377709a5b5d7ab75554593bced304fcff93')

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
                '3aa1bdf5a87fad15960f099e82a09e428901c590f2b68d71'
                'aa246c168db5e75daf4819d017a9530c56bed2da5c0cdbd7')

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
                '1c784beb8c49aa604b7fd57fbc73b36ec53a3f5fb48a2b89'
                '5ad6cc2ea15d18ee7cc15e3e57c792766b45f944c3e81cfe')

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
                '37a9efc939f360a9ccfaaf1a7702137b81ea00c38d0361c8'
                '523285fad1b10e94ad8c1ecd7c82ff589cb120670be74a99')

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
                0x21)
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
                "",
                0x21)
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
                '265aed64f2454253f6b19e49e17041ef052dedf964dd8d2740794a06aee3a720c475e3643a1b7e26b9efce7a107bf77f')

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
                '4ae03ca013690e956bc1eb16bc1c6465788dba64ad88a650db09216fa9cdddf06167bfce810eba8988108e71458dd68b')

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
