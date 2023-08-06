#!/usr/bin/python


from libsan.host.qemu_img import delete_image

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import read_var


def delete_qcow():
    errors = []

    name = read_var("IMAGE_NAME")
    path = read_var("IMAGE_PATH")

    atomic_run(
        "Deleting qcow image %s" % name,
        name=name,
        image_path=path,
        command=delete_image,
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = delete_qcow()
    exit(parse_ret(errs))
