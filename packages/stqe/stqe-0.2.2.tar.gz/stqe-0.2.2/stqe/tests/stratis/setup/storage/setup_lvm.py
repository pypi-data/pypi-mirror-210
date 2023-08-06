#!/usr/bin/python


from libsan.host.cmdline import run
from libsan.host.linux import is_service_running
from libsan.host.lvm import lv_create, vg_create
from libsan.host.scsi import get_free_disks

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_var, write_var


def setup_lvm():
    msg = "INFO: Getting local disks."
    print(msg)
    vg_name = "stratis_vg"
    lv_name = "stratis_lv_"
    errors = []

    disks = atomic_run(message="Getting free disks", command=get_free_disks, errors=errors)
    if disks is None:
        msg = "FAIL: Could not find any free disks."
        print(msg)
        errors.append(msg)
        return errors

    disks = disks.keys()
    disk_paths = ["/dev/" + j for j in disks]
    blockdevs = read_var("STRATIS_DEVICE")

    if blockdevs:
        # backup the previous devices
        atomic_run(
            "Writing var STRATIS_DEVICE_BACKUP",
            command=write_var,
            var={"STRATIS_DEVICE_BACKUP": " ".join(blockdevs)},
            errors=errors,
        )
        if not isinstance(blockdevs, list):
            blockdevs = [blockdevs]
        disk_paths += [x for x in blockdevs if x not in blockdevs]

    print("Using these blockdevs: %s" % " ".join(disk_paths))
    for disk in disk_paths:
        atomic_run(
            "Zeroing superblock of disk %s." % disk,
            command=run,
            cmd="dd if=/dev/zero of=%s bs=1M count=10" % disk,
            errors=errors,
        )
        if is_service_running("multipathd"):
            atomic_run(
                "remove multipath superblock of disk %s." % disk,
                command=run,
                cmd="multipath -W %s" % disk,
                errors=errors,
            )

    atomic_run(
        "Creating volume group from available disks",
        pv_name=" ".join(disk_paths),
        vg_name=vg_name,
        command=vg_create,
        errors=errors,
    )

    lv_paths = []

    for i in range(4):
        atomic_run(
            f"Creating logical volume with_name {lv_name}{i}",
            options=["-l 25%VG"],
            vg_name=vg_name,
            lv_name=f"{lv_name}{i}",
            command=lv_create,
            errors=errors,
        )

        lv_paths.append(f"/dev/mapper/{vg_name}-{lv_name}{i}")

    print("INFO: Will use following paths:" + " \n".join(lv_paths))

    atomic_run(
        "Writing var STRATIS_VG",
        command=write_var,
        var={"STRATIS_VG": vg_name},
        errors=errors,
    )

    atomic_run(
        "Writing var STRATIS_AVAILABLE_DEVICES",
        command=write_var,
        var={"STRATIS_AVAILABLE_DEVICES": lv_paths},
        errors=errors,
    )

    atomic_run(
        "Writing var STRATIS_DEVICE",
        command=write_var,
        var={"STRATIS_DEVICE": lv_paths},
        errors=errors,
    )

    atomic_run(message="Listing block devices.", command=run, cmd="lsblk", errors=errors)

    return errors


if __name__ == "__main__":
    errs = setup_lvm()
    exit(parse_ret(errs))
