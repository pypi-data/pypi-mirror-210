#!/usr/bin/python


from os import environ

from libsan.host.lsm import LibStorageMgmt

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.lsm import yield_lsm_config


def plugin_info_success():
    errors = []
    for config in yield_lsm_config():
        lsm = LibStorageMgmt(disable_check=True, **config)
        atomic_run(
            "Using LSM to get plugin info with protocol %s" % config["protocol"],
            command=lsm.plugin_info,
            errors=errors,
        )
    return errors


if __name__ == "__main__":
    if int(environ["fmf_tier"]) == 1:
        errs = plugin_info_success()
    exit(parse_ret(errs))
