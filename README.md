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

    git clone https://github.com/IBM/sev-snp-measure.git
    cd sev-snp-measure
    ./sev-snp-measure.py --help

## Command-line usage

```
$ sev-snp-measure --help
usage: sev-snp-measure [-h] [--version] [-v] --mode {sev,seves,snp} [--vcpus N]
                       [--vcpu-type CPUTYPE] [--vcpu-sig VALUE] [--vcpu-family FAMILY]
                       [--vcpu-model MODEL] [--vcpu-stepping STEPPING] --ovmf PATH [--kernel PATH]
                       [--initrd PATH] [--append CMDLINE] [--output-format {hex,base64}]

Calculate AMD SEV/SEV-ES/SEV-SNP guest launch measurement

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v, --verbose
  --mode {sev,seves,snp}
                        Guest mode
  --vcpus N             Number of guest vcpus
  --vcpu-type CPUTYPE   Type of guest vcpu (EPYC, EPYC-v1, EPYC-v2, EPYC-IBPB, EPYC-v3, EPYC-v4,
                        EPYC-Rome, EPYC-Rome-v1, EPYC-Rome-v2, EPYC-Rome-v3, EPYC-Milan, EPYC-
                        Milan-v1, EPYC-Milan-v2)
  --vcpu-sig VALUE      Guest vcpu signature value
  --vcpu-family FAMILY  Guest vcpu family
  --vcpu-model MODEL    Guest vcpu model
  --vcpu-stepping STEPPING
                        Guest vcpu stepping
  --ovmf PATH           OVMF file to calculate hash from
  --kernel PATH         Kernel file to calculate hash from
  --initrd PATH         Initrd file to calculate hash from (use with --kernel)
  --append CMDLINE      Kernel command line to calculate hash from (use with --kernel)
  --output-format {hex,base64}
                        Measurement output format
```

For example:

    $ sev-snp-measure --mode snp --vcpus=1 --vcpu-type=EPYC-v4 --ovmf=OVMF.fd --kernel=vmlinuz --initrd=initrd.img --append="console=ttyS0 loglevel=7"
    1c8bf2f320add50cb22ca824c17f3fa51a7a4296a4a3113698c2e31b50c2dcfa7e36dea3ebc3a9411061c30acffc6d5a

## Programmatic usage

After installing the `sev-snp-measure` package with pip, you can call it from
another Python application:

```python3
from sevsnpmeasure import guest
from sevsnpmeasure import vcpu_types
from sevsnpmeasure.sev_mode import SevMode

ld = guest.calc_launch_digest(SevMode.SEV_SNP, vcpus_num, vcpu_types.CPU_SIGS["EPYC-v4"],
                              ovmf_path, kernel_path, initrd_path, cmdline_str)
print("Calculated measurement:", ld.hex())
```

## Choosing guest CPU type

For SEV-ES and SEV-SNP, the initial CPU state (VMSA) includes the guest CPU
signature in the edx register.  Therefore, starting the VM with a different
type of guest CPU will modify the content of the VMSA, and therefore modify the
calculated measurement.

You can choose the guest CPU type using `--vcpu-type`, or `--vcpu-sig`, or a
combination of `--vcpu-family`, `--vcpu-model`, and `--vcpu-stepping`. For
example, the following 3 invocations are identical:

1. `sev-snp-measure --vcpu-type=EPYC-v4 ...`
2. `sev-snp-measure --vcpu-sig=0x800f12 ...`
3. `sev-snp-measure --vcpu-family=23 --vcpu-model=1 --vcpu-stepping=2 ...`

## Related projects

* libvirt tools: [virt-dom-sev-validate](https://gitlab.com/berrange/libvirt/-/blob/lgtm/tools/virt-dom-sev-validate.py),
  [virt-dom-sev-vmsa-tool](https://gitlab.com/berrange/libvirt/-/blob/lgtm/tools/virt-dom-sev-vmsa-tool.py)
* [sev Rust crate](https://github.com/virtee/sev)
* [AMD SEV-Tool](https://github.com/AMDESE/sev-tool)

## Notes

If you have any questions or issues you can create a new [issue
here](https://github.com/IBM/sev-snp-measure/issues/new)

Pull requests are welcome!

## License

Apache 2.0 license.
