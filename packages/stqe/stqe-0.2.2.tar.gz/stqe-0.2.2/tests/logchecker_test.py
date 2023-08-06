# Copyright (C) 2022 Red Hat, Inc.
# This file is part of libsan.
#
# libsan is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libsan is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libsan.  If not, see <http://www.gnu.org/licenses/>.


import unittest
from unittest.mock import call, patch

import stqe.host.logchecker as log_checker
from libsan.host.cmdline import run

# found segfault
segfault_msg = (
    " segfault at 10 ip 00007f9bebcca90d sp 00007fffb62705f0 error 4 in libQtWebKit.so.4.5.2[7f9beb83a000+f6f000]"
)
calltrace_msg = " Call Trace: "


def _run_dmesg_segfault(cmd, **kwargs):
    if cmd.startswith("dmesg | grep"):
        cmd = cmd.replace("dmesg", "echo '%s'" % segfault_msg)
        return run(cmd, verbose=False, **kwargs)

    return (0, "")


def _run_dmesg_calltrace(cmd, **kwargs):
    if cmd.startswith("dmesg | grep"):
        cmd = cmd.replace("dmesg", "echo '%s'" % calltrace_msg)
        return run(cmd, verbose=False, **kwargs)

    return (0, "")


class Testlogchecker(unittest.TestCase):
    @patch("stqe.host.logchecker.run")
    def test_kernel_check(self, run_func):
        run_func.return_value = (0, 0)
        assert log_checker.kernel_check() is True
        # already handled taint
        run_func.return_value = (0, 1)
        assert log_checker.kernel_check() is True

    @patch("stqe.host.logchecker.run")
    def test_dmesg_check(self, run_func):
        run_func.return_value = (0, "")
        assert log_checker.dmesg_check() is True
        run_func.reset_mock()

        run_func.side_effect = _run_dmesg_segfault
        assert log_checker.dmesg_check() is False
        run_calls = [
            call("dmesg | grep -i ' segfault '", return_output=True),
            call("echo '\nINFO found  segfault   Saving it\n'>> dmesg.log"),
            call("dmesg >> dmesg.log"),
            call("dmesg | grep -i 'Call Trace:'", return_output=True),
        ]
        # print(run_func.call_args_list)
        run_func.assert_has_calls(run_calls)
        run_func.reset_mock()

        run_func.side_effect = _run_dmesg_calltrace
        assert log_checker.dmesg_check() is False
        run_calls = [
            call("dmesg | grep -i ' segfault '", return_output=True),
            call("dmesg | grep -i 'Call Trace:'", return_output=True),
            call("echo '\nINFO found Call Trace:  Saving it\n'>> dmesg.log"),
            call("dmesg >> dmesg.log"),
        ]
        # print(run_func.call_args_list)
        run_func.assert_has_calls(run_calls)
        run_func.reset_mock()

    @patch("stqe.host.logchecker.kernel_check")
    def test_check_all(self, check_func):
        check_func.return_value = False
        assert log_checker.check_all() is False
