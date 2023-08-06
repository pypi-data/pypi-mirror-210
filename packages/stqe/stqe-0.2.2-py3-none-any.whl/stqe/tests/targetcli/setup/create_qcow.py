#!/usr/bin/python


from os import environ

from libsan.host.qemu_img import get_qcow_supported_options, qemu_create

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import write_var


def create_qemu_img():
    errors = []

    name = environ["fmf_filename"]
    size = environ["fmf_img_size"]
    supported_options = get_qcow_supported_options()
    args = {"fmt": None, "img_path": "/var/tmp"}
    for arg in args:
        try:
            args[arg] = environ["fmf_" + arg]
        except KeyError:
            pass
    for option in supported_options:
        try:
            args[option] = environ["fmf_" + option]
        except KeyError:
            pass

    atomic_run(
        "Creating qemu disk image %s" % name, filename=name, size=size, command=qemu_create, errors=errors, **args
    )

    atomic_run(
        "Writing var IMAGE_NAME",
        command=write_var,
        var={"IMAGE_NAME": name},
        errors=errors,
    )

    atomic_run(
        "Writing var IMAGE_PATH",
        command=write_var,
        var={"IMAGE_PATH": args["img_path"]},
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = create_qemu_img()
    exit(parse_ret(errs))
