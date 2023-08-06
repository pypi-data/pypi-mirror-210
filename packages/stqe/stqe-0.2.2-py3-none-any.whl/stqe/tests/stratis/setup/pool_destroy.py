#!/usr/bin/python


from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import clean_var, read_env, read_var, write_var


def destroy_pool():
    errors = []
    stratis = Stratis()

    id = ""
    try:
        id = "_" + str(read_env("fmf_pool_id"))
    except KeyError:
        pass
    pool_name = read_var("STRATIS_POOL%s" % id)

    if "single" in read_env("fmf_name"):
        available_devices = read_var("STRATIS_AVAILABLE_DEVICES")
        write_var({"STRATIS_DEVICE": available_devices})
        free = read_var("STRATIS_FREE")
        if free:
            clean_var("STRATIS_FREE")

    atomic_run(
        "Destroying stratis pool %s." % pool_name,
        command=stratis.pool_destroy,
        pool_name=pool_name,
        errors=errors,
    )

    atomic_run(
        "Cleaning var STRATIS_POOL%s" % id,
        command=clean_var,
        var="STRATIS_POOL%s" % id,
        errors=errors,
    )

    atomic_run(
        "Cleaning var STRATIS_POOL_UUID",
        command=clean_var,
        var="STRATIS_POOL_UUID",
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = destroy_pool()
    exit(parse_ret(errs))
