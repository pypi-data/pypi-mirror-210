#!/usr/bin/python


from time import sleep

from libsan.host.lvm import vg_remove

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import clean_var, read_var, write_var


def cleanup_lvm():
    print("INFO: Cleaning up free disks to previous state.")
    errors = []

    print("Waiting for data stream to settle before logging out of iscsi.")
    sleep(5)

    vg_name = read_var("STRATIS_VG")
    atomic_run(
        "Removing vg and all lvs",
        force=True,
        vg_name=vg_name,
        command=vg_remove,
        errors=errors,
    )

    atomic_run("Cleaning var STRATIS_VG", command=clean_var, var="STRATIS_VG", errors=errors)

    atomic_run(
        "Cleaning var STRATIS_DEVICE",
        command=clean_var,
        var="STRATIS_DEVICE",
        errors=errors,
    )

    backup = read_var("STRATIS_DEVICE_BACKUP")
    if backup:
        atomic_run(
            "Cleaning var STRATIS_DEVICE_BACKUP",
            command=clean_var,
            var="STRATIS_DEVICE_BACKUP",
            errors=errors,
        )

        atomic_run(
            "Writing var STRATIS_DEVICE",
            command=write_var,
            var={"STRATIS_DEVICE": backup},
            errors=errors,
        )

    return errors


if __name__ == "__main__":
    errs = cleanup_lvm()
    exit(parse_ret(errs))
