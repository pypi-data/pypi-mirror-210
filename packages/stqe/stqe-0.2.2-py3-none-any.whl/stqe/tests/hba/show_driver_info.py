#!/usr/bin/python -u

# Copyright (C) 2016 Red Hat, Inc.
# python-stqe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-stqe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-stqe.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Bruno Goncalves   <bgoncalv@redhat.com>


import argparse
import re
import subprocess
import sys

from libsan import sanmgmt
from libsan.host import mp
from libsan.host.cmdline import run

import stqe.host.logchecker as log


def _print(string):
    module_name = __name__
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)

    # Append time information to command
    date = 'date "+%Y-%m-%d %H:%M:%S"'
    p = subprocess.Popen(date, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, _ = p.communicate()
    stdout = stdout.decode("ascii", "ignore")
    stdout = stdout.rstrip("\n")

    print(f"[{stdout}] {string}")

    sys.stdout.flush()
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def execute_test(mpath_name):
    mp_info = mp.multipath_query_all(mpath_name)
    if not mp_info:
        _print("FAIL: Got NULL from query_mp_info(%s)" % mpath_name)
        return False

    _print("INFO: Going to process the SCSI drivers used by the multipath (%s)" % mpath_name)

    # _print("DEBUG: dump mp_info")
    # print mp_info

    error = False

    if "scsi_drivers" in mp_info:
        for driver in mp_info["scsi_drivers"]:
            _print("INFO: Showing information for %s driver" % driver)
            if run("modinfo %s" % driver) != 0:
                _print("FAIL: Could not show info for %s" % driver)
                error = True
    else:
        _print("FAIL: Could not find out the drivers used by %s" % mpath_name)
        error = True

    if not error:
        _print("INFO: test on %s PASS" % mpath_name)

    if not log.check_all():
        _print("FAIL: detected error on logchecker")
        return False

    if error:
        _print("FAIL: test case sys/show_driver_info on %s" % mpath_name)
        return False

    _print("PASS: test case sys/show_driver_info on %s" % mpath_name)
    return True


def main():
    """ """
    pass_retcode = 0
    fail_retcode = 1

    parser = argparse.ArgumentParser(description="add new num")
    parser.add_argument(
        "--mpath-name",
        "-m",
        required=False,
        dest="mpath_name",
        help="Name of multipath device to query",
        metavar="mpath",
    )

    args = parser.parse_args()

    mpath_name_list = []
    if args.mpath_name:
        mpath_name_list.append(args.mpath_name)

    # If not mpath was specified search for them on the system
    if not mpath_name_list:
        choosen_devs = sanmgmt.choose_mpaths()
        if not choosen_devs:
            _print("FAIL: Could not find any multipath device to use as base LUN")
            sys.exit(fail_retcode)
        mpath_name_list = list(choosen_devs.keys())

    if not mpath_name_list:
        _print("FAIL: Could not find any multipath device to use")
        sys.exit(fail_retcode)

    error = 0
    for mpath_name in mpath_name_list:
        if not execute_test(mpath_name):
            error = +1

    if error:
        sys.exit(fail_retcode)

    sys.exit(pass_retcode)


main()
