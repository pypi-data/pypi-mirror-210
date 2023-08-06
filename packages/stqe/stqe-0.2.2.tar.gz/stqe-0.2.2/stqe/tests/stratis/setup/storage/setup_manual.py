#!/usr/bin/python


from stqe.host.atomic_run import parse_ret
from stqe.host.persistent_vars import clean_var, read_var, write_var


def setup_manual():
    # this just checks if the device is created.
    data = read_var("STRATIS_DEVICE")

    # remove newline
    if data.endswith("\n"):
        data = data.rstrip("\n")
        clean_var("STRATIS_DEVICE")
        write_var({"STRATIS_DEVICE": data})

    print("INFO: Will run tests on device: '%s'" % data)
    return []


if __name__ == "__main__":
    errs = setup_manual()
    exit(parse_ret(errs))
