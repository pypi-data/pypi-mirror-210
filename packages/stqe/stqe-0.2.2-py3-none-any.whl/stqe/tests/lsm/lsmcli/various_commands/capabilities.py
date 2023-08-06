#!/usr/bin/python


from os import environ

from libsan.host.lsm import LibStorageMgmt

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.lsm import yield_lsm_config
from stqe.host.persistent_vars import read_var


def capabilities_success():
    errors = []

    sys = read_var("LSM_SYS_ID")

    for config in yield_lsm_config():
        lsm = LibStorageMgmt(disable_check=True, **config)
        atomic_run(
            "Getting capabilities of system {} with protocol {}".format(sys, config["protocol"]),
            command=lsm.capabilities,
            sys=sys,
            errors=errors,
        )
    return errors


def capabilities_fail():
    errors = []

    for config in yield_lsm_config():
        lsm = LibStorageMgmt(disable_check=True, **config)

        arguments = [
            {
                "message": "Trying to fail getting capabilities of system without any paramethers with protocol %s"
                % config["protocol"],
                "command": lsm.capabilities,
            },
            {
                "message": "Trying to fail getting capabilities of system with WRONG system with protocol %s"
                % config["protocol"],
                "sys": "WRONG",
                "command": lsm.capabilities,
            },
        ]
        for argument in arguments:
            atomic_run(expected_ret=2, errors=errors, **argument)
    return errors


if __name__ == "__main__":
    if int(environ["fmf_tier"]) == 1:
        errs = capabilities_success()
    if int(environ["fmf_tier"]) == 2:
        errs = capabilities_fail()
    exit(parse_ret(errs))
