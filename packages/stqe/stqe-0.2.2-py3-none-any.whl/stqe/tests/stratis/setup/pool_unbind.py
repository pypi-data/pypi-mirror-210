#!/usr/bin/python


from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_env, read_var


def unbind_pool():
    errors = []
    binding_method = None
    stratis = Stratis()

    pool_name = read_var(read_env("fmf_pool_name"))
    try:
        binding_method = read_env("fmf_binding_method")
    except KeyError:
        pass

    atomic_run(
        "Creating stratis pool %s." % pool_name,
        command=stratis.pool_unbind,
        pool_name=pool_name,
        binding_method=binding_method,
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = unbind_pool()
    exit(parse_ret(errs))
