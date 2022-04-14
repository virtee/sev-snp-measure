#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from sevsnpmeasure import guest


class TestGuest(unittest.TestCase):

    def test_calc_launch_digest(self):
        ld = guest.calc_launch_digest(
                1,
                "tests/fixtures/ovmf_suffix.bin",
                "/dev/null",
                "/dev/null",
                "")
        self.assertEqual(
                ld.hex(),
                '38859e76ac5fa5009c8249eb2f44dafb33a2a1f41efd65ce'
                'b13f042864abab87d018dc64da21628b320a98642f25ae6c')
