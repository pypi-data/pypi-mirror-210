#!/usr/bin/python


from time import sleep

from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_var


def fs_limit():
    errors = []
    stratis = Stratis()
    number_of_iterations = 100
    pool_name = "pool_create_destroy"
    fs_name = "fs_create_destroy"
    blockdev = read_var("STRATIS_DEVICE")

    for i in range(number_of_iterations):
        print(f"INFO: Iteration number: {i}")
        atomic_run(
            "Creating pool",
            pool_name=pool_name,
            blockdevs=blockdev,
            command=stratis.pool_create,
            errors=errors,
        )

        sleep(1)

        atomic_run(
            "Destroying pool",
            pool_name=pool_name,
            command=stratis.pool_destroy,
            errors=errors,
        )

    atomic_run(
        "Creating pool",
        pool_name=pool_name,
        blockdevs=blockdev,
        command=stratis.pool_create,
        errors=errors,
    )

    for i in range(number_of_iterations):
        print(f"INFO: Iteration number: {i}")
        atomic_run(
            "Creating fs",
            pool_name=pool_name,
            fs_name=fs_name,
            command=stratis.fs_create,
            errors=errors,
        )

        sleep(1)

        atomic_run(
            "Destroying fs",
            pool_name=pool_name,
            fs_name=fs_name,
            command=stratis.fs_destroy,
            errors=errors,
        )

    atomic_run(
        "Destroying pool",
        pool_name=pool_name,
        command=stratis.pool_destroy,
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = fs_limit()
    exit(parse_ret(errs))
