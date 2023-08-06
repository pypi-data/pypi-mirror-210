"""lvm.py: Module with test specific method for LVM."""

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

import re  # regex

from libsan.host import lvm
from libsan.host.cmdline import run

from stqe.host.fmf_tools import get_env_args
from stqe.host.persistent_vars import read_var


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


def check_lv_expected_value(test_obj, lv_name, vg_name, opt_val_dict):
    if not test_obj or not opt_val_dict or not lv_name or not vg_name:
        return

    opt_str = ",".join(opt_val_dict)
    lv_info = lvm.lv_info(lv_name, vg_name, options=opt_str)
    if not lv_info:
        test_obj.tfail(f"{vg_name}/{lv_name} does not exist")
        run("lvs -a -o +%s" % opt_str)
        return
    for opt in opt_val_dict:
        if lv_info[opt] == opt_val_dict[opt]:
            test_obj.tpass(f"{vg_name}/{lv_name} {opt} == {opt_val_dict[opt]}")
            continue

        if test_obj.tfail(f"{vg_name}/{lv_name} {opt} == {lv_info[opt]}, but expected {opt_val_dict[opt]}"):
            print(lv_info)
            run("lvs -a -o +%s" % opt_str)
            continue


def get_dmpd_args(dmpd_object):
    """
    Returns dict of arguments passed from FMF env vars
    :return: dict
    """
    arguments = dict(dmpd_object.arguments)
    return get_env_args(list(arguments), read_var("FILE_NAMES"), {})
