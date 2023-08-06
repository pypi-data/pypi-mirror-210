#!/usr/bin/python

from libsan.host.cmdline import run

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import clean_var, read_var


def cleanup_crypt():
    name = read_var("STRATIS_DEVICE")
    errors = []

    atomic_run("Stopping crypt device %s" % name, cmd="cryptsetup close %s" % name, command=run, errors=errors)

    disks = read_var("CRYPT_DISKS")
    atomic_run(
        "Zeroing superblock on disks: %s" % disks,
        cmd="dd if=/dev/zero of=%s bs=1M count=1" % disks,
        command=run,
        errors=errors,
    )

    atomic_run("Cleaning var STRATIS_DEVICE", command=clean_var, var="STRATIS_DEVICE", errors=errors)

    atomic_run("Cleaning var CRYPT_DISKS", command=clean_var, var="CRYPT_DISKS", errors=errors)

    return errors


if __name__ == "__main__":
    errs = cleanup_crypt()
    exit(parse_ret(errs))
