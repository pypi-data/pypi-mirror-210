#!/usr/bin/python


import time

from libsan.host.cmdline import run
from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_env, read_var, write_var


def create_pool():
    errors = []
    key_desc = ""
    trust_url = None
    clevis = None
    tang_url = None
    thumbprint = None
    no_overprovision = None
    stratis = Stratis()

    pool_name = read_env("fmf_pool_name")
    id = ""
    try:
        id = "_" + str(read_env("fmf_pool_id"))
        pool_name = pool_name + id
    except KeyError:
        pass
    try:
        key_desc = read_var(read_env("fmf_key_desc"))
    except KeyError:
        pass
    try:
        trust_url = read_env("fmf_trust_url")
    except KeyError:
        pass
    try:
        thumbprint = read_var(read_env("fmf_thumbprint"))
    except KeyError:
        pass
    try:
        clevis = read_env("fmf_clevis")
    except KeyError:
        pass
    try:
        tang_url = read_var(read_env("fmf_tang_url"))
    except KeyError:
        pass
    try:
        no_overprovision = read_env("fmf_no_overprovision")
    except KeyError:
        pass

    if thumbprint and trust_url:
        trust_url = None

    previous = ""
    try:
        previous = int(id[1:]) - 1
        previous = "" if previous == 1 else "_" + str(previous)
    except ValueError:
        pass
    if previous:
        print(f"previous is {previous}, id is {id},")
    blockdevs = read_var("STRATIS_FREE")
    if blockdevs is None:
        blockdevs = read_var("STRATIS_DEVICE")

    if "single" in read_env("fmf_name"):
        if not isinstance(blockdevs, list):
            blockdevs = [blockdevs]
        blockdevs = [blockdev for blockdev in blockdevs if blockdev]
        free = blockdevs[:]
        blockdevs = free.pop()
        atomic_run(
            "Writing var STRATIS_FREE",
            command=write_var,
            var={"STRATIS_FREE": free},
            errors=errors,
        )
        atomic_run(
            "Writing var STRATIS_DEVICE",
            command=write_var,
            var={"STRATIS_DEVICE": blockdevs},
            errors=errors,
        )

    time.sleep(2)
    atomic_run(
        message="Triggering udev",
        command=run,
        cmd="udevadm trigger; udevadm settle",
        errors=errors,
    )
    if clevis or key_desc:
        atomic_run(
            "Creating stratis pool %s." % pool_name,
            command=stratis.pool_create,
            pool_name=pool_name,
            blockdevs=blockdevs,
            key_desc=key_desc,
            clevis=clevis,
            thumbprint=thumbprint,
            tang_url=tang_url,
            trust_url=trust_url,
            no_overprovision=no_overprovision,
            errors=errors,
        )
    else:
        atomic_run(
            "Creating stratis pool %s." % pool_name,
            command=stratis.pool_create,
            pool_name=pool_name,
            no_overprovision=no_overprovision,
            blockdevs=blockdevs,
            errors=errors,
        )

    atomic_run(
        "Writing var STRATIS_POOL%s" % id,
        command=write_var,
        var={"STRATIS_POOL%s" % id: pool_name},
        errors=errors,
    )

    pool_uuid = stratis.get_pool_uuid(pool_name)

    atomic_run(
        "Writing var STRATIS_POOL_UUID",
        command=write_var,
        var={"STRATIS_POOL_UUID": pool_uuid},
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = create_pool()
    exit(parse_ret(errs))
