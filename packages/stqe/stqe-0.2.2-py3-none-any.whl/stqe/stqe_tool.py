#!/usr/bin/env python


import argparse
import sys

import stqe.host.nfs_lock as lock


def wait_nfs_lock(mpath, lock_type):
    print(f"Requesting NFS lock ({lock_type}) for mpath: {mpath}")
    lock_obj = lock.setup_nfs_lock_for_mpath(mpath)
    if not lock_obj:
        print("FAIL: Could not setup NFS lock for mpath: %s" % mpath)
        return False
    if not lock_obj.request_lock(lock_type):
        print(f"FAIL: Could not request lock: {lock_type} using {mpath}")
        return False
    print("INFO: Waiting for lock...")
    if not lock_obj.get_lock():
        print("FAIL: Could not get NFS lock")
        return False
    print("INFO: lock sucessfully acquired")
    return True


def release_nfs_lock(mpath, lock_type):
    print(f"Releasing NFS lock ({lock_type}) from mpath: {mpath}")
    lock_obj = lock.setup_nfs_lock_for_mpath(mpath)
    if not lock_obj:
        print("FAIL: Could not setup NFS lock for mpath: %s" % mpath)
        return False
    if not lock_obj.release_lock(lock_type):
        print(f"FAIL: Could not release lock: {lock_type} using {mpath}")
        return False
    print("INFO: Lock successfully released")
    return True


def main():
    parser = argparse.ArgumentParser(description="Tool useful for stqe environment")
    subparsers = parser.add_subparsers(help="Valid commands", dest="command")

    parser_wait_nfs_lock = subparsers.add_parser("wait-nfs-lock")
    parser_wait_nfs_lock.add_argument(
        "--mpath",
        "-m",
        required=True,
        dest="mpath",
        metavar="mpath_name",
        help="Mpath Name.",
    )
    parser_wait_nfs_lock.add_argument(
        "--lock-type",
        "-l",
        required=True,
        dest="lock_type",
        metavar="lock_type",
        help="Lock Type.",
    )

    parser_release_nfs_lock = subparsers.add_parser("release-nfs-lock")
    parser_release_nfs_lock.add_argument(
        "--mpath",
        "-m",
        required=True,
        dest="mpath",
        metavar="mpath_name",
        help="Mpath Name.",
    )
    parser_release_nfs_lock.add_argument(
        "--lock-type",
        "-l",
        required=True,
        dest="lock_type",
        metavar="lock_type",
        help="Lock Type.",
    )

    args = parser.parse_args()
    if args.command == "wait-nfs-lock":
        if wait_nfs_lock(args.mpath, args.lock_type):
            sys.exit(0)
        sys.exit(1)

    if args.command == "release-nfs-lock":
        if release_nfs_lock(args.mpath, args.lock_type):
            sys.exit(0)
        sys.exit(1)

    print("FAIL: Unsupported command: %s" % args.command)
    sys.exit(1)


main()
