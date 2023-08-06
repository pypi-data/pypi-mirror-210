#!/usr/bin/python -u
# Copyright (C) 2016 Red Hat, Inc.
# This file is part of python-stqe.
#
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

import argparse
import copy
import json
import os
import re
import signal
import subprocess
import sys
import threading
from os import listdir
from time import sleep
from typing import Tuple

from libsan.host import linux
from libsan.host.cmdline import run
from libsan.host.conf import load_config
from libsan.host.stratis import Stratis
from libsan.misc import time

from stqe.host import restraint
from stqe.host.fmf_tools import (
    TestNotFoundError,
    filter_tree,
    get_config,
    get_report,
    get_stqe_path,
    get_tests,
    get_tree,
)
from stqe.host.persistent_vars import read_var

stqe_path = get_stqe_path()
_IN_TREE_TESTS_DIR = stqe_path + "tests/"
_IN_TREE_CONF_DIR = stqe_path + "conf/"


def _get_python_executable() -> str:
    """Return name of the python executable based on a version info. If the major version is different from 3,
    return an empty string.

    :return: Return name of the python executable.
    :rtype: str
    """
    version = sys.version_info
    if version.major == 3:
        return "python3"
    else:
        print("FAIL: Unknown Python version, got %s.%s.%s" % (version[0:3]))
        return ""


def _load_test_cases() -> list:
    """Return a list with all test cases from IN_TREE_TESTS_DIR
    :return: List of test cases
    :rtype: list
    """
    supported_file_types = [".sh", ".py", ".pl"]
    exclude_filenames = ["__init__"]
    tests_dir = [x[0] for x in os.walk(_IN_TREE_TESTS_DIR)]

    test_cases = []
    # search for supported test files within the directory
    for test_dir in tests_dir:
        for output in listdir(test_dir):
            tmp = os.path.join(test_dir, output)
            if os.path.isfile(os.path.join(tmp)):
                filename, file_extension = os.path.splitext(tmp)
                _, basename = os.path.split(filename)
                if file_extension in supported_file_types and basename not in exclude_filenames:
                    filename = filename.replace(_IN_TREE_TESTS_DIR, "")
                    test_name = filename + file_extension
                    # add / to begin of the name to match what is returned by test config
                    # test_name = "/" + test_name
                    test_cases.append(test_name)
    return test_cases


def _list_all_test_cases() -> None:
    """Print all test cases from IN_TREE_TESTS_DIR."""
    test_cases = _load_test_cases()
    print("INFO: Showing all test files")
    for tc in test_cases:
        print("--> %s" % tc)


def _list_all_test_conf() -> None:
    """Print all test config files that it found in _IN_TREE_CONF_DIR."""
    supported_file_types = [".conf"]
    exclude_filenames = ["__init__"]
    confs_dir = [x[0] for x in os.walk(_IN_TREE_CONF_DIR)]

    print("INFO: Showing all test config files")
    for conf_dir in confs_dir:
        for entry in listdir(conf_dir):
            tmp = os.path.join(conf_dir, entry)
            if os.path.isfile(os.path.join(tmp)):
                filename, file_extension = os.path.splitext(tmp)
                _, basename = os.path.split(filename)
                if file_extension in supported_file_types and basename not in exclude_filenames:
                    filename = filename.replace(_IN_TREE_CONF_DIR, "")
                    conf_name = filename + file_extension
                    print("--> %s" % conf_name)


