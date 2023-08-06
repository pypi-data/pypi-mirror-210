#!/usr/bin/python


from libsan.host.lio import TargetCLI

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_var


def loopback_cleanup():
    errors = []
    wwn = read_var("LOOPBACK_WWN")
    lun = "lun" + str(read_var("LOOPBACK_LUN"))
    target = TargetCLI(path="/loopback/%s/luns" % wwn)

    atomic_run("Deleting lun: %s" % lun, lun=lun, command=target.delete, errors=errors)

    target.path = "/loopback"

    atomic_run("Deleting loopback: %s" % wwn, wwn=wwn, command=target.delete, errors=errors)

    return errors


if __name__ == "__main__":
    errs = loopback_cleanup()
    exit(parse_ret(errs))
