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
        ovmf_hash = '086e2e9149ebf45abdc3445fba5b2da8270bdbb04094d7a2c37faaa4b24af3aa16aff8c374c2a55c467a50da6d466b74'
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
                '329c8ce0972ae52343b64d34a434a86f245dfd74f5ed7aae'
                '15d22efc78fb9683632b9b50e4e1d7fa41179ef98a7ef198')

    def test_snp_ovmf_hash_gen_feature_snp_only(self):
        ovmf_hash = '086e2e9149ebf45abdc3445fba5b2da8270bdbb04094d7a2c37faaa4b24af3aa16aff8c374c2a55c467a50da6d466b74'
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
                'ddc5224521617a536ee7ce9dd6224d1b58a8d4fda1c741f3'
                'ac99fc4bfa04ba6e9fc98646d4a07a9079397fa3852819b5')

    # Test of we can a full LD from the OVMF hash
    def test_snp_ovmf_hash_full_default(self):
        ovmf_hash = guest.calc_snp_ovmf_hash("tests/fixtures/ovmf_AmdSev_suffix.bin").hex()
        self.assertEqual(
                ovmf_hash,
                '086e2e9149ebf45abdc3445fba5b2da8270bdbb04094d7a2'
                'c37faaa4b24af3aa16aff8c374c2a55c467a50da6d466b74')

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
                '803f691094946e42068aaa3a8f9e26a5c89f36f7b73ecfb2'
                '8c653360fe4b3aba7e534442e7e1e17895dfe778d0228977')

    def test_snp_ovmf_hash_full_feature_snp_only(self):
        ovmf_hash = guest.calc_snp_ovmf_hash("tests/fixtures/ovmf_AmdSev_suffix.bin").hex()
        self.assertEqual(
                ovmf_hash,
                '086e2e9149ebf45abdc3445fba5b2da8270bdbb04094d7a2'
                'c37faaa4b24af3aa16aff8c374c2a55c467a50da6d466b74')

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
                '6d287813eb5222d770f75005c664e34c204f385ce832cc2c'
                'e7d0d6f354454362f390ef83a92046c042e706363b4b08fa')

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
                '6ae80856486b1396af8c82a40351d6ed76a20c785e9c7fa4'
                'ffa27c22d5d6313b4b3b458cd3c9968e6f89fb5d8450d7a6')

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
                '7d3756157c805bf6adf617064c8552e8c1688fa1c8756f11'
                'cbf56ba5d25c9270fb69c0505c1cbe1c5c66c0e34c6ed3be')

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
                '803f691094946e42068aaa3a8f9e26a5c89f36f7b73ecfb2'
                '8c653360fe4b3aba7e534442e7e1e17895dfe778d0228977')

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
                '6d287813eb5222d770f75005c664e34c204f385ce832cc2c'
                'e7d0d6f354454362f390ef83a92046c042e706363b4b08fa')

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
                'e1e1ca029dd7973ab9513295be68198472dcd4fc834bd9af'
                '9b63f6e8a1674dbf281a9278a4a2ebe0eed9f22adbcd0e2b')

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
                '19358ba9a7615534a9a1e2f0dfc29384dcd4dcb7062ff9c6'
                '013b26869a5fc6ecabe033c48dd6f6db5d6d76e7c5df632d')

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
                '4953b1fb416fa874980e8442b3706d345926d5f38879134e'
                '00813c5d7abcbe78eafe7b422907be0b4698e2414a631942')

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
                '5061fffb019493a903613d56d54b94912a1a2f9e4502385f'
                '5c194616753720a92441310ba6c4933de877c36e23046ad5')

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
                '28797ae0afaba4005a81e629acebfb59e6687949d6be4400'
                '7cd5506823b0dd66f146aaae26ff291eed7b493d8a64c385')

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
                'da0296de8193586a5512078dcd719eccecbd87e2b825ad41'
                '48c44f665dc87df21e5b49e21523a9ad993afdb6a30b4005')

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
                '13810ae661ea11e2bb205621f582fee268f0367c8f97bc297b7fadef3e12002c')

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
                '0dccbcaba8e90b261bd0d2e1863a2f9da714768b7b2a19363cd6ae35aa90de91')

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
                '82a3ee5d537c3620628270c292ae30cb40c3c878666a7890ee7ef2a08fb535ff')

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
                '77f613d7bbcdf12a73782ea9e88b0172aeda50d1a54201cb903594ff52846898')

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
                'b4c021e085fb83ceffe6571a3d357b4a98773c83c474e47f76c876708fe316da')

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
