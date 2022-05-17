#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import argparse
import sys

from sevsnpmeasure import guest
from .sev_mode import SevMode

VERSION = '0.0.2'


def main() -> int:
    parser = argparse.ArgumentParser(prog='sev-snp-measure',
                                     description='Calculate AMD SEV/SEV-ES/SEV-SNP guest launch measurement')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--mode', choices=['sev', 'seves', 'snp'], help='Guest mode', required=True)
    parser.add_argument('--vcpus', metavar='N', type=int, help='Number of guest vcpus', default=None)
    parser.add_argument('--ovmf', metavar='PATH',
                        help='OVMF file to calculate hash from', required=True)
    parser.add_argument('--kernel', metavar='PATH',
                        help='Kernel file to calculate hash from')
    parser.add_argument('--initrd', metavar='PATH',
                        help='Initrd file to calculate hash from (use with --kernel)')
    parser.add_argument('--append', metavar='CMDLINE',
                        help='Kernel command line to calculate hash from (use with --kernel)')
    args = parser.parse_args()

    if args.mode != 'sev' and args.vcpus is None:
        parser.error(f"missing --vcpus N in guest mode '{args.mode}'")

    sev_mode = SevMode.from_str(args.mode)
    ld = guest.calc_launch_digest(sev_mode, args.vcpus, args.ovmf, args.kernel, args.initrd, args.append)
    if args.verbose:
        print(f"Calculated {sev_mode.name} guest measurement: {ld.hex()}")
    else:
        print(ld.hex())
    return 0


if __name__ == '__main__':
    sys.exit(main())
