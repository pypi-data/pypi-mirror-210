#!/usr/bin/python


from libsan.host.lio import TargetCLI

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import clean_var, read_var


def disable_chap():
    errors = []
    target_iqn = read_var("TARGET_IQN")
    tpg = read_var("TPG")

    target = TargetCLI(path="/iscsi")

    atomic_run(
        "Disabling discovery_auth",
        enable=0,
        group="discovery_auth",
        command=target.set,
        errors=errors,
    )

    target.path = "/iscsi/" + target_iqn + "/" + tpg

    atomic_run(
        "Disabling authentication",
        group="attribute",
        authentication=0,
        command=target.set,
        errors=errors,
    )

    for i in [
        "CHAP_MUTUAL_USERID",
        "CHAP_MUTUAL_PASSWORD",
        "CHAP_PASSWORD",
        "CHAP_USERID",
    ]:
        try:
            atomic_run(
                "Removing var: %s from /tmp" % i,
                var=i,
                command=clean_var,
                errors=errors,
            )
        except OSError:
            pass

    return errors


if __name__ == "__main__":
    errs = disable_chap()
    exit(parse_ret(errs))
