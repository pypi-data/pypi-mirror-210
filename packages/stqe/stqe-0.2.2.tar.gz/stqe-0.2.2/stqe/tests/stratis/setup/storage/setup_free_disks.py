#!/usr/bin/python


from libsan.host.cmdline import run
from libsan.host.lio import TargetCLI
from libsan.host.mp import get_free_mpaths, is_multipathd_running, mpath_name_of_wwid, remove_mpath
from libsan.host.nvme import get_free_nvme_devices
from libsan.host.scsi import get_free_disks, get_logical_block_size_of_disk, get_physical_block_size_of_disk

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_env, write_var


def setup_disks_targetcli(missing_devices, block_size="4096"):
    errors = []
    target = TargetCLI()
    wwn = "naa.50014054c1441891"
    stratis_device_size = "10G"
    name = "stratis-lun-"

    try:
        stratis_device_size = read_env("fmf_loopback_size")
    except KeyError:
        pass

    target.path = "/loopback"
    atomic_run("Creating loopback", wwn=wwn, command=target.create, errors=errors)

    for file in range(missing_devices):
        target.path = "/backstores/fileio"

        atomic_run(
            "Creating fileio backstore",
            command=target.create,
            name=f"{name}{file}",
            file_or_dev=f"/home/{name}{file}.img",
            size=stratis_device_size,
            errors=errors,
        )

        target.path = f"/backstores/fileio/{name}{file}"

        atomic_run(
            f"Setting block size of {name}{file} to {block_size}",
            command=target.set,
            group="attribute",
            block_size=block_size,
            errors=errors,
        )

        target.path = "/loopback/" + wwn + "/" + "luns"

        atomic_run(
            "Creating lun using fileio backstore",
            command=target.create,
            storage_object=f"/backstores/fileio/{name}{file}",
            errors=errors,
        )

    atomic_run("Writing var STRATIS_LOOPBACK_WWN", command=write_var, var={"STRATIS_LOOPBACK_WWN": wwn}, errors=errors)

    atomic_run("Writing var STRATIS_LUN_NAME", command=write_var, var={"STRATIS_LUN_NAME": name}, errors=errors)

    atomic_run(
        "Writing var STRATIS_NUMBER_OF_LUNS",
        command=write_var,
        var={"STRATIS_NUMBER_OF_LUNS": missing_devices},
        errors=errors,
    )

    if is_multipathd_running():
        lio_disks = atomic_run(
            message="Getting free disks",
            exclude_mpath_device=False,
            command=get_free_disks,
            filter_only={"vendor": "LIO-ORG"},
            errors=errors,
        )

        # Try to remove mpath from lio disks
        for disk in lio_disks:
            mpath_name = mpath_name_of_wwid(lio_disks[disk]["wwid"])
            if mpath_name:
                print(f"INFO: Trying to remove mpath {mpath_name}")
                remove_mpath(mpath_name)

    return errors


def setup_local_disks(required_disks):
    msg = "INFO: Getting local disks."
    if required_disks:
        msg += f" Trying to get {required_disks} disks"
    print(msg)
    errors = []
    disk_paths = []

    # get available scsi devices
    disks = atomic_run(message="Getting free disks", command=get_free_disks, errors=errors)

    # get available nvme devices
    nvme_devices = atomic_run(message="Getting free nvme devices", command=get_free_nvme_devices, errors=errors)

    if nvme_devices:
        disks.update(nvme_devices)

    mpath_disks = {}
    if is_multipathd_running():
        # getting free mpaths
        mpaths = get_free_mpaths()
        if mpaths:
            mpath_disks = {
                mpath["dm_name"]: {
                    "logical_block_size": get_logical_block_size_of_disk(mpath["dm_name"]),
                    "physical_block_size": get_physical_block_size_of_disk(mpath["dm_name"]),
                    "name": mpath["dm_name"],
                }
                for mpath in mpaths.values()
            }
    if mpath_disks:
        disks.update(mpath_disks)

    filtered_disks_by_block_sizes = {}
    for disk in disks.values():
        try:
            block_size = (disk["logical_block_size"], disk["physical_block_size"])
            if block_size in filtered_disks_by_block_sizes:
                filtered_disks_by_block_sizes[block_size].append(disk["name"])
            else:
                filtered_disks_by_block_sizes[block_size] = [disk["name"]]
        except KeyError:
            print(f"WARN: Could not find logical or physical block size of disk: {disk['name']}")

    print("INFO: Filtering disks by block sizes:")
    most_available_disks = []
    block_size_of_chosen_disks = ()
    for block_size in filtered_disks_by_block_sizes:
        print(
            f"INFO: Found following disks with block "
            f"sizes {', '.join(block_size)}: {','.join(filtered_disks_by_block_sizes[block_size])}"
        )
        if len(filtered_disks_by_block_sizes[block_size]) > len(most_available_disks):
            most_available_disks = filtered_disks_by_block_sizes[block_size]
            block_size_of_chosen_disks = block_size
    print(
        f"Using following disks: {', '.join(most_available_disks)}"
        f" with block sizes: {', '.join(block_size_of_chosen_disks)}"
    )
    disks = most_available_disks

    number_of_avail_devices = len(disks)
    missing_devices = required_disks - number_of_avail_devices
    if missing_devices > 0 and block_size_of_chosen_disks != ("512", "4096"):
        msg = (
            f"INFO: Found only {number_of_avail_devices} out of {required_disks} required. "
            f"Creating {missing_devices} disks with targetcli!"
        )
        print(msg)

        errors += setup_disks_targetcli(missing_devices, block_size_of_chosen_disks[0])

        targetcli_disks = atomic_run(
            message="Getting free disks", command=get_free_disks, filter_only={"vendor": "LIO-ORG"}, errors=errors
        )
        disks.extend(targetcli_disks)
    else:
        atomic_run(
            "Writing var STRATIS_NUMBER_OF_LUNS",
            command=write_var,
            var={"STRATIS_NUMBER_OF_LUNS": 0},
            errors=errors,
        )
        if block_size_of_chosen_disks == ("512", "4096"):
            msg = "WARN: Creating targetcli disks with block sizes 512, 4096 is not supported!"
            print(msg)

    disk_paths += ["/dev/" + j for j in disks]
    print(f"Using these blockdevs: {' '.join(disk_paths)}")
    for disk in disk_paths:
        atomic_run(
            f"Zeroing superblock of disk {disk}.",
            command=run,
            cmd=f"dd if=/dev/zero of={disk} bs=1M count=10",
            errors=errors,
        )

    atomic_run(
        "Writing var STRATIS_AVAILABLE_DEVICES",
        command=write_var,
        var={"STRATIS_AVAILABLE_DEVICES": disk_paths},
        errors=errors,
    )

    atomic_run(
        "Writing var STRATIS_DEVICE",
        command=write_var,
        var={"STRATIS_DEVICE": disk_paths},
        errors=errors,
    )

    atomic_run(message="Listing block devices.", command=run, cmd="lsblk", errors=errors)

    return errors


if __name__ == "__main__":
    try:
        required_disks = read_env("fmf_required_disks")
    except KeyError:
        required_disks = None
    errs = setup_local_disks(required_disks)
    exit(parse_ret(errs))
