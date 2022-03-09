import unittest
from sevsnpmeasure import guest

class TestGuest(unittest.TestCase):

    def test_calc_launch_digest(self):
        ld = guest.calc_launch_digest("tests/fixtures/ovmf_suffix.bin", "tests/fixtures/vmsa_cpu0.bin", "/dev/null", "/dev/null", "")
        self.assertEqual(ld.hex(), '38859e76ac5fa5009c8249eb2f44dafb33a2a1f41efd65ceb13f042864abab87d018dc64da21628b320a98642f25ae6c')
