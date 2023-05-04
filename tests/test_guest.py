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
                '228c6b5fe659c179041ed98ccc13e1199a2d85575ef28b7b'
                '851e4a0b3a178f5401620cc67b1aa22bca198566defb63e1')

    # Test of we can a full LD from the OVMF hash
    def test_snp_ovmf_hash_full(self):
        ovmf_hash = guest.calc_snp_ovmf_hash("tests/fixtures/ovmf_suffix.bin").hex()
        self.assertEqual(
                ovmf_hash,
                '4ef91bfd7241908300ac19305a694753cbc8db28104f356f'
                'd7860cc7b4119db285ce80586c19bd358a731d5267cee60e')

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
                'd68382026a91989d9428675e9b220548b76db03c75234403'
                '16b90f0a72c33b5fee2ade72791fb1c0ff0a923741e5190d')

    def test_snp_ec2(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "tests/fixtures/ovmf_suffix.bin",
                "/dev/null",
                "/dev/null",
                "",
                vmm_type = vmm_types.VMMType.ec2)
        self.assertEqual(
                ld.hex(),
                '21408991204a77c12eb014cc7a1ad723b423069f421b873d'
                '1fa283472712182752a5ad6656f5e22aea239b6adde1db26')

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
                'd68382026a91989d9428675e9b220548b76db03c75234403'
                '16b90f0a72c33b5fee2ade72791fb1c0ff0a923741e5190d')

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
                '7e5c26fb454621eb466978b4d0242b3c04b44a034de7fc0a2d8dac60ea2b6403')

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
                'd59d7696efd7facfaa653758586e6120c4b6eaec3e327771d278cc6a44786ba5')
