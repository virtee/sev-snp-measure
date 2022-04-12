# sev-snp-measure

## Scope

Command-line tool and Python library to calculate expected measurement of an
AMD SEV-SNP guest VM for confidential computing.

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
usage: sev-snp-measure [-h] --vcpus VCPUS --ovmf OVMF [--kernel KERNEL] [--initrd INITRD] [--append APPEND]

Calculate AMD SEV-SNP launch measurement

optional arguments:
  -h, --help       show this help message and exit
  --vcpus VCPUS    Number of vcpus
  --ovmf OVMF      OVMF file to calculate hash from
  --kernel KERNEL  Kernel file to calculate hash from
  --initrd INITRD  Initrd file to calculate hash from (use with --kernel)
  --append APPEND  Kernel command line to calculate hash from (use with --kernel)
```

For example:

    $ sev-snp-measure --vcpus=1 --ovmf=OVMF.fd --kernel=vmlinuz --initrd=initrd.img --append="console=ttyS0 loglevel=7"
    Calculated SNP guest measurement: 1c8bf2f320add50cb22ca824c17f3fa51a7a4296a4a3113698c2e31b50c2dcfa7e36dea3ebc3a9411061c30acffc6d5a

## Programmatic usage

After installing the `sev-snp-measure` package with pip, you can call it from
another Python application:

```python3
from sevsnpmeasure import guest

ld = guest.calc_launch_digest(vcpus_num, ovmf_path, kernel_path, initrd_path, cmdline_str)
print("Calculated measurement:", ld.hex())
```

## Notes

If you have any questions or issues you can create a new [issue
here](https://github.com/IBM/sev-snp-measure/issues/new)

Pull requests are welcome!

## License

Apache 2.0 license.
