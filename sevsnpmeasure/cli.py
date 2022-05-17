#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import argparse
import base64
import sys

from sevsnpmeasure import guest
from sevsnpmeasure import vcpu_types
from .sev_mode import SevMode

VERSION = '0.0.3'


def auto_base_int(s: str) -> int:
    return int(s, 0)


def main() -> int:
    parser = argparse.ArgumentParser(prog='sev-snp-measure',
                                     description='Calculate AMD SEV/SEV-ES/SEV-SNP guest launch measurement')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--mode', choices=['sev', 'seves', 'snp'], help='Guest mode', required=True)
    parser.add_argument('--vcpus', metavar='N', type=int, help='Number of guest vcpus', default=None)
    parser.add_argument('--vcpu-type', metavar='CPUTYPE', choices=list(vcpu_types.CPU_SIGS.keys()),
                        help=f"Type of guest vcpu ({', '.join(vcpu_types.CPU_SIGS.keys())})",
                        default=None)
    parser.add_argument('--vcpu-sig', metavar='VALUE', type=auto_base_int, help='Guest vcpu signature value', default=None)
    parser.add_argument('--vcpu-family', metavar='FAMILY', type=int, help='Guest vcpu family', default=None)
    parser.add_argument('--vcpu-model', metavar='MODEL', type=int, help='Guest vcpu model', default=None)
    parser.add_argument('--vcpu-stepping', metavar='STEPPING', type=int, help='Guest vcpu stepping', default=None)
    parser.add_argument('--ovmf', metavar='PATH',
                        help='OVMF file to calculate hash from', required=True)
    parser.add_argument('--kernel', metavar='PATH',
                        help='Kernel file to calculate hash from')
    parser.add_argument('--initrd', metavar='PATH',
                        help='Initrd file to calculate hash from (use with --kernel)')
    parser.add_argument('--append', metavar='CMDLINE',
                        help='Kernel command line to calculate hash from (use with --kernel)')
    parser.add_argument('--output-format', choices=['hex', 'base64'], help='Measurement output format', default='hex')
    args = parser.parse_args()

    if args.mode != 'sev' and args.vcpus is None:
        parser.error(f"missing --vcpus N in guest mode '{args.mode}'")

    vcpu_sig = 0
    if args.mode != 'sev':
        if args.vcpu_family:
            vcpu_sig = vcpu_types.cpu_sig(args.vcpu_family, args.vcpu_model, args.vcpu_stepping)
        elif args.vcpu_sig:
            vcpu_sig = args.vcpu_sig
        elif args.vcpu_type:
            vcpu_sig = vcpu_types.CPU_SIGS[args.vcpu_type]
        else:
            parser.error(f"missing --vcpu-type or --vcpu-sig or --vcpu-family in guest mode '{args.mode}'")

    sev_mode = SevMode.from_str(args.mode)
    ld = guest.calc_launch_digest(sev_mode, args.vcpus, vcpu_sig, args.ovmf, args.kernel, args.initrd, args.append)

    if args.output_format == "hex":
        measurement = ld.hex()
    elif args.output_format == "base64":
        measurement = base64.b64encode(ld).decode()

    if args.verbose:
        print(f"Calculated {sev_mode.name} guest measurement: {measurement}")
    else:
        print(measurement)
    return 0


if __name__ == '__main__':
    sys.exit(main())
