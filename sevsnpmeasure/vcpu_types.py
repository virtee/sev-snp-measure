def cpu_sig(family: int, model: int, stepping: int) -> int:
    """Compute the 32-bit CPUID signature from family, model, and stepping.

    This computation is described in AMD's CPUID Specification, publication #25481
    https://www.amd.com/system/files/TechDocs/25481.pdf
    See section: CPUID Fn0000_0001_EAX Family, Model, Stepping Identifiers
    """
    if family > 0xf:
        family_low = 0xf
        family_high = (family - 0x0f) & 0xff
    else:
        family_low = family
        family_high = 0

    model_low = model & 0xf
    model_high = (model >> 4) & 0xf

    stepping_low = stepping & 0xf

    return ((family_high << 20) |
            (model_high << 16) |
            (family_low << 8) |
            (model_low << 4) |
            stepping_low)


# List the CPU types that appear in QEMU's builtin_x86_defs
CPU_SIGS = {
    'EPYC': cpu_sig(family=23, model=1, stepping=2),
    'EPYC-v1': cpu_sig(family=23, model=1, stepping=2),
    'EPYC-v2': cpu_sig(family=23, model=1, stepping=2),
    'EPYC-IBPB': cpu_sig(family=23, model=1, stepping=2),
    'EPYC-v3': cpu_sig(family=23, model=1, stepping=2),
    'EPYC-v4': cpu_sig(family=23, model=1, stepping=2),
    'EPYC-Rome': cpu_sig(family=23, model=49, stepping=0),
    'EPYC-Rome-v1': cpu_sig(family=23, model=49, stepping=0),
    'EPYC-Rome-v2': cpu_sig(family=23, model=49, stepping=0),
    'EPYC-Rome-v3': cpu_sig(family=23, model=49, stepping=0),
    'EPYC-Milan': cpu_sig(family=25, model=1, stepping=1),
    'EPYC-Milan-v1': cpu_sig(family=25, model=1, stepping=1),
    'EPYC-Milan-v2': cpu_sig(family=25, model=1, stepping=1),
    'EPYC-Genoa': cpu_sig(family=25, model=17, stepping=0),
    'EPYC-Genoa-v1': cpu_sig(family=25, model=17, stepping=0),
}
