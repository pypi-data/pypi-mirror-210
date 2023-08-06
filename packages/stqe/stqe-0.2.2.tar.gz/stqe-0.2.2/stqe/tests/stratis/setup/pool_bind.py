#!/usr/bin/python


from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_env, read_var


def bind_pool():
    errors = []
    key_desc = ""
    trust_url = None
    binding_method = None
    tang_url = None
    thumbprint = None
    stratis = Stratis()

    pool_name = read_var(read_env("fmf_pool_name"))
    try:
        key_desc = read_env("fmf_key_desc")
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
        binding_method = read_env("fmf_binding_method")
    except KeyError:
        pass
    try:
        tang_url = read_var(read_env("fmf_tang_url"))
    except KeyError:
        pass

    atomic_run(
        "Creating stratis pool %s." % pool_name,
        command=stratis.pool_bind,
        pool_name=pool_name,
        key_desc=key_desc,
        binding_method=binding_method,
        thumbprint=thumbprint,
        tang_url=tang_url,
        trust_url=trust_url,
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = bind_pool()
    exit(parse_ret(errs))
