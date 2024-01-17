# tests/fixtures

## SEV-ES and SNP

`ovmf_AmdSev_suffix.bin` contains the last 4KB of the `OVMF.fd` binary from
edk2's `OvmfPkg/AmdSev/AmdSevX64.dsc` build; this is the build that supports
kernel-hashes and measured direct boot.  Currently the SNP support for
kernel-hashes is not upstream in the edk2 repository, so this is built from the
[snp-kernel-hashes-v3 fork](https://github.com/confidential-containers-demo/edk2/tree/snp-kernel-hashes-v3).

`ovmf_OvmfX64_suffix.bin` contains the last 4KB of the `OVMF.fd` binary from
edk2's `OvmfPkg/OvmfPkgX64.dsc` build; this is the standard build of OVMF.

To save space, we committed only the last 4KB instead of the the full 4MB
binaries.

The end of the file contains a GUIDed footer table with entries that hold the
SEV-ES AP reset vector address and SNP metadata table, which are needed in
order to compute VMSAs for SEV-ES guests and the list of SNP measured pages.

## SVSM

`svsm.bin` contains a full Coconut SVSM binary image, based on this commit [bebb485a](https://github.com/coconut-svsm/svsm/commit/bebb485aa94b84e59aca905f62414db885efc419)
from the main branch with some additional code that prints the measurement
value.

`svsm_ovmf.fd` is a matching OVMF build from commit [e824edbc](https://github.com/coconut-svsm/edk2/commit/e824edbc98303a1de73f233aca25ea6512d3a29b).
The full files are required for SNP:SVSM mode. Qemu from commit [0e64fb84](https://github.com/coconut-svsm/qemu/commit/0e64fb84eeeb86e2b263068c098a64d2f3d5a661)
running on host kernel based on commit [e1335c6f0](https://github.com/coconut-svsm/linux/commit/e1335c6f029281db280945e084ec2d079934e744)
was used to launch Coconut SVSM and obtain the measurement values used in
the tests.
