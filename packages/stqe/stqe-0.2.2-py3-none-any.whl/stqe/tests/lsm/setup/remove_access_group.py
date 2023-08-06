#!/usr/bin/python


from os import environ

from libsan.host.lsm import LibStorageMgmt

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.lsm import yield_lsm_config
from stqe.host.persistent_vars import clean_var, read_var


def remove_fs():
    print("INFO: Removing AG.")
    errors = []

    var_name = "LSM_" + environ["fmf_ag_id"]
    ag_id = read_var(var_name)

    lsm = LibStorageMgmt(disable_check=True, **list(yield_lsm_config())[0])

    atomic_run(
        "Removing AG '%s'." % ag_id,
        command=lsm.access_group_delete,
        ag=ag_id,
        force=True,
        errors=errors,
    )

    atomic_run("Removing var %s" % var_name, command=clean_var, var=var_name, errors=errors)

    return errors


if __name__ == "__main__":
    errs = remove_fs()
    exit(parse_ret(errs))
