#!/usr/bin/env python3

import argparse

from sevsnpmeasure import guest

def main() -> None:
    parser = argparse.ArgumentParser(description='Calculate AMD SEV-SNP launch measurement')
    parser.add_argument('--ovmf',
                        help='OVMF file to calculate hash from', required=True)
    parser.add_argument('--vmsa',
                        help='file containing the contents of VMSA in binary format', required=True)
    parser.add_argument('--kernel',
                        help='kernel file to calculate hash from')
    parser.add_argument('--initrd',
                        help='initrd file to calculate hash from (use with --kernel)')
    parser.add_argument('--append',
                        help='the kernel command line to calculate hash from (use with --kernel)')
    args = parser.parse_args()

    ld = guest.calc_launch_digest(args.ovmf, args.vmsa, args.kernel, args.initrd, args.append)
    print("Calculated SNP guest measurement:", ld.hex())

if __name__ == '__main__':
    main()
