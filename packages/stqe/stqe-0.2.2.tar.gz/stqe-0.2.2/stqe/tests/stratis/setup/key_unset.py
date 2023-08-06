from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import clean_var, read_env, read_var


def generate_key():
    errors = []
    id = ""
    stratis = Stratis()

    try:
        id = "_" + str(read_env("fmf_key_id"))
    except KeyError:
        pass

    key_desc = read_var(f"STRATIS_KEY_DESC{id}")
    keyfile_name = read_var(f"STRATIS_KEYFILE{id}")

    atomic_run(
        f"Unsetting stratis key {key_desc}.",
        command=stratis.key_unset,
        key_desc=key_desc,
        errors=errors,
    )

    atomic_run(
        f"Cleaning var STRATIS_KEYFILE{id}",
        command=clean_var,
        var=f"STRATIS_KEYFILE{id}",
        errors=errors,
    )

    atomic_run(
        f"Cleaning var STRATIS_KEYFILE_PATH{id}",
        command=clean_var,
        var=f"STRATIS_KEYFILE_PATH{id}",
        errors=errors,
    )

    atomic_run(
        f"Cleaning var STRATIS_KEYFILE{id}",
        command=clean_var,
        var=f"{keyfile_name}",
        errors=errors,
    )

    atomic_run(
        f"Cleaning var STRATIS_KEY_DESC{id}",
        command=clean_var,
        var=f"STRATIS_KEY_DESC{id}",
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = generate_key()
    exit(parse_ret(errs))
