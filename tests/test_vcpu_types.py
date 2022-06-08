#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from sevsnpmeasure import vcpu_types


class TestGuest(unittest.TestCase):

    def test_cpu_sig_with_low_family(self):
        sig = vcpu_types.cpu_sig(family=14, model=1, stepping=2)
        self.assertEqual(sig, 0x0e12)

    def test_cpu_sig_with_high_family(self):
        sig = vcpu_types.cpu_sig(family=23, model=1, stepping=2)
        self.assertEqual(sig, 0x800f12)
