from enum import Enum


class VMMType(Enum):
    QEMU = 1
    ec2 = 2
    gce = 3
