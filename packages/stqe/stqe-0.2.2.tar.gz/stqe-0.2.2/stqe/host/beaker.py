"""beaker.py: Module to manage beaker."""

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

__author__ = "Bruno Goncalves"
__copyright__ = "Copyright (c) 2016 Red Hat, Inc. All rights reserved."

import os
import re  # regex

from libsan.host.cmdline import run

import stqe.host.restraint


def _print(string):
    module_name = __name__
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)
    return


def get_task_timeout(task_id):
    """Get how much time the task still has
    Parameter:
    \ttask_id:          Beaker Task ID
    Return:
    \tNone:             In case of some problem
    or
    \tint(value):       The remaining time in seconds.
    """
    if not stqe.host.restraint.is_restraint_job():
        return None

    if task_id is None:
        _print("FAIL: beaker get_task_timeout() - requires task_id as parameter")
        return None

    cmd = "bkr watchdog-show %s" % task_id
    ret, output = run(cmd, return_output=True, verbose=False)
    if ret != 0:
        _print("FAIL: beaker get_task_timeout() - Could not get beaker kill time")
        print(output)
        return None

    output_regex = re.compile(r"%s: (\d+)" % task_id)
    m = output_regex.match(output)
    if m:
        return int(m.group(1))
    _print("FAIL: beaker get_task_timeout() - Could not parse output:")
    print(output)
    return None


def get_task_status(task_id):
    """Requires beaker-client package installed and configured."""
    if not stqe.host.restraint.is_restraint_job():
        return None

    if not task_id:
        _print("FAIL: get_task_status() - requires task ID")
        return None

    cmd = "bkr job-results --prettyxml T:%s" % task_id
    ret, output = run(cmd, return_output=True, verbose=False)
    if ret != 0:
        _print("FAIL: get_task_status() - Could not get beaker task result for T:%s" % task_id)
        print(output)
        return None

    lines = output.split("\n")
    status_regex = re.compile(r"<task.*status=\"(\S+)\"")
    for line in lines:
        m = status_regex.match(line)
        if m:
            return m.group(1)
    return None


def console_log_check(error_mgs):
    """Checks for error messages on console log ("Call Trace and segfault")."""
    error = 0
    console_log_file = "/root/console.log"
    prev_console_log_file = "/root/console.log.prev"
    new_console_log_file = "/root/console.log.new"

    if not is_beaker_job():
        print("WARN: skip console_log_check as it doesn't seem to be a beaker job")
        return True

    lab_controller = os.environ["LAB_CONTROLLER"]
    recipe_id = os.environ["BEAKER_RECIPE_ID"]

    # get current console log
    url = f"http://{lab_controller}:8000/recipes/{recipe_id}/logs/console.log"

    if run(f"wget -q {url} -O {new_console_log_file}") != 0:
        print("INFO: Could not get console log")
        # return sucess if could not get console.log
        return True

    # if there was previous console log, we just check the new part
    run(
        "diff -N -n --unidirectional-new-file %s %s > %s"
        % (prev_console_log_file, new_console_log_file, console_log_file),
    )

    # backup the current full console.log
    # next time we run the test we will compare just
    # what has been appended to console.log
    run(f"mv -f {new_console_log_file} {prev_console_log_file}")

    print("INFO: Checking for errors on %s" % console_log_file)
    for msg in error_mgs:
        _, output = run(f"cat {console_log_file} | grep -i '{msg}'", return_output=True)
        if output:
            print(f"INFO found {msg} on {console_log_file}")
            stqe.host.restraint.log_submit(console_log_file)
            error = +1

    if error:
        return False

    print("PASS: No errors on %s have been found." % console_log_file)
    return True


def is_beaker_job():
    """Checks if it is beaker job."""
    need_env = ["BEAKER", "BEAKER_RECIPE_ID", "LAB_CONTROLLER"]
    return all(not var not in os.environ for var in need_env)
