#!/usr/bin/python

# This is a reproducer for Bug 1456019
# [Pegas1.0 EA2] cache_dump crashes with SIGSEGV when passed small file as an argument

# !/usr/bin/python

import sys

from libsan.host.cmdline import run
from libsan.host.linux import install_package

import stqe.host.tc
from stqe.host.atomic_run import atomic_run
from stqe.host.tc import TestClass

global tc


def cache_dump_test(tc):
    print("\n#######################################\n")
    print("INFO: Testing cache_dump for SIGSEV.")

    errors = []

    arguments = [
        {
            "message": "Creating very small file to dump to.",
            "cmd": "fallocate -l 200 /var/tmp/small_file",
            "command": run,
        },
        {
            "message": "Dumping metadata from small file",
            "cmd": "cache_dump /var/tmp/small_file",
            "command": run,
        },
        {
            "message": "Removing small file",
            "cmd": "rm -f /var/tmp/small_file",
            "command": run,
        },
    ]

    for argument in arguments:
        atomic_run(errors=errors, **argument)

    print("\n#######################################\n")

    if len(errors) == 0:
        tc.tpass("Testing cache_dump for SIGSEV passed.")
    else:
        tc.tfail(
            "Testing cache_dump for SIGSEV failed with following errors: \n\t'" + "\n\t ".join([str(i) for i in errors])
        )
        return 1
    return 0


def thin_dump_test(tc):
    print("\n#######################################\n")
    print("INFO: Testing thin_dump for SIGSEV.")

    errors = []

    arguments = [
        {
            "message": "Creating very small file to dump to.",
            "cmd": "fallocate -l 200 /var/tmp/small_file",
            "command": run,
        },
        {
            "message": "Dumping metadata from small file",
            "cmd": "thin_dump /var/tmp/small_file",
            "command": run,
        },
        {
            "message": "Removing small file",
            "cmd": "rm -f /var/tmp/small_file",
            "command": run,
        },
    ]

    for argument in arguments:
        atomic_run(errors=errors, **argument)

    print("\n#######################################\n")

    if len(errors) == 0:
        tc.tpass("Testing thin_dump for SIGSEV passed.")
    else:
        tc.tfail(
            "Testing thin_dump for SIGSEV failed with following errors: \n\t'" + "\n\t ".join([str(i) for i in errors])
        )
        return 1
    return 0


def main():
    # Initialize Test Case
    test_class: TestClass = stqe.host.tc.TestClass()

    install_package("device-mapper-persistent-data")

    cache_dump_test(tc=test_class)
    thin_dump_test(tc=test_class)

    if not test_class.tend():
        print("FAIL: Test failed")
        sys.exit(1)

    print("PASS: Test passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
