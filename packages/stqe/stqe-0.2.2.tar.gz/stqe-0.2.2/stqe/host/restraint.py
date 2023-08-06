"""restraint.py: Module to manage restraint."""

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

import libsan.host.linux
from libsan.host.cmdline import run


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


def update_killtime(kill_time):
    """Change beaker watchdog kill time
    Parameter:
    \tkill_time     new kill time in hours
    Return:
    \tTrue
    or
    \tFalse.
    """
    if not is_restraint_job():
        return False

    if not kill_time:
        kill_time = 1

    result_server = os.environ["RESULT_SERVER"]
    jobid = os.environ["RSTRNT_JOBID"]
    test = os.environ["RSTRNT_TASKNAME"]
    testid = os.environ["RSTRNT_TASKID"]

    host = libsan.host.linux.hostname()
    cmd = "rhts-test-checkin {} {} {} {} {} {}".format(
        result_server,
        host,
        jobid,
        test,
        kill_time,
        testid,
    )
    ret, output = run(cmd, return_output=True, verbose=False)
    if ret != 0:
        _print("FAIL: Could not update beaker kill time")
        print(output)
        return False
    _print("INFO: beaker_update_killtime() - Watchdog timer successfully updated to %d hours" % kill_time)
    return True


def log_submit(log_file):
    """upload log file."""
    if not is_restraint_job():
        return True

    if not log_file:
        _print("FAIL: log_submit() - requires log_file parameter")
        return False

    if not os.path.exists(log_file):
        _print("FAIL: log_submit() - file (%s) does not exist" % log_file)
        return False

    cmd = 'rhts-submit-log -l "%s"' % log_file
    ret, output = run(cmd, return_output=True, verbose=False)
    if ret != 0:
        _print("FAIL: Could not upload log %s" % log_file)
        print(output)
        return False
    _print("INFO: log_submit() - %s uploaded successfully" % log_file)
    return True


def get_recipe_id():
    """Get current recipe id
    Parameter:
    \tNone
    Return:
    \trecipe_id:          Restraint recipe ID
    or
    \tNone:               When not running using restraint.
    """
    if not is_restraint_job():
        return None
    return os.environ["RSTRNT_RECIPEID"]


def get_task_id():
    """Get current task id
    Parameter:
    \tNone
    Return:
    \ttask_id:          Beaker task ID
    or
    \tNone:             Some error occurred.
    """
    if not is_restraint_job():
        return None
    return os.environ["RSTRNT_TASKID"]


def is_restraint_job():
    """Checks if it is restraint job."""
    need_env = ["RSTRNT_TASKNAME", "RSTRNT_TASKID"]
    return all(not var not in os.environ for var in need_env)
