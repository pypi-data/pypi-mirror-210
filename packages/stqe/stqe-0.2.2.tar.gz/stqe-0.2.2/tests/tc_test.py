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


import io
import os
import sys
import unittest

from stqe.host import tc


class TestTC(unittest.TestCase):
    def test_init(self):
        test_obj = tc.TestClass()
        log_msg = "my test"
        test_obj.tpass(log_msg)
        test_obj.tfail(log_msg)
        test_obj.tskip(log_msg)
        # initializing it again should preserve the values
        test_obj = tc.TestClass()
        assert len(test_obj.tc_pass) == 1
        assert len(test_obj.tc_fail) == 1
        assert len(test_obj.tc_skip) == 1

        # initializing after tend should clear the values
        test_obj.tend()
        test_obj = tc.TestClass()
        assert len(test_obj.tc_pass) == 0
        assert len(test_obj.tc_fail) == 0
        assert len(test_obj.tc_skip) == 0

    def test_tlog(self):
        test_obj = tc.TestClass()

        log_msg = "my test"
        new_callable = io.StringIO()
        sys.stdout = new_callable
        test_obj.tlog(log_msg)
        sys.stdout = sys.__stdout__
        assert new_callable.getvalue() == f"{log_msg}\n"

    def test_tpass(self):
        test_obj = tc.TestClass()

        log_msg = "my test"
        new_callable = io.StringIO()
        sys.stdout = new_callable
        assert os.path.exists(test_obj.test_log) is False
        test_obj.tpass(log_msg)
        sys.stdout = sys.__stdout__
        assert new_callable.getvalue() == "{}{}\n".format(test_obj.tc_sup_status["pass"], log_msg)
        assert log_msg in open(test_obj.test_log).read()  # noqaSIM115
        os.remove(test_obj.test_log)

    def test_tfail(self):
        test_obj = tc.TestClass()

        log_msg = "my test"
        new_callable = io.StringIO()
        sys.stdout = new_callable
        assert os.path.exists(test_obj.test_log) is False
        test_obj.tfail(log_msg)
        sys.stdout = sys.__stdout__
        assert new_callable.getvalue() == "{}{}\n".format(test_obj.tc_sup_status["fail"], log_msg)
        assert log_msg in open(test_obj.test_log).read()  # noqaSIM115
        os.remove(test_obj.test_log)

    def test_tskip(self):
        test_obj = tc.TestClass()

        log_msg = "my test"
        new_callable = io.StringIO()
        sys.stdout = new_callable
        assert os.path.exists(test_obj.test_log) is False
        test_obj.tskip(log_msg)
        sys.stdout = sys.__stdout__
        assert new_callable.getvalue() == "{}{}\n".format(test_obj.tc_sup_status["skip"], log_msg)
        assert log_msg in open(test_obj.test_log).read()  # noqaSIM115
        os.remove(test_obj.test_log)

    def test_tend_pass(self):
        test_obj = tc.TestClass()
        log_msg = "my test"
        test_obj.tskip(log_msg)
        test_obj.tpass(log_msg)
        assert test_obj.tend() is True

    def test_tend_fail(self):
        test_obj = tc.TestClass()
        log_msg = "my test"
        test_obj.tskip(log_msg)
        test_obj.tfail(log_msg)
        test_obj.tpass(log_msg)
        assert test_obj.tend() is False

    def test_log_submit(self):
        test_obj = tc.TestClass()

        test_obj.log_submit(test_obj.test_log)
