#!/usr/bin/python


from os import environ

from libsan.host.lio import TargetCLI

from stqe.host.atomic_run import atomic_run, parse_ret


def saveconfig_create():
    errors = []
    target = TargetCLI(path="")

    args = {"savefile": None}
    try:
        args["savefile"] = environ["fmf_savefile_name"]
    except KeyError:
        pass

    atomic_run("Creating saveconfig", command=target.saveconfig, errors=errors, **target.remove_nones(args))

    return errors


if __name__ == "__main__":
    errs = saveconfig_create()
    exit(parse_ret(errs))
