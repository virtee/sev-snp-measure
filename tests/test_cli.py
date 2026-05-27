import unittest
from argparse import Namespace
from sevsnpmeasure.cli import get_vcpu_sig
from sevsnpmeasure.vmm_types import VMMType
from sevsnpmeasure.vcpu_types import CPU_SIGS, cpu_sig


class TestCLI(unittest.TestCase):
    def test_get_vcpu_sig_zero(self):
        args = Namespace(mode="snp", vcpu_family=None, vcpu_sig=0, vcpu_type=None)
        sig = get_vcpu_sig(None, args, VMMType.QEMU)
        self.assertEqual(sig, 0)

    def test_get_vcpu_sig_none_qemu_errors(self):
        class MockParser:
            def error(self, msg):
                raise ValueError(msg)

        parser = MockParser()
        args = Namespace(mode="snp", vcpu_family=None, vcpu_sig=None, vcpu_type=None)
        with self.assertRaises(ValueError):
            get_vcpu_sig(parser, args, VMMType.QEMU)

    def test_get_vcpu_sig_from_type(self):
        args = Namespace(
            mode="snp", vcpu_family=None, vcpu_sig=None, vcpu_type="EPYC-Milan"
        )
        sig = get_vcpu_sig(None, args, VMMType.QEMU)
        self.assertEqual(sig, CPU_SIGS["EPYC-Milan"])

    def test_get_vcpu_sig_from_family(self):
        CPU_FAMILY = 25
        CPU_MODEL = 1
        CPU_STEPPING = 1

        args = Namespace(
            mode="snp",
            vcpu_family=CPU_FAMILY,
            vcpu_model=CPU_MODEL,
            vcpu_stepping=CPU_STEPPING,
            vcpu_sig=None,
            vcpu_type=None,
        )
        expected = cpu_sig(CPU_FAMILY, CPU_MODEL, CPU_STEPPING)
        sig = get_vcpu_sig(None, args, VMMType.QEMU)
        self.assertEqual(sig, expected)
