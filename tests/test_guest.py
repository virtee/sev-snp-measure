#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from sevsnpmeasure import guest
from sevsnpmeasure import vcpu_types
from sevsnpmeasure import vmm_types
from sevsnpmeasure.sev_mode import SevMode


class TestGuest(unittest.TestCase):

    # Test of we can generate a good OVMF hash
    def test_snp_ovmf_hash_gen(self):
        ovmf_hash = 'cab7e085874b3acfdbe2d96dcaa3125111f00c35c6fc9708464c2ae74bfdb048a198cb9a9ccae0b3e5e1a33f5f249819'
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_suffix.bin",
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
        ovmf_hash = guest.calc_snp_ovmf_hash("tests/fixtures/ovmf_suffix.bin").hex()
        self.assertEqual(
                ovmf_hash,
                'edcf6d1c57ce868a167c990f58c8667c698269ef9e080324'
                '6419eea914186343054d557e1f17acd93b032c106bc70d25')

        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                snp_ovmf_hash_str=ovmf_hash)

        self.assertEqual(
                ld.hex(),
                '841f900f4aa101754522ab020442a5bd8652c4237eea7a7e'
                '2c4d501f654536378bc36be8dc06140de94a882408bc8a7f')

    def test_snp_ec2(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_suffix.bin",
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
                "tests/fixtures/ovmf_suffix.bin",
                "/dev/null",
                "/dev/null",
                "")
        self.assertEqual(
                ld.hex(),
                '841f900f4aa101754522ab020442a5bd8652c4237eea7a7e'
                '2c4d501f654536378bc36be8dc06140de94a882408bc8a7f')

    def test_seves(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_ES,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_suffix.bin",
                "/dev/null",
                "/dev/null",
                "")
        self.assertEqual(
                ld.hex(),
                '2e91d54814445ad178180af09f881efe4079fc54bfddd0ec1179ecd3cdbdf772')

    def test_sev(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV,
                1,
                None,
                "tests/fixtures/ovmf_suffix.bin",
                "/dev/null",
                "/dev/null",
                "")
        self.assertEqual(
                ld.hex(),
                '7332f6ef294f79919b46302e4541900a2dfc96714e2b7b4b5ccdc1899b78a195')
