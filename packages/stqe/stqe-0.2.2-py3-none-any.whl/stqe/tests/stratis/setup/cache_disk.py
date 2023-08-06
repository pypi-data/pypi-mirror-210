#!/usr/bin/python


import time

from libsan.host.cmdline import run
from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_env, read_var, write_var


def create_cache_disk():
    errors = []
    stratis = Stratis()
    pool_name = read_env("fmf_pool_name")

    id = ""
    try:
        id = "_" + str(read_env("fmf_id"))
        pool_name = pool_name + id
    except KeyError:
        pass

    previous = ""
    try:
        previous = int(id[1:]) - 1
        previous = "" if previous == 1 else "_" + str(previous)
    except ValueError:
        pass
    print(f"previous is {previous}, id is {id},")
    blockdevs = read_var("STRATIS_FREE")

    if "init_cache" in read_env("fmf_name"):
        if not isinstance(blockdevs, list):
            blockdevs = [blockdevs]
        if blockdevs:
            cache_disk = blockdevs.pop()
            atomic_run(
                "Writing var STRATIS_FREE",
                command=write_var,
                var={"STRATIS_FREE": blockdevs},
                errors=errors,
            )

    time.sleep(2)
    atomic_run(
        message="Triggering udev",
        command=run,
        cmd="udevadm trigger; udevadm settle",
        errors=errors,
    )

    atomic_run(
        "statis pool init cache %s." % pool_name,
        command=stratis.pool_init_cache,
        pool_name=pool_name,
        blockdevs=cache_disk,
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = create_cache_disk()
    exit(parse_ret(errs))