def _load_test_conf(config_file="") -> list:
    """Return a list of test cases from a config file. If :param config_file is not provided,
    return all test cases from _IN_TREE_TESTS_DIR.

    :param config_file: Name of the conf file from _IN_TREE_CONF_DIR
    :type config_file: str
    :return: List of test cases
    :rtype: list
    """
    if not config_file:
        # return all supported test cases, without any test parameters
        test_cases = _load_test_cases()
        tc_conf = []
        for tc in test_cases:
            tc_dict = {}
            tc_dict["name"] = tc
            tc_dict["options"] = {}
            tc_conf.append(tc_dict)
        return tc_conf

    # append base path for config file
    config_file = _IN_TREE_CONF_DIR + config_file
    tc_conf = load_config(config_file)
    if not tc_conf:
        print("FAIL: _load_test_conf() - could not load test config")
        return []

    # We do not like the test names starting with /, so we remove it
    for tc in tc_conf:
        tc["name"] = re.sub("^/", "", tc["name"])

    tc_list = []
    # process all tests on config, if test name has .conf we assume we should load the tests from this file
    for tc in tc_conf:
        if re.match(r".*\.conf", tc["name"]):
            sub_tests = _load_test_conf(tc["name"])
            if sub_tests:
                tc_list.extend(sub_tests)
        else:
            # Should match:
            # rhel
            # rhel7
            # rhel<7
            # rhel>7
            distro_rex = re.compile(r"(\S+?)([<>])?(\d+)?$")
            skip_test_case = False
            if "options" in tc and "skip_version" in tc["options"]:
                skip_version = tc["options"]["skip_version"]
                skip_ver_list = skip_version.split(",")
                for skip in skip_ver_list:
                    m = distro_rex.match(skip)
                    if not m:
                        print("FAIL: %s is not a valid skip_version value" % skip)
                        continue

                    skip_distro = m.group(1)
                    skip_major_minor = m.group(2)
                    skip_version = m.group(3)
                    os_version = linux.dist_ver()
                    # currently only supports rhel
                    if skip_distro == "rhel":
                        if not skip_version:
                            # skip in all distro versions
                            skip_test_case = True
                            continue
                        if not skip_major_minor and int(os_version) == int(skip_version):
                            skip_test_case = True
                            continue
                        if skip_major_minor == ">" and int(os_version) > int(skip_version):
                            skip_test_case = True
                            continue
                        if skip_major_minor == "<" and int(os_version) < int(skip_version):
                            skip_test_case = True
                            continue

            if skip_test_case:
                print("DEBUG: skipping test case: %s" % tc["name"])
                continue
            tc_list.append(tc)

    return tc_list


def _list_test_cases_from_config(config_file: str) -> bool:
    """Print test cases defined in the :param config_config_file.

    :param config_file: Name of the conf file used for listing from _IN_TREE_CONF_DIR
    :type config_file: str
    :return: Return True on success. If conf file is not provided, return False.
    :rtype: bool
    """
    if not config_file:
        print("FAIL: _list_test_cases_from_config() - requires config_file as parameter")
        return False

    print("INFO: Showing all test from %s" % config_file)
    tc_list = _load_test_conf(config_file)
    if not tc_list:
        return True
    for tc in tc_list:
        test_info = tc["name"]
        if "options" in tc and "parameters" in tc["options"]:
            test_info += "(%s)" % tc["options"]["parameters"]
        print("--> %s" % test_info)
    return True


