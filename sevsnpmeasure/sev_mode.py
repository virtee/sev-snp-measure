#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import enum


class SevMode(enum.Enum):
    SEV = enum.auto()
    SEV_ES = enum.auto()
    SEV_SNP = enum.auto()
    SEV_SNP_SVSM = enum.auto()

    @staticmethod
    def from_str(s: str):
        if s == "sev" or s == "SEV":
            return SevMode.SEV
        elif s == "seves" or s == "sev-es" or s == "SEVES" or s == "SEV-ES":
            return SevMode.SEV_ES
        elif s == "snp" or s == "sev-snp" or s == "SNP" or s == "SEV-SNP":
            return SevMode.SEV_SNP
        elif s.lower() in ["snp:svsm", "sev-snp:svsm"]:
            return SevMode.SEV_SNP_SVSM
        else:
            raise ValueError("illegal SEV mode")
