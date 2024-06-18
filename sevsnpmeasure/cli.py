#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import argparse
import base64
import sys
import pathlib

from sevsnpmeasure import guest
from sevsnpmeasure import vcpu_types
from sevsnpmeasure import vmm_types
from .sev_mode import SevMode

VERSION = '0.0.11'


def auto_base_int(s: str) -> int:
    return int(s, 0)


def print_measurement(ld: bytes, sev_mode: SevMode, output_format: str, verbose: bool):
    if output_format == "hex":
        measurement = ld.hex()
    elif output_format == "base64":
        measurement = base64.b64encode(ld).decode()

    if verbose:
        print(f"Calculated {sev_mode.name} guest measurement: {measurement}")
    else:
        print(measurement)


def get_vcpu_sig(parser, args, vmm_type):
    if args.mode == 'sev':
        return 0
    elif args.vcpu_family:
        return vcpu_types.cpu_sig(args.vcpu_family, args.vcpu_model, args.vcpu_stepping)
    elif args.vcpu_sig:
        return args.vcpu_sig
    elif args.vcpu_type:
        return vcpu_types.CPU_SIGS[args.vcpu_type]
    elif vmm_type == vmm_types.VMMType.QEMU:
        parser.error(f"missing --vcpu-type or --vcpu-sig or --vcpu-family in guest mode '{args.mode}'")


def main() -> int:
    parser = argparse.ArgumentParser(prog='sev-snp-measure',
                                     description='Calculate AMD SEV/SEV-ES/SEV-SNP guest launch measurement')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--mode', choices=['sev', 'seves', 'snp', 'snp:ovmf-hash', 'snp:svsm'], help='Guest mode',
                        required=True)
    parser.add_argument('--vcpus', metavar='N', type=int, help='Number of guest vcpus', default=None)
    parser.add_argument('--vcpu-type', metavar='CPUTYPE', choices=list(vcpu_types.CPU_SIGS.keys()),
                        help=f"Type of guest vcpu ({', '.join(vcpu_types.CPU_SIGS.keys())})",
                        default=None)
    parser.add_argument('--vcpu-sig', metavar='VALUE', type=auto_base_int, help='Guest vcpu signature value', default=None)
    parser.add_argument('--vcpu-family', metavar='FAMILY', type=int, help='Guest vcpu family', default=None)
    parser.add_argument('--vcpu-model', metavar='MODEL', type=int, help='Guest vcpu model', default=None)
    parser.add_argument('--vcpu-stepping', metavar='STEPPING', type=int, help='Guest vcpu stepping', default=None)
    parser.add_argument('--vmm-type', metavar='VMMTYPE', type=str,
                        help=f"Type of guest vmm ({', '.join(vmm_types.VMMType.__members__.keys())})", default='QEMU')
    parser.add_argument('--ovmf', metavar='PATH',
                        help='OVMF file to calculate hash from', required=True)
    parser.add_argument('--kernel', metavar='PATH',
                        help='Kernel file to calculate hash from')
    parser.add_argument('--initrd', metavar='PATH',
                        help='Initrd file to calculate hash from (use with --kernel)')
    parser.add_argument('--append', metavar='CMDLINE',
                        help='Kernel command line to calculate hash from (use with --kernel)')
    parser.add_argument('--guest-features', metavar='VALUE', type=lambda x: int(x, 0),
                        default=0x1,
                        help="Hex representation of the guest kernel features expected to be included "
                             "(defaults to 0x1); see README.md for possible values"),
    parser.add_argument('--output-format', choices=['hex', 'base64'], help='Measurement output format', default='hex')
    parser.add_argument('--snp-ovmf-hash', metavar='HASH', help='Precalculated hash of the OVMF binary (hex string)')
    parser.add_argument('--dump-vmsa', action='store_true',
                        help='Write measured VMSAs to vmsa<N>.bin (seves, snp, and snp:svsm modes only)')

    arg_group_svsm = parser.add_argument_group(title='snp:svsm Mode',
                                               description='AMD SEV-SNP with Coconut-SVSM. This mode additionally requires '
                                               '--svsm and either --vars-file or --vars-size to be set.')
    arg_group_svsm.add_argument('--svsm', type=str, metavar='PATH', help='SVSM binary')
    arg_group_ovmf_vars = arg_group_svsm.add_mutually_exclusive_group(required=False)
    arg_group_ovmf_vars.add_argument('--vars-size', type=int, metavar='SIZE', help='Size of the OVMF_VARS file in bytes '
                                     '(conflicts with --vars-file)')
    arg_group_ovmf_vars.add_argument('--vars-file', type=str, metavar='PATH', help='OVMF_VARS file '
                                     '(conflicts with --vars-size)')

    args = parser.parse_args()

    if args.mode == 'snp:ovmf-hash':
        print(guest.calc_snp_ovmf_hash(args.ovmf).hex())
        return 0

    if args.initrd and args.kernel is None:
        parser.error("--kernel required when using --initrd")

    if args.append and args.kernel is None:
        parser.error("--kernel required when using --append")

    if args.mode != 'sev' and args.vcpus is None:
        parser.error(f"missing --vcpus N in guest mode '{args.mode}'")

    if args.vmm_type in vmm_types.VMMType.__members__.keys():
        vmm_type = vmm_types.VMMType[args.vmm_type]
    else:
        parser.error(f"unknown VMM type '{args.vmm_type}'")

    vcpu_sig = get_vcpu_sig(parser, args, vmm_type)

    try:
        vars_size = 0
        sev_mode = SevMode.from_str(args.mode)

        if sev_mode == SevMode.SEV_SNP_SVSM:

            if args.vars_file:
                vars_size = pathlib.Path(args.vars_file).stat().st_size
            elif args.vars_size:
                vars_size = args.vars_size
            else:
                parser.error("snp:svsm mode requires --vars-size or --vars-file")

        if args.dump_vmsa is True and sev_mode not in [SevMode.SEV_ES, SevMode.SEV_SNP, SevMode.SEV_SNP_SVSM]:
            parser.error("--dump-vmsa is not availibe in the selected mode")

        ld = guest.calc_launch_digest(sev_mode, args.vcpus, vcpu_sig, args.ovmf, args.kernel, args.initrd, args.append,
                                      args.guest_features, args.snp_ovmf_hash, vmm_type, args.dump_vmsa,
                                      args.svsm, vars_size)

        print_measurement(ld, sev_mode, args.output_format, args.verbose)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