def _execute_test_conf(config_file=None, opt_test_name=None, opt_test_params=None, no_run=False) -> list:
    """Execute all test cases as defined on config file .If opt_test_name is given execute only this
    test case from the config file.

    :param config_file: Config file name from __IN_TREE_CONF_DIR
    :type config_file: str
    :param opt_test_name: A test case name to be executed from :param config_file
    :type opt_test_name: str
    :param opt_test_params: Overwrites default config params.
    Parameters are expected to be separated by ',' e.g. 'param1,param2,param3'.
    :type opt_test_params: str
    :param no_run: If no run is set to True, test case is not executed. Param is mainly use for debugging
    :type no_run: bool
    :return: Return a list of test results.
    :rtype: list
    """
    if not config_file and not opt_test_name:
        print("FAIL: _execute_test_conf() - No config name nor test_name was provided")
        return []

    supported_test_cases = _load_test_cases()
    if not supported_test_cases:
        print("FAIL: _execute_test_conf() - Could not find any test case at %s" % _IN_TREE_TESTS_DIR)
        return []

    test_cases = _load_test_conf(config_file)
    if not test_cases:
        print("FAIL: _execute_test_conf() -  Could not read test config file")
        return []

    test_runs = []
    # If test name is given, check if it actually is defined on config file
    if opt_test_name:
        found_test_name = False
        for tc in test_cases:
            if tc["name"] == opt_test_name:
                found_test_name = True
        if not found_test_name:
            msg = "FAIL: Test %s is not defined" % opt_test_name
            if config_file:
                msg += " on config file: %s" % config_file
            test_result = {}
            test_result["name"] = opt_test_name
            test_result["test_result"] = "FAIL"
            test_result["test_log"] = msg
            test_result["elapsed_time"] = 0
            test_runs.append(test_result)
            print("%s" % msg)
            return test_runs

    for tc in test_cases:
        # Skip test cases if is not the test_name given
        if opt_test_name and tc["name"] != opt_test_name:
            continue

        test_result = _setup_test_result(tc["name"])

        if tc["name"] not in supported_test_cases:
            msg = "FAIL: %s is not a valid test case" % tc["name"]
            print(msg)
            print(supported_test_cases)
            test_result["test_result"] = "FAIL"
            test_result["test_log"] = "%s\n" % msg
            test_runs.append(test_result)
            continue

        cmd = ""
        if tc["name"].endswith(".py"):
            cmd = _get_python_executable() + " "
        command = cmd + _IN_TREE_TESTS_DIR + tc["name"]
        test_params = None
        if "options" in tc and "parameters" in tc["options"]:
            tc_options = tc["options"]
            test_params = tc_options["parameters"].split(",")

        if opt_test_params:
            # Overwrites default config params
            test_params = opt_test_params.split(",")

        if test_params:
            param_str = " ".join(test_params)
            command += " %s" % param_str
            test_result["test_param"] = param_str

        _, test_runs = _run_command(command, test_result, test_runs, no_run)

    return test_runs


def _setup_test_result(name: str, flag="") -> dict:
    """Prepare test result dictionary for a test case.

    :param name: Name of the test case
    :type name: str
    :param flag: A flag name
    :type flag: str
    :return: Dictionary which contains keys: name, log_name, elapsed_time and flag
    :rtype: dict
    """
    test_result: dict = {}
    test_result["name"] = name
    test_result["log_name"] = "{}_{}.log".format(test_result["name"], time.get_time())
    # replace path to subdirectories with _
    test_result["log_name"] = test_result["log_name"].replace("/", "_")
    test_result["log_name"] = "/tmp/%s" % test_result["log_name"]
    test_result["elapsed_time"] = 0
    if flag:
        test_result[flag] = True
    return test_result


def _run_command(
    command: str, test_result: dict, test_runs: list, no_run=False, test_type="", export_commands=False  # noqa: ARG001
) -> Tuple[dict, list]:
    """Run a command and populate a test result dictionary with the information about the run.

    :param command: A command to be run
    :type command: str
    :param test_result: Dictionary used to gather info about the run. Function __setup_test_result should be used to
    create a dictionary in a correct format
    :type test_result: dict
    :param test_runs: List to store :param test_result.
    :type test_runs: list
    :param no_run: If no run is set to True, command is not executed. Param is mainly use for debugging
    :type no_run: bool
    :param test_type: Declares type of the test case e.g. Setup, Cleanup, Test. Default type is Test
    :type test_type: str
    :return: Return test_result dictionary and test_runs list as tuple
    :rtype: tuple
    """
    start_time = time.get_time(in_seconds=True)
    print("=" * 110)
    print("Running {} '{}'".format(test_type or "test", test_result["name"]))
    print("=" * 110)
    if no_run:
        retcode = 0
        log = "Did not run."
    else:
        retcode, log = run(command, return_output=True, verbose=True, force_flush=True)
    end_time = time.get_time(in_seconds=True)
    status = "FAIL"
    if retcode == 0:
        status = "PASS"
    elif retcode == 2:
        status = "SKIP"
    test_result["test_result"] = status
    test_result["test_log"] = log
    test_result["elapsed_time"] = time.sec_2_time(end_time - start_time)
    test_runs.append(test_result)
    with open(test_result["log_name"], "w") as file_:
        file_.write(test_result["test_log"])
    # upload the test case log of failed test cases
    if test_result["test_result"] == "FAIL":
        restraint.log_submit(test_result["log_name"])
    return test_result, test_runs


