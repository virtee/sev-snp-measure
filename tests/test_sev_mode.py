#
# Copyright 2024 Red Hat, Inc.
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from sevsnpmeasure.sev_mode import SevMode


class TestSevMode(unittest.TestCase):

    def test_sev_mode_from_string(self):
        """Test conversion from string to SevMode."""
        self.assertEqual(SevMode.from_str("SEV"), SevMode.SEV)
        self.assertEqual(SevMode.from_str("sev"), SevMode.SEV)

        self.assertEqual(SevMode.from_str("sev-es"), SevMode.SEV_ES)
        self.assertEqual(SevMode.from_str("seves"), SevMode.SEV_ES)
        self.assertEqual(SevMode.from_str("SEVES"), SevMode.SEV_ES)
        self.assertEqual(SevMode.from_str("SEV-ES"), SevMode.SEV_ES)

        self.assertEqual(SevMode.from_str("sev-snp"), SevMode.SEV_SNP)
        self.assertEqual(SevMode.from_str("snp"), SevMode.SEV_SNP)
        self.assertEqual(SevMode.from_str("SEV-SNP"), SevMode.SEV_SNP)
        self.assertEqual(SevMode.from_str("SNP"), SevMode.SEV_SNP)

        self.assertEqual(SevMode.from_str("SnP:sVsM"), SevMode.SEV_SNP_SVSM)
        self.assertEqual(SevMode.from_str("SNP:SVSM"), SevMode.SEV_SNP_SVSM)
        self.assertEqual(SevMode.from_str("sev-SnP:sVsM"), SevMode.SEV_SNP_SVSM)

        with self.assertRaises(ValueError):
            SevMode.from_str("foo")
