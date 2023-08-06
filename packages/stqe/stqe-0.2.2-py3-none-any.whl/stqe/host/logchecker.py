"""logchecker.py: Module to Check for errors on the system."""

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
__copyright__ = "Copyright (c) 2015 Red Hat, Inc. All rights reserved."

import os
import re  # regex

import libsan.host.linux
from libsan.host.cmdline import run

import stqe.host.beaker
import stqe.host.restraint

segfault_msg = " segfault "
calltrace_msg = "Call Trace:"

error_mgs = [segfault_msg, calltrace_msg]


def check_all():
    """Check for error on the system
    Returns:
    \tBoolean:
    \t\tTrue is no error was found
    \t\tFalse if some error was found
    """
    print("INFO: Checking for error on the system")
    error = 0

    if not kernel_check():
        error += 1
    if not abrt_check():
        error += 1
    if not messages_dump_check():
        error += 1
    if not dmesg_check():
        error += 1
    if not console_log_check():
        error += 1
    if not kdump_check():
        error += 1

    if error:
        log_messages = "/var/log/messages"
        if os.path.isfile(log_messages):
            print("submit %s, named messages.log" % log_messages)
            run("cp %s messages.log" % log_messages)
            stqe.host.restraint.log_submit("messages.log")

        if libsan.host.linux.is_installed("sos"):
            sos_file = libsan.host.linux.generate_sosreport()
            if not sos_file:
                return False
            stqe.host.restraint.log_submit(sos_file)
        return False

    return True


def abrt_check():
    """Check if abrtd found any issue
    Returns:
    \tBoolean:
    \t\tTrue no error was found
    \t\tFalse some error was found
    """
    print("INFO: Checking abrt for error")

    if run("rpm -q abrt", verbose=False) != 0:
        print("WARN: abrt tool does not seem to be installed")
        print("WARN: skipping abrt check")
        return True

    if run("pidof abrtd", verbose=False) != 0:
        print("FAIL: abrtd is not running")
        return False

    ret, log = run("abrt-cli list", return_output=True)
    if ret != 0:
        print("FAIL: abrt-cli command failed")
        return False

    # We try to match for "Directory" to check if
    # abrt-cli list is actually listing any issue
    error = False
    if log:
        lines = log.split("\n")
        for line in lines:
            m = re.match(r"Directory:\s+(\S+)", line)
            if m:
                directory = m.group(1)
                filename = directory
                filename = filename.replace(":", "-")
                filename += ".tar.gz"
                run(f"tar cfzP {filename} {directory}")
                stqe.host.restraint.log_submit(filename)
                # if log is saved on restraint, it can be deleted from server
                # it avoids next test from detecting this failure
                run("abrt-cli rm %s" % directory)
                error = True

    if error:
        print("FAIL: Found abrt error")
        return False

    print("PASS: no Abrt entry has been found.")
    return True


def kernel_check():
    """
    Check if kernel got tainted.
    It checks /proc/sys/kernel/tainted which returns a bitmask.
    The values are defined in the kernel source file include/linux/kernel.h,
    and explained in kernel/panic.c
    cd /usr/src/kernels/`uname -r`/
    Sources are provided by kernel-devel
    Returns:
    \tBoolean:
    \t\tTrue if did not find any issue
    \t\tFalse if found some issue
    """
    print("INFO: Checking for tainted kernel")

    previous_tainted_file = "/tmp/previous-tainted"

    _, tainted = run("cat /proc/sys/kernel/tainted", return_output=True)

    tainted_val = int(tainted)
    if tainted_val == 0:
        run("echo %d > %s" % (tainted_val, previous_tainted_file), verbose=False)
        print("PASS: Kernel is not tainted.")
        return True

    print("WARN: Kernel is tainted!")

    if not os.path.isfile(previous_tainted_file):
        run(f"echo {tainted_val} > {previous_tainted_file}", verbose=False)
    _, prev_taint = run("cat %s" % previous_tainted_file, return_output=True)
    prev_taint_val = int(prev_taint)
    if prev_taint_val == tainted_val:
        print("INFO: Kernel tainted has already been handled")
        return True

    run("echo %d > %s" % (tainted_val, previous_tainted_file), verbose=False)

    # check all bits that are set
    bit = 0
    while tainted_val != 0:
        # need to change back to int because it got changed to float at shifting
        tainted_val = int(tainted_val)
        if tainted_val & 1:
            print("\tTAINT bit %d is set\n" % bit)
        bit += 1
        # shift tainted value
        tainted_val /= 2
    # List all tainted bits that are defined
    print("List bit definition for tainted kernel")
    run("cat /usr/src/kernels/`uname -r`/include/linux/kernel.h | grep TAINT_")

    found_issue = False
    # try to find the module which tainted the kernel, tainted module have a mark between '('')'
    _, output = run("cat /proc/modules | grep -e '(.*)' |  cut -d' ' -f1", return_output=True)
    tainted_mods = output.split("\n")
    # For example during iscsi async_events scst tool loads an unsigned module
    # just ignores it, so we will ignore this tainted if there is no tainted
    # modules loaded
    if not tainted_mods:
        print("INFO: ignoring tainted as the module is not loaded anymore")
    else:
        # ignore ocrdma due BZ#1334675
        # ignore nvme_fc and nvmet_fc due Tech Preview - BZ#1384922
        ignore_modules = ["ocrdma", "nvme_fc", "nvmet_fc"]
        for tainted_mod in tainted_mods:
            if tainted_mod:
                print("INFO: The following module got tainted: %s" % tainted_mod)
                run("modinfo %s" % tainted_mod)
                # due BZ#1334675  we are ignoring ocrdma module
                if tainted_mod in ignore_modules:
                    print("INFO: ignoring tainted on %s" % tainted_mod)
                    run(
                        "echo %d > %s" % (tainted_val, previous_tainted_file),
                        verbose=False,
                    )
                    continue
                found_issue = True

    run(f"echo {tainted} > {previous_tainted_file}", verbose=False)
    if found_issue:
        return False

    return True