class StratisMonitorDBus(threading.Thread):
    def __init__(self):
        self.p = None
        self.monitor_dbus_path = "/var/tmp/testing"
        threading.Thread.__init__(self)
        self.stratis = Stratis()

    def run(self):
        self.get_stratis_testing_repo()
        ret, version = self.stratis.version(return_output=True)
        version = version.split(".")
        if os.path.isfile(f"{self.monitor_dbus_path}/scripts/monitor_dbus_signals.py"):
            print("monitor_dbus_signals.py is running in the background!")
            cmd = [
                "python3",
                f"{self.monitor_dbus_path}/scripts/monitor_dbus_signals.py",
                f"org.storage.stratis{version[0]}",
                f"/org/storage/stratis{version[0]}",
                f"--top-interface=org.storage.stratis{version[0]}.Manager.r{version[1]}",
            ]
            print(cmd)
            self.p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while self.p.poll() is None:
                try:
                    print(self.p.stderr.readline().decode("utf-8"))
                    print(self.p.stderr.readline().decode("utf-8"))
                except ValueError:
                    pass

    def teardown(self):
        if self.p is not None:
            sleep(12)
            self.p.send_signal(signal.SIGINT)
            (stdoutdata, _) = self.p.communicate()
            msg = stdoutdata.decode("utf-8")
            print(msg)
            if self.p.returncode != 0:
                print(f"WARN: Monitor dbus signals failed with error code: {self.p.returncode}")
            return self.p.returncode
        return None

    def get_stratis_testing_repo(self):
        if not linux.is_installed("git"):
            run("yum install -y git")
        if not os.path.exists(self.monitor_dbus_path):
            ret = run(f"git clone https://github.com/stratis-storage/testing.git {self.monitor_dbus_path}")
            if ret != 0:
                print("WARN: Could not download stratis testing repo!")
                return False
            return True
        print(f"INFO: Path {self.monitor_dbus_path} already exists!")
        return True


