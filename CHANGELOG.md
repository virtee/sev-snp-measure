# Changelog

## Unreleased
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
