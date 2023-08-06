import random

from libsan.host.stratis import Stratis

from stqe.host.atomic_run import atomic_run, parse_ret
from stqe.host.persistent_vars import (
    get_persistent_files_dir,
    read_env,
    write_file,
    write_var,
)


def generate_key():
    errors = []
    keyfile = None
    key_length = None
    key = ""
    key_desc = None
    id = ""
    stratis = Stratis()

    try:
        key_desc = read_env("fmf_key_desc")
    except KeyError:
        pass
    try:
        id = "_" + str(read_env("fmf_key_id"))
        key_desc = key_desc + id
    except KeyError:
        pass
    try:
        keyfile = f"{read_env('fmf_keyfile')}{id}"
    except KeyError:
        pass
    try:
        key_length = read_env("fmf_key_length")
    except KeyError:
        pass
    try:
        key = read_env("fmf_keyring_key")
    except KeyError:
        pass

    if not key:
        for _ in range(key_length):
            random_num = str(random.randint(0, 9))
            random_lower_char = chr(random.randint(97, 122))
            random_upper_char = chr(random.randint(65, 90))
            random_char = random.choice([random_num, random_lower_char, random_upper_char])[0]
            key += random_char

    directory = get_persistent_files_dir()
    print(f"INFO: Using key: {key}")
    atomic_run(
        f"Writing key: {key} into file: {directory}{keyfile}",
        command=write_file,
        file_name=f"{keyfile}",
        value=key,
        errors=errors,
    )

    atomic_run(
        f"Writing var STRATIS_KEYFILE{id}",
        command=write_var,
        var={f"STRATIS_KEYFILE{id}": f"{keyfile}"},
        errors=errors,
    )

    atomic_run(
        f"Writing var STRATIS_KEYFILE_PATH{id}",
        command=write_var,
        var={f"STRATIS_KEYFILE_PATH{id}": f"{directory}{keyfile}"},
        errors=errors,
    )

    atomic_run(
        f"Setting key with key_desc:{key_desc} and keyfile_path:{keyfile}.",
        command=stratis.key_set,
        keyfile_path=f"{directory}{keyfile}",
        key_desc=key_desc,
        errors=errors,
    )

    atomic_run(
        f"Writing var STRATIS_KEY_DESC{id}",
        command=write_var,
        var={f"STRATIS_KEY_DESC{id}": f"{key_desc}"},
        errors=errors,
    )

    return errors


if __name__ == "__main__":
    errs = generate_key()
    exit(parse_ret(errs))