def _date2num(date):
    date_map = {
        "Jan": "1",
        "Feb": "2",
        "Mar": "3",
        "Apr": "4",
        "May": "5",
        "Jun": "6",
        "Jul": "7",
        "Aug": "8",
        "Sep": "9",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }

    date_regex = r"(\S\S\S)\s(\d+)\s(\d\d:\d\d:\d\d)"
    m = re.match(date_regex, date)
    month = date_map[m.group(1)]
    day = str(m.group(2))
    # if day is a single digit, add '0' to begin
    if len(day) == 1:
        day = "0" + day

    hour = m.group(3)
    hour = hour.replace(":", "")

    value = month + day + hour

    return value


def messages_dump_check():
    previous_time_file = "/tmp/previous-dump-check"

    log_msg_file = "/var/log/messages"
    if not os.path.isfile(log_msg_file):
        print("WARN: Could not open %s" % log_msg_file)
        return True

    with open(log_msg_file, "rb") as log_file:
        log = ""
        for line in log_file.readlines():
            try:
                log += line.decode("UTF-8")
            except UnicodeDecodeError:
                log += line.decode("latin-1")

    begin_tag = "\\[ cut here \\]"
    end_tag = "\\[ end trace "

    if not os.path.isfile(previous_time_file):
        first_time = "Jan 01 00:00:00"
        time = _date2num(first_time)
        run(f"echo {time} > {previous_time_file}")

    # Read the last time test ran
    _, last_run = run("cat %s" % previous_time_file, return_output=True)
    print("INFO: Checking for stack dump messages after: %s" % last_run)

    # Going to search the file for text that matches begin_tag until end_tag
    dump_regex = begin_tag + "(.*?)" + end_tag
    m = re.findall(dump_regex, log, re.MULTILINE)
    if m:
        print("INFO: Checking if it is newer than: %s" % last_run)
        print(m.group(1))
        # TODO

    print("PASS: No recent dump messages has been found.")
    return True


def dmesg_check():
    """Check for error messages on dmesg ("Call Trace and segfault")"""
    print("INFO: Checking for errors on dmesg.")
    error = 0
    for msg in error_mgs:
        _, output = run("dmesg | grep -i '%s'" % msg, return_output=True)
        if output:
            print("FAIL: found %s on dmesg" % msg)
            run("echo '\nINFO found %s  Saving it\n'>> dmesg.log" % msg)
            run("dmesg >> dmesg.log")
            stqe.host.restraint.log_submit("dmesg.log")
            error = 1
    libsan.host.linux.clear_dmesg()
    if error:
        return False

    print("PASS: No errors on dmesg have been found.")
    return True


def console_log_check():
    """Checks for error messages on console log ("Call Trace and segfault")"""
    if not stqe.host.beaker.is_beaker_job():
        # skip check
        return True
    return stqe.host.beaker.console_log_check(error_mgs)


def kdump_check():
    """
    Check for kdump error messages.
    It assumes kdump is configured on /var/crash
    """
    error = 0

    previous_kdump_check_file = "/tmp/previous-kdump-check"
    kdump_dir = "/var/crash"
    ret, hostname = run("hostname", verbose=False, return_output=True)

    if not os.path.exists(f"{kdump_dir}/{hostname}"):
        print("INFO: No kdump log found for this server")
        return True

    ret, output = run(f"ls -l {kdump_dir}/{hostname} |  awk '{{print$9}}'", return_output=True)
    kdumps = output.split("\n")
    kdump_dates = []
    for kdump in kdumps:
        if kdump == "":
            continue
        # parse on the date, remove the ip of the uploader
        m = re.match(".*?-(.*)", kdump)
        if not m:
            print("WARN: unexpected format for kdump (%s)" % kdump)
            continue
        date = m.group(1)
        # Old dump were using "."
        date = date.replace(r"\.", "-")
        # replace last "-" with space to format date properly
        index = date.rfind("-")
        date = date[:index] + " " + date[index + 1 :]
        print("INFO: Found kdump from %s" % date)
        kdump_dates.append(date)

    # checks if a file to store last run exists, if not create it
    if not os.path.isfile("%s" % previous_kdump_check_file):
        # time in seconds
        ret, time = run(r"date +\"\%s\"", verbose=False, return_output=True)
        run(f"echo -n {time} > {previous_kdump_check_file}", verbose=False)
        print("INFO: kdump check is executing for the first time.")
        print("INFO: doesn't know from which date should check files.")
        print("PASS: Returning success.")
        return True

    # Read the last time test ran
    ret, previous_check_time = run("cat %s" % previous_kdump_check_file, return_output=True)
    # just add new line to terminal because the file should not have already new line character
    print("")

    for date in kdump_dates:
        # Note %% is escape form to use % in a string
        ret, kdump_time = run('date --date="%s" +%%s' % date, return_output=True)
        if ret != 0:
            print("WARN: Could not convert date %s" % date)
            continue

        if not kdump_time:
            continue
        if int(kdump_time) > int(previous_check_time):
            print(f"FAIL: Found a kdump log from {date} (more recent than {previous_check_time})")
            print(f"FAIL: Check {kdump_dir}/{hostname}")
            error += 1

    ret, time = run(r"date +\"\%s\"", verbose=False, return_output=True)
    run(f"echo -n {time} > {previous_kdump_check_file}", verbose=False)

    if error:
        return False

    print("PASS: No errors on kdump have been found.")
    return True
