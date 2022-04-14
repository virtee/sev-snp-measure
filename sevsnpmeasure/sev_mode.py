#
# Copyright 2022- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache-2.0
#

import enum


class SevMode(enum.Enum):
    SEV = enum.auto()
    SEV_ES = enum.auto()
    SEV_SNP = enum.auto()
