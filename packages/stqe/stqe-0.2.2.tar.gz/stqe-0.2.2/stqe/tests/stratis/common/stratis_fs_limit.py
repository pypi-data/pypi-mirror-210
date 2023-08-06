#!/usr/bin/python


from libsan.host.loopdev import create_loopdev, delete_loopdev
from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret


def fs_limit():
    errors = []
    stratis = Stratis()
    dev = create_loopdev(size=10240)
    pool_name = "fs_limit"

    atomic_run(
        "Creating pool",
        pool_name=pool_name,
        blockdevs=dev,
        command=stratis.pool_create,
        errors=errors,
    )

    print("INFO: Creating 100 filesystems with 512MiB size.")
    for fs in range(0, 100):
        atomic_run(
            f"Creating filesystem: fs{fs}",
            pool_name=pool_name,
            fs_name=f"fs{fs}",
            fs_size="512MiB",
            command=stratis.fs_create,
            errors=errors,
        )

    atomic_run(
        "Creating fs number 101, this should fail because limit is set to 100 by default",
        expected_out=[
            "ERROR: The pool limit of 100 filesystems has already been reached; increase"
            " the filesystem limit on the pool to continue",
        ],
        expected_ret=1,
        pool_name=pool_name,
        fs_name="fs100",
        fs_size="512MiB",
        command=stratis.fs_create,
        errors=errors,
    )

    atomic_run(
        "Setting fs limit to 101",
        pool_name=pool_name,
        fs_amount=101,
        command=stratis.pool_set_fs_limit,
        errors=errors,
    )

    atomic_run(
        "Creating fs number 101, this should pass because limit has been set to 101",
        pool_name=pool_name,
        fs_name="fs100",
        fs_size="512MiB",
        command=stratis.fs_create,
        errors=errors,
    )

    atomic_run(
        "Creating fs number 102, this should fail because limit is set to 101",
        expected_out=[
            "ERROR: The pool limit of 101 filesystems has already been reached; increase"
            " the filesystem limit on the pool to continue",
        ],
        expected_ret=1,
        pool_name=pool_name,
        fs_name="fs101",
        fs_size="512MiB",
        command=stratis.fs_create,
        errors=errors,
    )

    for fs in range(0, 101):
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

    atomic_run("Removing loopdev", name=dev, command=delete_loopdev, errors=errors)

    return errors


if __name__ == "__main__":
    errs = fs_limit()
    exit(parse_ret(errs))
