#!/usr/bin/python


import time

from libsan.host.cmdline import run
from libsan.host.linux import mkdir, mount, umount
from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_var


def stopped_pool_preserve_data():
    errors = []

    stratis = Stratis()
    pool_name = read_var("STRATIS_POOL")
    pool_uuid = read_var("STRATIS_POOL_UUID")
    fs_name = "fs_test"
    file_name = "test_file"
    mount_dir = "/mnt/pool_preserve_data"
    message = "this is pool preserve data test"
    stratis_fs_path = f"/dev/stratis/{pool_name}/{fs_name}"

    atomic_run(
        f"Creating filesystem: {fs_name}",
        pool_name=pool_name,
        fs_name=fs_name,
        command=stratis.fs_create,
        errors=errors,
    )

    time.sleep(2)

    atomic_run(f"Creating dir: {mount_dir}", new_dir=mount_dir, command=mkdir, errors=errors)

    atomic_run(
        f"Mounting filesystem: {fs_name}",
        device=stratis_fs_path,
        mountpoint=mount_dir,
        command=mount,
        errors=errors,
    )

    atomic_run(
        f"Writing data to file: {fs_name}",
        cmd=f"echo '{message}' > {mount_dir}/{file_name}",
        command=run,
        errors=errors,
    )

    atomic_run(
        "Writing 1GB of random data to stratis fs",
        cmd=f"dd if=/dev/random of={mount_dir}/random_data bs=1M count=1000",
        command=run,
        errors=errors,
    )

    atomic_run(
        f"Trying to stop pool with mounted fs, this should fail: {fs_name}",
        pool_name=pool_name,
        command=stratis.pool_stop,
        expected_ret=1,
        expected_out=[
            "stratis_cli._errors.StratisCliEngineError: ERROR: low-level ioctl error due to nix error;"
            " header result:",
            "error: EBUSY: Device or resource busy",
        ],
        errors=errors,
    )

    atomic_run(f"Unmounting fs: {fs_name}", mountpoint=mount_dir, command=umount, errors=errors)

    atomic_run("Listing stratis filesystems", command=stratis.fs_list, errors=errors)

    atomic_run(
        "Trying to stop pool with unmounted fs",
        pool_name=pool_name,
        command=stratis.pool_stop,
        errors=errors,
    )

    atomic_run(
        "Starting pool to verify data",
        pool_uuid=pool_uuid,
        command=stratis.pool_start,
        errors=errors,
    )

    atomic_run("Listing stratis filesystems", command=stratis.fs_list, errors=errors)

    atomic_run(
        f"Mounting filesystem: {fs_name}",
        device=stratis_fs_path,
        mountpoint=mount_dir,
        command=mount,
        errors=errors,
    )

    _, data = atomic_run(
        "Check data on filesystem",
        return_output=True,
        cmd=f"cat {mount_dir}/{file_name}",
        command=run,
        errors=errors,
    )

    if message not in data:
        errors.append(f"FAIL: Could not find message: {message} in returned output!")

    atomic_run(
        "Writing 1GB of random data to stratis fs to verify fs is still usable",
        cmd=f"dd if=/dev/random of={mount_dir}/random_data2 bs=1M count=1000",
        command=run,
        errors=errors,
    )

    atomic_run(f"Unmounting fs: {fs_name}", mountpoint=mount_dir, command=umount, errors=errors)

    atomic_run(
        f"Destroying filesystem: {fs_name}",
        pool_name=pool_name,
        fs_name=fs_name,
        command=stratis.fs_destroy,
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = stopped_pool_preserve_data()
    exit(parse_ret(errs))
