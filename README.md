# sev-snp-measure

## Scope

Calculate expected measurement of an AMD SEV-SNP guest VM for confidential
computing.

## Usage

```
$ git clone https://github.com/IBM/sev-snp-measure.git
$ cd sev-snp-measure
$ ./sev-snp-measure.py --help
usage: sev-snp-measure.py [-h] --ovmf OVMF --vmsa VMSA [--kernel KERNEL] [--initrd INITRD]
                          [--append APPEND]

Calculate AMD SEV-SNP launch measurement

optional arguments:
  -h, --help       show this help message and exit
  --ovmf OVMF      OVMF file to calculate hash from
  --vmsa VMSA      file containing the contents of VMSA in binary format
  --kernel KERNEL  kernel file to calculate hash from
  --initrd INITRD  initrd file to calculate hash from (use with --kernel)
  --append APPEND  the kernel command line to calculate hash from (use with --kernel)
```

## Notes

If you have any questions or issues you can create a new [issue
here](https://github.com/IBM/sev-snp-measure/issues/new)

Pull requests are welcome!

## License

Apache 2.0 license.
