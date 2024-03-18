# sev-snp-measure

## Scope

Command-line tool and Python library to calculate expected measurement of an
AMD SEV/SEV-ES/SEV-SNP guest VM for confidential computing.

## Installation

### From pip

Install from pip:

    pip install sev-snp-measure

This installs the `sevsnpmeasure` package and the `sev-snp-measure`
command-line script.

### From Github

Clone the Github repo and run the script directly from the local directory:

    git clone https://github.com/virtee/sev-snp-measure.git
    cd sev-snp-measure
    ./sev-snp-measure.py --help

## Command-line usage

### sev-snp-measure
```
$ sev-snp-measure --help
usage: sev-snp-measure [-h] [--version] [-v] --mode {sev,seves,snp,snp:ovmf-hash,snp:svsm}
                       [--vcpus N] [--vcpu-type CPUTYPE] [--vcpu-sig VALUE] [--vcpu-family FAMILY]
                       [--vcpu-model MODEL] [--vcpu-stepping STEPPING] [--vmm-type VMMTYPE] --ovmf
                       PATH [--kernel PATH] [--initrd PATH] [--append CMDLINE]
                       [--guest-features VALUE] [--output-format {hex,base64}]
                       [--snp-ovmf-hash HASH] [--dump-vmsa] [--svsm PATH]
                       [--vars-size SIZE | --vars-file PATH]

Calculate AMD SEV/SEV-ES/SEV-SNP guest launch measurement

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v, --verbose
  --mode {sev,seves,snp,snp:ovmf-hash,snp:svsm}
                        Guest mode
  --vcpus N             Number of guest vcpus
  --vcpu-type CPUTYPE   Type of guest vcpu (EPYC, EPYC-v1, EPYC-v2, EPYC-IBPB, EPYC-v3, EPYC-v4,
                        EPYC-Rome, EPYC-Rome-v1, EPYC-Rome-v2, EPYC-Rome-v3, EPYC-Milan, EPYC-
                        Milan-v1, EPYC-Milan-v2, EPYC-Genoa, EPYC-Genoa-v1)
  --vcpu-sig VALUE      Guest vcpu signature value
  --vcpu-family FAMILY  Guest vcpu family
  --vcpu-model MODEL    Guest vcpu model
  --vcpu-stepping STEPPING
                        Guest vcpu stepping
  --vmm-type VMMTYPE    Type of guest vmm (QEMU, ec2)
  --ovmf PATH           OVMF file to calculate hash from
  --kernel PATH         Kernel file to calculate hash from
  --initrd PATH         Initrd file to calculate hash from (use with --kernel)
  --append CMDLINE      Kernel command line to calculate hash from (use with --kernel)
  --guest-features VALUE
                        Hex representation of the guest kernel features expected to be included
                        (defaults to 0x1); see README.md for possible values
  --output-format {hex,base64}
                        Measurement output format
  --snp-ovmf-hash HASH  Precalculated hash of the OVMF binary (hex string)
  --dump-vmsa           Write measured VMSAs to vmsa<N>.bin (seves, snp, and snp:svsm modes only)

snp:svsm Mode:
  AMD SEV-SNP with Coconut-SVSM. This mode additionally requires --svsm and either --vars-file
  or --vars-size to be set.

  --svsm PATH           SVSM binary
  --vars-size SIZE      Size of the OVMF_VARS file in bytes (conflicts with --vars-file)
  --vars-file PATH      OVMF_VARS file (conflicts with --vars-size)
```

### Example: SNP mode

```
$ sev-snp-measure --mode snp --vcpus=1 --vcpu-type=EPYC-v4 --ovmf=OVMF.fd --kernel=vmlinuz --initrd=initrd.img --append="console=ttyS0 loglevel=7"
1c8bf2f320add50cb22ca824c17f3fa51a7a4296a4a3113698c2e31b50c2dcfa7e36dea3ebc3a9411061c30acffc6d5a
```

### Example: SNP:SVSM mode

```
$ sev-snp-measure \
    --mode snp:svsm \
    --vmm-type=QEMU \
    --vcpus=4 \
    --vcpu-type=EPYC-v4 \
    --ovmf=OVMF_CODE.fd \
    --svsm=svsm.bin --vars-file=OVMF_VARS.fd
3447e476b226e317890a350003b56ee17becb48d1dc25dd6b5819a1192df3238f50cda0f0216bd5ae2a992ad7ab961c4
```

### snp-create-id-block
```
$ snp-create-id-block --help
usage: snp-create-id-block [-h] [--measurement VALUE] [--idkey PATH] [--authorkey PATH]

Calculate AMD SEV-SNP guest id block

optional arguments:
  -h, --help           show this help message and exit
  --measurement VALUE  Guest launch measurement in Base64 encoding
  --idkey PATH         id private key file
  --authorkey PATH     author private key file
```

## Programmatic usage

After installing the `sev-snp-measure` package with pip, you can call it from
another Python application:

