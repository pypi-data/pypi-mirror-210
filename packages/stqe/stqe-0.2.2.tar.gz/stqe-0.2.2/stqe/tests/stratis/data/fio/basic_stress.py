#!/usr/bin/python


from os import environ

from libsan.host.fio import fio_stress
from libsan.host.linux import mkdir, mount, rmdir, umount
from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_var


def basic_stress():
    errors = []

    stratis = Stratis()
    pool_name = "pool_stress"
    fs_name = "fs_stress"
    mnt_dir = "basic_stress"
    stratis_fs_path = f"/dev/stratis/{pool_name}/{fs_name}"
    blockdev = read_var("STRATIS_DEVICE")

    atomic_run(
        "Creating pool",
        pool_name=pool_name,
        blockdevs=blockdev,
        command=stratis.pool_create,
        errors=errors,
    )

    atomic_run(
        "Creating FS",
        pool_name=pool_name,
        fs_name=fs_name,
        command=stratis.fs_create,
        errors=errors,
    )

    atomic_run(f"Creating dir: {mnt_dir}", new_dir=mnt_dir, command=mkdir, errors=errors)

    atomic_run(
        f"Mounting filesystem: {fs_name}",
        device=stratis_fs_path,
        mountpoint=mnt_dir,
        command=mount,
        errors=errors,
    )

    arguments = [
        {
            "message": "Checking stratis status to get info on data.",
            "command": stratis.fs_list,
        },
        # FIXME: Get max size of device to run stress test
        {
            "message": "Starting fio stress on stratis fs",
            "command": fio_stress,
            "directory": f"{mnt_dir}",
            "of": None,
            "verbose": True,
            # fio settings
            "ioengine": environ["fmf_ioengine"],
            "direct": environ["fmf_direct"],
            "group_reporting": environ["fmf_group_reporting"],
            "bs": environ["fmf_bs"],
            "iodepth": environ["fmf_iodepth"],
            "numjobs": environ["fmf_numjobs"],
            "rw": environ["fmf_rw"],
            "rwmixread": environ["fmf_rwmixread"],
            "randrepeat": environ["fmf_randrepeat"],
            "norandommap": environ["fmf_norandommap"],
            "size": environ["fmf_size"],
            "runtime": int(environ["fmf_runtime"]) * 60,
        },
        {
            "message": "Checking stratis status to get info on data.",
            "command": stratis.fs_list,
        },
    ]

    for argument in arguments:
        atomic_run(errors=errors, **argument)

    atomic_run("Unmounting filesystem", mountpoint=mnt_dir, command=umount, errors=errors)

    atomic_run("Removing mnt dir", dir_name=mnt_dir, command=rmdir, errors=errors)

    atomic_run(
        f"Destroying filesystem: fs{fs_name}",
        pool_name=pool_name,
        fs_name=fs_name,
        command=stratis.fs_destroy,
        errors=errors,
    )

    atomic_run(
        f"Destroying pool: {pool_name}",
        pool_name=pool_name,
        command=stratis.pool_destroy,
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    if int(environ["fmf_tier"]) == 1:
        errs = basic_stress()
    exit(parse_ret(errs))
