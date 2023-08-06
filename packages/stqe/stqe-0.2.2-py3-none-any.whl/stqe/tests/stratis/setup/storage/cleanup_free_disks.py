#!/usr/bin/python


from time import sleep

from libsan.host.cmdline import run

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import clean_var, read_var, write_var


def cleanup_free_disks():
    print("INFO: Cleaning up free disks to previous state.")
    errors = []

    print("Waiting for data stream to settle before logging out of iscsi.")
    sleep(5)

    stratis_number_of_luns = read_var("STRATIS_NUMBER_OF_LUNS")
    if stratis_number_of_luns != 0:
        path = "/home/"
        wwn = read_var("STRATIS_LOOPBACK_WWN")
        stratis_fileio_name = read_var("STRATIS_LUN_NAME")

        atomic_run(
            "Deleting loopback",
            cmd=f"targetcli /loopback delete {wwn}",
            command=run,
            errors=errors,
        )

        for lun in range(stratis_number_of_luns):
            atomic_run(
                f"Deleting backstore {stratis_fileio_name}{lun}",
                cmd=f"targetcli /backstores/fileio delete {stratis_fileio_name}{lun}",
                command=run,
                errors=errors,
            )

            atomic_run(
                f"Removing file from {path}",
                cmd=f"rm -f {path}{stratis_fileio_name}{lun}.img",
                command=run,
                errors=errors,
            )

        atomic_run(
            "Cleaning var STRATIS_LOOPBACK_WWN",
            command=clean_var,
            var="STRATIS_LOOPBACK_WWN",
            errors=errors,
        )

        atomic_run(
            "Cleaning var STRATIS_LUN_NAME",
            command=clean_var,
            var="STRATIS_LUN_NAME",
            errors=errors,
        )

    atomic_run(
        "Cleaning var STRATIS_DEVICE",
        command=clean_var,
        var="STRATIS_DEVICE",
        errors=errors,
    )

    atomic_run(
        "Cleaning var STRATIS_AVAILABLE_DEVICES",
        command=clean_var,
        var="STRATIS_AVAILABLE_DEVICES",
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
    errs = cleanup_free_disks()
    exit(parse_ret(errs))
