#!/usr/bin/python


from os import environ

from libsan.host.lsm import LibStorageMgmt

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.lsm import yield_lsm_config
from stqe.host.persistent_vars import clean_var, read_var


def create_fs():
    print("INFO: Removing snapshot from FS.")
    errors = []

    snap_var_name = "LSM_" + environ["fmf_fs_snap_id"]
    fs_snap_id = read_var(snap_var_name)

    fs_id = read_var("LSM_" + environ["fmf_fs_id"])

    lsm = LibStorageMgmt(disable_check=True, **list(yield_lsm_config())[0])

    atomic_run(
        f"Removing snapshot {fs_snap_id} from FS {fs_id}",
        command=lsm.fs_snap_delete,
        snap=fs_snap_id,
        fs=fs_id,
        force=True,
        errors=errors,
    )

    atomic_run(
        "Removing var %s" % snap_var_name,
        command=clean_var,
        var=snap_var_name,
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = create_fs()
    exit(parse_ret(errs))
