# Changelog

## Unreleased

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
