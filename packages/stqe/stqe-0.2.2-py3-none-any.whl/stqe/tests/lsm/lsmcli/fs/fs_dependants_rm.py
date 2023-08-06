#!/usr/bin/python


from os import environ

from libsan.host.lsm import LibStorageMgmt

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.lsm import yield_lsm_config
from stqe.host.persistent_vars import read_var


def fs_dependants_rm_success():
    errors = []

    fs_id = read_var("LSM_FS_ID")
    fs_cloned_name = read_var("LSM_FS_CLONED_NAME")

    for config in yield_lsm_config():
        lsm = LibStorageMgmt(disable_check=True, **config)

        _, data = atomic_run(
            f"Cloning FS {fs_id} to FS {fs_cloned_name}.",
            command=lsm.fs_clone,
            src_fs=fs_id,
            dst_name=fs_cloned_name,
            return_output=True,
            errors=errors,
        )
        fs_cloned_id = [line.split()[0].strip() for line in data.splitlines() if fs_cloned_name in line][0]

        atomic_run(
            "Removing dependants of FS {} with protocol {}.".format(fs_id, config["protocol"]),
            command=lsm.fs_dependants_rm,
            fs=fs_id,
            errors=errors,
        )

        # this should return 'False', because we just removed the dependant
        _, data = atomic_run(
            "Checking dependants of FS {} with protocol {}.".format(fs_id, config["protocol"]),
            command=lsm.fs_dependants,
            fs=fs_id,
            return_output=True,
            errors=errors,
        )
        if data != "False":
            errors.append(
                "Removing dependants of FS {} did not return 'False', but {}."
                " Dependants did not get removed.".format(fs_id, data),
            )

        # FIXME: Add removing dependants for file

        atomic_run(
            "Removing cloned FS {} with protocol {}.".format(fs_cloned_name, config["protocol"]),
            command=lsm.fs_delete,
            fs=fs_cloned_id,
            force=True,
            errors=errors,
        )

    return errors


def fs_dependants_rm_fail():
    errors = []

    fs_name = read_var("LSM_FS_NAME")

    for config in yield_lsm_config():
        lsm = LibStorageMgmt(disable_check=True, **config)

        arguments = [
            {
                "message": "Trying to fail removing dependants without any paramethers with protocol %s"
                % config["protocol"],
                "command": lsm.fs_dependants_rm,
            },
            {
                "message": "Trying to fail removing dependants FS with wrong 'fs' 'wrong' with protocol %s"
                % config["protocol"],
                "command": lsm.fs_dependants_rm,
                "fs": "wrong",
            },
            {
                "message": "Trying to fail removing dependants FS with 'fs' name instead of ID with protocol %s"
                % config["protocol"],
                "command": lsm.fs_dependants_rm,
                "fs": fs_name,
            },
        ]
        for argument in arguments:
            atomic_run(expected_ret=2, errors=errors, **argument)
    return errors


def fs_dependants_rm_fail_no_state_change():
    errors = []

    fs_id = read_var("LSM_FS_ID")
    fs_cloned_name = read_var("LSM_FS_CLONED_NAME")

    for config in yield_lsm_config():
        lsm = LibStorageMgmt(disable_check=True, **config)

        atomic_run(
            "Removing dependants of FS {} with protocol {} to hit NO_STATE_CHANGE.".format(fs_id, config["protocol"]),
            command=lsm.fs_dependants_rm,
            fs=fs_id,
            expected_ret=4,
            errors=errors,
        )

        _, data = atomic_run(
            f"Cloning FS {fs_id} to FS {fs_cloned_name}.",
            command=lsm.fs_clone,
            src_fs=fs_id,
            dst_name=fs_cloned_name,
            return_output=True,
            errors=errors,
        )
        fs_cloned_id = [line.split()[0].strip() for line in data.splitlines() if fs_cloned_name in line][0]

        atomic_run(
            "Removing dependants of FS {} with protocol {}.".format(fs_id, config["protocol"]),
            command=lsm.fs_dependants_rm,
            fs=fs_id,
            errors=errors,
        )

        atomic_run(
            "Removing cloned FS {} with protocol {}.".format(fs_cloned_name, config["protocol"]),
            command=lsm.fs_delete,
            fs=fs_cloned_id,
            force=True,
            errors=errors,
        )
    return errors


if __name__ == "__main__":
    if int(environ["fmf_tier"]) == 1:
        errs = fs_dependants_rm_success()
    if int(environ["fmf_tier"]) == 2:
        errs = fs_dependants_rm_fail()
        errs += fs_dependants_rm_fail_no_state_change()
    exit(parse_ret(errs))
