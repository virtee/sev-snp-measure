#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from sevsnpmeasure import guest
from sevsnpmeasure import vcpu_types
from sevsnpmeasure.sev_mode import SevMode


class TestGuest(unittest.TestCase):

    def test_snp(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_SNP,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "fixtures/ovmf_suffix.bin",
                "/dev/null",
                "/dev/null",
                "")
        self.assertEqual(
                ld.hex(),
                '38859e76ac5fa5009c8249eb2f44dafb33a2a1f41efd65ce'
                'b13f042864abab87d018dc64da21628b320a98642f25ae6c')

    def test_seves(self):
        ld = guest.calc_launch_digest(
                SevMode.SEV_ES,
                1,
                vcpu_types.CPU_SIGS["EPYC-v4"],
                "fixtures/ovmf_suffix.bin",
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
                "fixtures/ovmf_suffix.bin",
                "/dev/null",
                "/dev/null",
                "")
        self.assertEqual(
                ld.hex(),
                'd59d7696efd7facfaa653758586e6120c4b6eaec3e327771d278cc6a44786ba5')
