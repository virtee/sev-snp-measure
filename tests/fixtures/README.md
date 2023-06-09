# tests/fixtures

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
