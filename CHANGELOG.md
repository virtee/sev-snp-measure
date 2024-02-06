# Changelog

## Unreleased

### Added
- Add optional `--vars-file` (besides `--vars-size`) for SNP-SVSM mode (by
  [@osteffenrh](https://github.com/osteffenrh)).

## 0.0.8 - 2024-02-01

### Added
- Add `--mode=snp:svsm` to calculate SNP measurements when starting with SVSM
  under QEMU (by [@osteffenrh](https://github.com/osteffenrh)).
- Add `--dump-vmsa` to write measured VMSAs to local files for debugging (by
  [@osteffenrh](https://github.com/osteffenrh)).

### Modified
- Fix bad id-auth signature generation (by [@shuk777](https://github.com/shuk777)).
- Verify keys given to snp-create-id-block are EC P-384 keys (by [@shuk777](https://github.com/shuk777)).

## 0.0.7 - 2023-06-27

### Modified
- Github repository moved to the [VirTEE](https://github.com/virtee) organization.

## 0.0.6 - 2023-06-12

### Added
- Add `--vmm-type=ec2` to calculate SNP measurements according to the EC2 VMM,
  which is slightly different than the way QEMU measures the initial VM state
  (by [@agraf](https://github.com/agraf)).

### Modified
- Detect OVMF that doesn't support kernel hashes and exit with error.
- Exit with error if `--initrd`/`--append` are used without `--kernel`.

## 0.0.5 - 2023-04-13

### Modified
- Modify SNP measured direct boot to match the order of measured pages in QEMU
  for the [March 2023 patches (v3)](https://lore.kernel.org/qemu-devel/20230302092347.1988853-1-dovmurik@linux.ibm.com/)
  for SNP measured boot.  Note that this is a **BREAKING CHANGE** if you use
  `--kernel` (that is, the calculated measurement will be different when compared
  to v0.0.4).

## 0.0.4 - 2023-04-13

### Added
- Add `--mode=snp:ovmf-hash` and `--snp-ovmf-hash` to allow precalculating the
  first part of SNP launch digest and avoid carrying the full OVMF binary for
  every minor OVMF change (by [@agraf](https://github.com/agraf)).
- Add new utility `snp-create-id-block` which allows generating an SNP ID block
  from a given measurement (by [@shuk777](https://github.com/shuk777)).

## 0.0.3 - 2022-05-17

### Added
- Add `--output-format={hex,base64}` to control the measurement output format
  (default is hex)
- For SEV-ES and SNP: Add guest CPU type choice using `--vcpu-type` or
  `--vcpu-sig` or `--vcpu-family/--vcpu-model/--vcpu-stepping`
- Add SEV (`--mode=sev`) and SEV-ES (`--mode=seves`) measurement modes
- Add `--verbose` for verbose output; by default, only the digest is printed
- Improve README

## 0.0.2 - 2022-04-11

### Added
- Initial version