def _execute_tests_fmf(
    path,
    filter=None,
    opt_test_param=None,
    setup_env=None,
    bz=None,
    no_run=False,
    sort=False,
    export_commands=False,  # noqa: ARG001
) -> list:
    """Execute fmf tests.

    :param path: Relative path from stqe/tests/
    :type path: str
    :param filter: String of filters
    :type filter: list
    :param opt_test_param: Optional test parameters
    :type opt_test_param:
    :param setup_env:  Setup strings to replace '*' in required_setup
    :type setup_env: str
    :param bz: BZ number to test
    :type bz: str
    :param no_run: Do not run commands, just print them. (for debugging)
    :type no_run: bool
    :param sort: Sort tests instead of shuffling them
    :type sort: bool
    :return: List of test runs
    :rtype: list
    """
    if filter is None:
        filter = []
    test_runs: list = []

    stratis_monitor = None
    if "tags:multiple_device" in filter or "component:stratis" in filter:
        stratis_monitor = StratisMonitorDBus()
        stratis_monitor.start()

    # Need to get the whole tree because of inheritance
    tree = get_tree()

    tests = get_tests(tree, path, filter, os_env_asterix=setup_env, bz=bz)
    try:
        config = get_config(tests, sort=sort)
    except TestNotFoundError as e:
        print(e)
        return []

    for test in config:
        # skip comments
        if not isinstance(test, dict):
            continue

        not_test = None
        try:
            # The new way of marking test types
            not_test = test.pop("test_type")
        except KeyError:
            # This is the old way
            for flag in ["setup", "cleanup", "install"]:
                if flag in test and test[flag]:
                    not_test = flag
        test_result = _setup_test_result(test["name"], not_test or False)

        if "test" not in test:
            print("FAIL: Could not find test file for %s. Check its metadata for correct path." % test["name"])
            return []
        test_file = test["test"]

        command = ""
        for att in test:
            if att == "test":
                continue
            # this is required to have ['x'] instead of [u'x']
            # The replacing is needed for lists containing space in strings
            if isinstance(test[att], list) and sys.version_info[0] < 3:
                command += "fmf_{}='{}' ".format(str(att), str([str(x) for x in test[att]]).replace("'", ""))
            else:
                command += "fmf_{}='{}' ".format(str(att), str(test[att]).replace("'", ""))
        cmd = ""
        if test_file.endswith(".py"):
            cmd = _get_python_executable() + " "
        command += cmd + _IN_TREE_TESTS_DIR + test_file
        if opt_test_param:
            param_str = " ".join(opt_test_param.split(","))
            command += " %s" % param_str
            test_result["test_param"] = param_str
        test_result, test_runs = _run_command(command, test_result, test_runs, no_run, test_type=not_test)

    # Remove any leftover persistent vars files.
    if os.path.isfile("/tmp/FILE_NAMES"):
        files = read_var("FILE_NAMES")
        files.append("FILE_NAMES")
        for f in files:
            test_result = _setup_test_result("remove-tmp/%s" % f, "cleanup")
            cmd = "rm -f /tmp/%s" % f
            test_result, test_runs = _run_command(cmd, test_result, test_runs, no_run)

    if stratis_monitor:
        retcode = stratis_monitor.teardown()
        test_res = "FAIL"
        if retcode == 0:
            test_res = "PASS"
        test_runs.append(
            {
                "name": "Monitor dbus signals",
                "log_name": "",
                "elapsed_time": "00s",
                "test": True,
                "test_result": test_res,
                "test_log": "",
            }
        )

    return test_runs


def _report_test_runs(test_runs: list, report_exit_code: bool, no_report: bool) -> int:
    """Print a test report of test runs.

    :param test_runs: List of test runs
    :param report_exit_code: In case we executed only 1 test and want return its exit code
    :param no_report: Do not print report on stdout
    :return: exit code
    :rtype: int
    """
    if not test_runs:
        print("WARN: stqe-test got no test runs to report.")
        return 1

    # Collect the data
    result_cnt = {}
    result_cnt["PASS"] = 0
    result_cnt["FAIL"] = 0
    result_cnt["SKIP"] = 0
    result_cnt["WARN"] = 0
    result_cnt["total_time"] = 0
    for testrun in test_runs:
        test_name = testrun["name"]
        if "test_param" in testrun:
            test_name += "(%s)" % testrun["test_param"]
        # Do not count failed cleanups as FAILs, use SKIP instead
        if "cleanup" in testrun and testrun["test_result"] == "FAIL":
            testrun["test_result"] = "WARN"
        result_cnt[testrun["test_result"]] += 1

    if not no_report:
        max_len = 0
        for testrun in test_runs:
            if len(testrun["name"]) > max_len:
                max_len = len(testrun["name"])
        str_len = max(102 + max_len - 50, 110)  # 110 is length of the TOTAL line at the end
        print("=" * str_len)
        print("Generating test result report")
        print("=" * str_len)
        errors = _get_errors()
        for testrun in test_runs:
            test_name = testrun["name"]
            error = None
            if test_name in errors:
                error = errors.pop(test_name)
            if "test_param" in testrun:
                test_name += "(%s)" % testrun["test_param"]
            test_type = "   Test"
            try:
                test_type = "%+7s" % testrun["test_type"].capitalize()
                print("***")
            except KeyError:
                if "setup" in testrun:
                    test_type = "  Setup"
                elif "cleanup" in testrun:
                    test_type = "Cleanup"
                elif "install" in testrun:
                    test_type = "Install"
            print(
                "%s name: %-*s Status: %-10s Elapsed Time: %s"
                % (test_type, max_len, test_name, testrun["test_result"], testrun["elapsed_time"])
            )
            if error is not None:
                # Print errors
                for e in error:
                    print("\t%s" % e)
            result_cnt["total_time"] += time.time_2_sec(testrun["elapsed_time"])
        print("=" * str_len)
        print(
            "Total - PASS: %-10d FAIL: %-10d SKIP: %-10d WARN: %-10d %-*s Total Time: %s"
            % (
                result_cnt["PASS"],
                result_cnt["FAIL"],
                result_cnt["SKIP"],
                result_cnt["WARN"],
                max_len - 40,
                "",
                time.sec_2_time(result_cnt["total_time"]),
            )
        )
        print("=" * str_len)

    # Exit with failure of if there is a test run that failed. Consider SKIP as PASS
    if result_cnt["FAIL"] > 0:
        return 1
    # In case we executed only 1 test and want return its exit code.
    # Basically need to return SKIP as SKIP and not as PASS
    if report_exit_code and result_cnt["SKIP"] > 0 and len(test_runs) == 1:
        return 2
    return 0


