#!/usr/bin/python


from libsan.host.dmpd import DMPD

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.fmf_tools import get_env_args, get_func_from_string
from stqe.host.lvm import get_dmpd_args


def dmpd_cli():
    errors = []
    dmpd = DMPD()
    args = get_dmpd_args(dmpd_object=dmpd)
    args.update(get_env_args({"source_vg": str, "source_lv": str, "source_file": str}))
    if args["command"] == "thin_trim":
        args["data_dev"] = f'{args["data_dev"]}_tdata'
    args["command"] = get_func_from_string(dmpd, args.pop("command"), local_functions=globals())

    atomic_run(errors=errors, **args)

    return errors


if __name__ == "__main__":
    errs = dmpd_cli()
    exit(parse_ret(errs))
