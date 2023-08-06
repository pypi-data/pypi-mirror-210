#!/usr/bin/python


from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_env, read_var


def restart_pool():
    errors = []
    stratis = Stratis()
    pool_name = None
    pool_uuid = None
    unlock_method = None

    try:
        pool_name = read_env("fmf_pool_name")
    except KeyError:
        pass
    if not pool_name:
        try:
            pool_name = read_var("STRATIS_POOL")
            pool_uuid = read_var("STRATIS_POOL_UUID")
        except KeyError:
            pass
    if not pool_uuid:
        pool_uuid = stratis.get_pool_uuid(pool_name=pool_name)
    try:
        unlock_method = read_env("fmf_unlock_method")
    except KeyError:
        pass

    atomic_run(
        "Stopping stratis pool %s." % pool_name,
        command=stratis.pool_stop,
        pool_name=pool_name,
        errors=errors,
    )

    atomic_run(
        "Starting stratis pool %s." % pool_name,
        command=stratis.pool_start,
        unlock_method=unlock_method,
        pool_uuid=pool_uuid,
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = restart_pool()
    exit(parse_ret(errs))