def _get_errors() -> dict:
    """Get errors from errors log file in /tmp/test_errors.json.

    :return: Content of /tmp/test_errors.json as python dictionary
    :rtype: dict
    """
    errors_log = "/tmp/test_errors.json"
    errors = {}
    if os.path.isfile(errors_log):
        with open(errors_log) as f:
            errors = json.load(f)
        os.remove(errors_log)
    return errors


def _strip_quotation_marks(args):
    """rhts-simple-test-run actually passes the value including quotation marks, example follows
    var="value" gets passed as var="value" instead of just var=value.

    :param args: ArgumentParser object to strip quotation mark from.
    :return: stripped args
    :rtype: ArgumentParser
    """

    def _strip_value(val):
        val = val.strip('"')
        return val.strip("'")

    arguments = args.__dict__
    for arg in arguments:
        if isinstance(arguments[arg], list):
            setattr(args, arg, [_strip_value(a) for a in arguments[arg]])
            continue
        if arguments[arg] is None or not isinstance(arguments[arg], str):
            continue
        # Dynamically set the attribute to correct value
        setattr(args, arg, _strip_value(arguments[arg]))
    return args


def main():
    parser = argparse.ArgumentParser(description="stqe-test")
    subparsers = parser.add_subparsers(help="Valid commands", dest="command")
    parser_list = subparsers.add_parser("list")
    parser_list.add_argument("type", choices=["tests", "configs"], type=str, default=False)
    # in case we want to list test cases from specific test config
    parser_list.add_argument("--config", "-c", required=False, dest="config", default=None, help="Test config file")
    parser_list.add_argument("--fmf", required=False, dest="fmf", default=False, action="store_true", help="Use fmf.")
    parser_list.add_argument(
        "--filter",
        "-f",
        required=False,
        dest="filter",
        type=str,
        default=list(""),
        help="(FMF) String of filters.",
        action="append",
    )
    parser_list.add_argument(
        "--path", required=False, dest="path", default="", help="(FMF) Relative path from stqe/tests/"
    )
    parser_list.add_argument(
        "--verbose",
        "-v",
        required=False,
        dest="verbose",
        default=False,
        action="store_true",
        help="(FMF) Be more verbose.",
    )

    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("--config", "-c", required=False, dest="config", default=None, help="Test config file")
    parser_run.add_argument("--test-name", "-t", required=False, dest="test_name", default=None, help="Test name")
    parser_run.add_argument(
        "--test-parameters",
        "-p",
        required=False,
        dest="test_param",
        action="append",
        default=None,
        help="Test parameters",
    )
    parser_run.add_argument(
        "--test-exit-code",
        required=False,
        action="store_true",
        dest="exit_code",
        default=None,
        help="Exit with the exit code of the test case.",
    )
    parser_run.add_argument(
        "--no-report",
        required=False,
        action="store_true",
        dest="no_report",
        default=None,
        help="Does not show the test run report",
    )
    parser_run.add_argument("--fmf", required=False, dest="fmf", default=False, action="store_true", help="Use fmf.")
    parser_run.add_argument(
        "--filter",
        "-f",
        required=False,
        dest="filter",
        type=str,
        default=list(""),
        help="(FMF, repeatable) String of filters.",
        action="append",
    )
    parser_run.add_argument(
        "--path", required=False, dest="path", default="", help="(FMF) Relative path from stqe/tests/"
    )
    parser_run.add_argument(
        "--setup",
        required=False,
        dest="setup",
        action="append",
        default=None,
        help="(FMF, repeatable) Setup strings to replace '*' in required_setup.",
    )
    parser_run.add_argument("--bz", required=False, dest="bz", type=int, default=None, help="(FMF) BZ number to test.")
    parser_run.add_argument(
        "--norun",
        required=False,
        dest="norun",
        default=False,
        action="store_true",
        help="Do not run commands, just print them. (for debugging)",
    )
    parser_run.add_argument(
        "--sort",
        required=False,
        dest="sort",
        default=False,
        action="store_true",
        help="(FMF) Sort tests instead of shuffling them.",
    )

    parser_report = subparsers.add_parser("report")
    parser_report.add_argument(
        "--no_metadata",
        required=False,
        dest="no_metadata",
        default=False,
        action="store_true",
        help="(FMF) Return just test names, no metadata.",
    )
    parser_report.add_argument(
        "--metadata",
        "-m",
        required=False,
        dest="metadata",
        type=str,
        default=list(""),
        help="(FMF, repeatable) FMF attribute to report.",
        action="append",
    )
    parser_report.add_argument(
        "--path", "-p", required=False, dest="path", default="", help="(FMF) Relative path from stqe/tests/"
    )
    parser_report.add_argument(
        "--filter",
        "-f",
        required=False,
        dest="filter",
        type=str,
        default=list(""),
        help="(FMF) String of filters.",
        action="append",
    )
    parser_report.add_argument(
        "--file", required=False, dest="file", default="", help="(FMF) File to save to instead of printing out"
    )

    args = _strip_quotation_marks(parser.parse_args())

    if args.command == "list":
        if args.type == "configs":
            _list_all_test_conf()
        if args.type == "tests":
            if args.fmf:
                # List tests using fmf metadata in directory stqe/tests/args.path
                tests = filter_tree(name=args.path, filters=args.filter, verbose=args.verbose, to_print=True)
                for test in tests:
                    print(test)
            elif not args.config:
                _list_all_test_cases()
            else:
                _list_test_cases_from_config(args.config)

    if args.command == "run":
        # to be able to pass more parameters
        if args.test_param is not None:
            args.test_param = " ".join(args.test_param)
        if args.fmf:
            args.setup = " ".join(args.setup) if args.setup else None
            test_runs = _execute_tests_fmf(
                args.path, args.filter, args.test_param, args.setup, args.bz, args.norun, args.sort
            )
        else:
            test_runs = _execute_test_conf(args.config, args.test_name, args.test_param, args.norun)
        sys.exit(_report_test_runs(test_runs, args.exit_code, args.no_report))

    if args.command == "report":
        # Need to get the whole tree because of inheritance
        tree = get_tree()
        tests = get_tests(tree, args.path, args.filter, os_env_asterix="*")
        if not args.metadata:
            args.metadata = ["description", "tier"]
        report = get_report("", tests, copy.deepcopy(tests), "", args.no_metadata, args.metadata)
        if args.file:
            with open(args.file, "w") as f:
                f.write(report.encode("UTF-8"))
                print("Wrote report to file %s" % args.file)
        else:
            print(report)

    return 0


sys.exit(main())
