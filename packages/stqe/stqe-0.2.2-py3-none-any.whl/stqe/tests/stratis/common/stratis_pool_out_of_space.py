#!/usr/bin/python


from libsan.host.linux import mkdir, mount, umount
from libsan.host.loopdev import create_loopdev, delete_loopdev
from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_env


def pool_out_of_space():
    errors = []

    pool_name = "pool_out_of_space2"
    fs_size = 512
    loopdev_size = 10400
    fs_name = "fs_fail"
    mount_dir = "/mnt/pool_out_of_space"
    stratis_fs_path = f"/dev/stratis/{pool_name}/fs1"
    no_overprovision = None
    stratis = Stratis()

    try:
        no_overprovision = read_env("fmf_pool_nooverprovision")
    except KeyError:
        pass

    loop_path = create_loopdev(size=loopdev_size)

    if not no_overprovision:
        atomic_run(
            f"Creating pool: {pool_name}",
            pool_name=pool_name,
            blockdevs=loop_path,
            command=stratis.pool_create,
            errors=errors,
        )

    else:
        atomic_run(
            f"Creating pool: {pool_name}",
            pool_name=pool_name,
            blockdevs=loop_path,
            no_overprovision=True,
            command=stratis.pool_create,
            errors=errors,
        )

    # for an approximate result in MiB, divide loopdev_size value by 1.049. Then divide
    # result with fs size to get how many fs we should create in order to fill pool.
    # pool always takes ~500MiB when created, so this formula should execute 1 or 2
    # fs create commands that will fail.
    num_of_filesystems = int((loopdev_size / 1.049) / fs_size)
    for fs in range(num_of_filesystems):
        stratis.fs_create(
            pool_name=pool_name,
            fs_name=f"fs{fs}",
            fs_size=f"{fs_size}MiB",
        )

    atomic_run(
        "Creating FS, this should fail because doesn't have enough space",
        expected_out=["Error: Command failed:", "No space left on device"],
        expected_ret=1,
        pool_name=pool_name,
        fs_name=fs_name,
        command=stratis.fs_create,
        errors=errors,
    )

    atomic_run(f"Creating dir: {mount_dir}", new_dir=mount_dir, command=mkdir, errors=errors)

    atomic_run(
        f"Mounting filesystem: {fs_name}",
        device=stratis_fs_path,
        mountpoint=mount_dir,
        command=mount,
        errors=errors,
    )

    # at this point fs snapshot should fail as well because pool has not enough space
    atomic_run(
        "Creating FS snapshot, this should fail because doesn't have enough space",
        expected_ret=1,
        # expected_out="",
        pool_name=pool_name,
        snapshot_name="snap1",
        origin_name="fs1",
        command=stratis.fs_snapshot,
        errors=errors,
    )

    atomic_run("Unmounting filesystem", mountpoint=mount_dir, command=umount, errors=errors)

    for fs in range(num_of_filesystems):
        atomic_run(
            f"Destroying filesystem: fs{fs}",
            pool_name=pool_name,
            fs_name=f"fs{fs}",
            command=stratis.fs_destroy,
            errors=errors,
        )

    atomic_run(
        f"Destroying pool: {pool_name}",
        pool_name=pool_name,
        command=stratis.pool_destroy,
        errors=errors,
    )

    atomic_run("Removing loopdev", name=loop_path, command=delete_loopdev, errors=errors)

    return errors


if __name__ == "__main__":
    errs = pool_out_of_space()
    exit(parse_ret(errs))
