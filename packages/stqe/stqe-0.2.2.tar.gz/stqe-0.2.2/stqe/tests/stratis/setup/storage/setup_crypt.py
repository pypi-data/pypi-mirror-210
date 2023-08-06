#!/usr/bin/python

from libsan.host.cmdline import run
from libsan.host.scsi import get_free_disks

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import write_var


def setup_crypt(crypt_name=None):
    errors = []
    passwd = "redhatredhat"
    if not crypt_name:
        crypt_name = "test_crypt"
    disks = atomic_run(message="Getting free disks for crypt", command=get_free_disks, errors=errors)
    if disks is None:
        exit(1)
    disks = disks.keys()
    _, lsblk = atomic_run(
        message="Listing block devices to check they are really free.",
        command=run,
        cmd="lsblk",
        return_output=True,
        errors=errors,
    )
    # remove disks that are in use (find only partitioned ones)
    values = [x.strip() for line in lsblk.splitlines() for x in line.split()]
    for disk in [disk for value in values for disk in disks if disk != value and disk in value]:
        disks.remove(disk)

    disk_paths = ["/dev/" + j for j in disks]
    print("Found these free disks: %s" % " ".join(disk_paths))
    for disk in disk_paths:
        atomic_run(
            "Zeroing superblock of disk %s." % disk,
            command=run,
            cmd="dd if=/dev/zero of=%s bs=4k count=2" % disk,
            errors=errors,
        )
    if not disk_paths:
        print("Could not find any disk")
        exit(1)
    test_disk = disk_paths[0]
    atomic_run(
        "Format luks with device %s" % test_disk,
        cmd=f"echo {passwd} |cryptsetup luksFormat -q {test_disk}",
        command=run,
        errors=errors,
    )

    atomic_run(
        "Open luks with device %s " % test_disk,
        cmd=f"echo {passwd} |cryptsetup open -q {test_disk}  {crypt_name}",
        command=run,
        errors=errors,
    )

    run(cmd="cryptsetup luksDump %s" % test_disk)

    atomic_run(
        "Writing var STRATIS_AVAILABLE_DEVICES",
        command=write_var,
        var={"STRATIS_AVAILABLE_DEVICES": "/dev/mapper/%s" % crypt_name},
        errors=errors,
    )

    atomic_run(
        "Writing var STRATIS_DEVICE",
        command=write_var,
        var={"STRATIS_DEVICE": "/dev/mapper/%s" % crypt_name},
        errors=errors,
    )

    atomic_run("Writing var CRYPT_DISKS", command=write_var, var={"CRYPT_DISKS": test_disk}, errors=errors)

    atomic_run(message="Listing block devices.", command=run, cmd="lsblk", errors=errors)

    return errors


if __name__ == "__main__":
    errs = setup_crypt(crypt_name="test_crypt")
    exit(parse_ret(errs))