```python3
from sevsnpmeasure import guest,id_block
from sevsnpmeasure import vcpu_types
from sevsnpmeasure.sev_mode import SevMode

ld = guest.calc_launch_digest(SevMode.SEV_SNP, vcpus_num, vcpu_types.CPU_SIGS["EPYC-v4"],
                              ovmf_path, kernel_path, initrd_path, cmdline_str, guest_features)
print("Calculated measurement:", ld.hex())

block = id_block.snp_calc_id_block(ld,"id_key_file","author_key_file")
print("Calculated id block in base64", block)
```

## Choosing guest CPU type

For SEV-ES and SEV-SNP, the initial CPU state (VMSA) includes the guest CPU
signature in the edx register when you use the QEMU vmm.  Therefore, starting
the VM with a different type of guest CPU will modify the content of the VMSA,
and therefore modify the calculated measurement.

You can choose the guest CPU type using `--vcpu-type`, or `--vcpu-sig`, or a
combination of `--vcpu-family`, `--vcpu-model`, and `--vcpu-stepping`. For
example, the following 3 invocations are identical:

1. `sev-snp-measure --vcpu-type=EPYC-v4 ...`
2. `sev-snp-measure --vcpu-sig=0x800f12 ...`
3. `sev-snp-measure --vcpu-family=23 --vcpu-model=1 --vcpu-stepping=2 ...`

## SEV-SNP Guest Feature Field Values
Prior to Linux Kernel version 6.6, the default value was always calculated to `0x1`, as the kernel only supported `SNPActive`. After the release of Linux Kernel 6.6, additional features were made available some of them enabled by default. Because of this, the new default value is `0x21` which is `SNPActive + DebugSwap`. Other possible combinations my be derived by generating a 64-bit hex value from the following chart:

| BIT FIELD | Description |
|:---------:|:------------:|
| 0 | SNPActive |
| 1 | vTOM |
| 2 | ReflectVC |
| 3 | RestrictedInjection |
| 4 | AlternateInjection |
| 5 | DebugSwap |
| 6 | PreventHostIBS |
| 7 | BTBIsolation |
| 8 | VmplSSS |
| 9 | SecureTSC |
| 10 | VmgexitParameter |
| 11 | Reserved, SBZ |
| 12 | IbsVirtualization |
| 13 | Reserved, SBZ |
| 14 | VmsaRegProt |
| 15 | SmtProtection |
| 63:16 | Reserved, SBZ |


## Precalculated OVMF hashes

The SEV-SNP digest gets generated in multiple steps that each have a digest as output. With that digest output, you can stop at any of these steps and continue generation of the full digest later. These are the steps:

1. OVMF
2. (optional) -kernel, -initrd, -append arguments
3. Initial state of all vCPUs

In situations where only minor OVMF changes happen, you may not want to copy the full OVMF binary to the validation system. In these situations, you can cut digest calculation after the `OVMF` step and use its hash instead of the full binary.

To generate a hash, use the `--mode snp:ovmf-hash` parameter:

    $ sev-snp-measure --mode snp:ovmf-hash --ovmf OVMF.fd
    cab7e085874b3acfdbe2d96dcaa3125111f00c35c6fc9708464c2ae74bfdb048a198cb9a9ccae0b3e5e1a33f5f249819

On a different machine that only has access to an older but compatible OVMF binary, you can then ingest the hash again to generate a full measurement:

    $ sev-snp-measure --mode snp --vcpus=1 --vcpu-type=EPYC-v4 --ovmf=OVMF.fd.old --ovmf-hash cab7e[...]
    d52697c3e056fb8d698d19cc29adfbed5a8ec9170cb9eb63c2ac957d22b4eb647e25780162036d063a0cf418b8830acc

## Related projects

* [sev-snp-measure-go](https://github.com/virtee/sev-snp-measure-go): port of sev-snp-measure to Go
* libvirt tools: [virt-dom-sev-validate](https://gitlab.com/berrange/libvirt/-/blob/lgtm/tools/virt-dom-sev-validate.py),
  [virt-dom-sev-vmsa-tool](https://gitlab.com/berrange/libvirt/-/blob/lgtm/tools/virt-dom-sev-vmsa-tool.py)
* [sev Rust crate](https://github.com/virtee/sev) and [snpguest CLI tool](https://github.com/virtee/snpguest)
* [snp-digest-rs](https://github.com/slp/snp-digest-rs)
* AMD [sev-tool](https://github.com/AMDESE/sev-tool), [sev-guest](https://github.com/AMDESE/sev-guest),
  and [sev-utils](https://github.com/amd/sev-utils)
* [go-sev-guest](https://github.com/google/go-sev-guest)

## Development

Run all unit tests:

    pip install -r requirements.txt
    make test

Check unit tests coverage:

    pip install coverage
    make coverage
    # See HTML coverage report in htmlcov/

Check Python type hints:

    pip install mypy
    make typecheck

Check Python coding style:

    pip install flake8
    make lint

## Notes

If you have any questions or issues you can create a new [issue
here](https://github.com/virtee/sev-snp-measure/issues/new)

Pull requests are welcome!

## License

Apache 2.0 license.
