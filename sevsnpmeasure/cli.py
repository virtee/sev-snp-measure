import argparse
import sys
from sevsnpmeasure import guest


def main() -> int:
    parser = argparse.ArgumentParser(description='Calculate AMD SEV-SNP launch measurement')
    parser.add_argument('--vcpus', type=int, help='Number of vcpus', required=True)
    parser.add_argument('--ovmf',
                        help='OVMF file to calculate hash from', required=True)
    parser.add_argument('--kernel',
                        help='Kernel file to calculate hash from')
    parser.add_argument('--initrd',
                        help='Initrd file to calculate hash from (use with --kernel)')
    parser.add_argument('--append',
                        help='Kernel command line to calculate hash from (use with --kernel)')
    args = parser.parse_args()

    ld = guest.calc_launch_digest(args.vcpus, args.ovmf, args.kernel, args.initrd, args.append)
    print("Calculated SNP guest measurement:", ld.hex())
    return 0


if __name__ == '__main__':
    sys.exit(main())
