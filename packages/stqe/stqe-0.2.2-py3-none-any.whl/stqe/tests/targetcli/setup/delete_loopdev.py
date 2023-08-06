#!/usr/bin/python


from libsan.host.loopdev import delete_loopdev

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_var


def loopdev_delete():
    errors = []

    name = read_var("TARGETCLI_LOOPDEV_NAME")

    atomic_run("Deleting loopdev %s" % name, command=delete_loopdev, name=name, errors=errors)

    return errors


if __name__ == "__main__":
    errs = loopdev_delete()
    exit(parse_ret(errs))
