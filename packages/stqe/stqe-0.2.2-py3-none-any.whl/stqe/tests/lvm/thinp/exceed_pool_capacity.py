#!/usr/bin/python -u
# -u is for unbuffered stdout
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
import sys
import traceback

from libsan.host import dm, linux
from libsan.host.cmdline import run
from libsan.host.loopdev import create_loopdev, delete_loopdev
from libsan.host.lvm import pv_remove, vg_create, vg_remove

import stqe.host.tc

TestObj = None

loop_dev = None

vg_name = "vgtest"
pool_name = "test_pool"
thin1_name = "thin1"
thin2_name = "thin2"
mnt_point_thin1 = "/mnt/thin1"
mnt_point_thin2 = "/mnt/thin2"


def start_test(filesystem, errwhenfull):
    global TestObj

    print(80 * "#")
    print(f"INFO: Starting test on FS {filesystem} and errwhenfull={errwhenfull}")
    print(80 * "#")

    _clean_up()

    # create loop device of 1G
    global loop_dev
    loop_dev = create_loopdev(size=1024)
    if not loop_dev:
        TestObj.tfail("Could not create loop device")
        return False

    if not vg_create(vg_name, loop_dev):
        TestObj.tfail('Could not create VG "%s"' % vg_name)
        return False

    print("INFO: Creating LVs")
    if run(f"lvcreate --thinpool {pool_name} -L 800M {vg_name} --errorwhenfull {errwhenfull}") != 0:
        TestObj.tfail(f"Could not create {pool_name} [{filesystem} - errorwhenfull={errwhenfull}]")
        return False
    if run(f"lvcreate -V 1G -T {vg_name}/{pool_name} -n {thin1_name}") != 0:
        TestObj.tfail(f"Could not create {thin1_name} [{filesystem} - errorwhenfull={errwhenfull}]")
        return False
    if run(f"lvcreate -V 1G -T {vg_name}/{pool_name} -n {thin2_name}") != 0:
        TestObj.tfail(f"Could not create {thin2_name} [{filesystem} - errorwhenfull={errwhenfull}]")
        return False

    print("INFO: Displaying LVs")
    run("lvs -a -o +devices")

    dm.dm_show_table()

    thin1_device = f"/dev/mapper/{vg_name}-{thin1_name}"
    print(f"INFO:Going to create FS({filesystem}) on {thin1_device}")
    if run(f"mkfs.{filesystem} {thin1_device}") != 0:
        TestObj.tfail(f"Could not create FS({filesystem}) on {thin1_device} with errorwhenfull={errwhenfull}")
        return False

    if not linux.mkdir(mnt_point_thin1):
        TestObj.tfail(
            f"Could not create directory {mnt_point_thin1} - FS({filesystem}) with errorwhenfull={errwhenfull}",
        )
        return False

    if not linux.mount(thin1_device, mnt_point_thin1):
        TestObj.tfail(f"Could not mount {mnt_point_thin1} - FS({filesystem}) with errorwhenfull={errwhenfull}")
        return False

    thin2_device = f"/dev/mapper/{vg_name}-{thin2_name}"
    print(f"INFO:Going to create FS({filesystem}) on {thin2_device}")
    if run(f"mkfs.{filesystem} {thin2_device}") != 0:
        TestObj.tfail(f"Could not create FS({filesystem}) on {thin2_device} with errorwhenfull={errwhenfull}")
        return False

    if not linux.mkdir(mnt_point_thin2):
        TestObj.tfail(
            f"Could not create directory {mnt_point_thin2}- FS({filesystem}) with errorwhenfull={errwhenfull}",
        )
        return False

    if not linux.mount(thin2_device, mnt_point_thin2):
        TestObj.tfail(f"Could not mount {mnt_point_thin2}- FS({filesystem}) with errorwhenfull={errwhenfull}")
        return False

    run("lvs -a")

    print("INFO: Going create file on %s" % mnt_point_thin1)
    filename = "file1.img"
    # For dd to sync data
    if run(f"dd conv=fdatasync if=/dev/urandom of={mnt_point_thin1}/{filename} bs=1M count=500") != 0:
        TestObj.tfail(f"Could not create file on {mnt_point_thin1} - FS({filesystem}) with errorwhenfull={errwhenfull}")
        return False

    linux.sync()
    run("lvs -a")

    # if not TestObj.tnok("cp %s/%s %s/"% (mnt_point_thin1, filename, mnt_point_thin2)):
    if run(f"dd conv=fdatasync if=/dev/urandom of={mnt_point_thin2}/{filename} bs=1M count=500") == 0:
        TestObj.tfail(
            "Should be possible to create file on %s - FS(%s) with errorwhenfull=%s"
            % (mnt_point_thin2, filesystem, errwhenfull),
        )
        run("lvs -a")
        dm.dm_show_status()
        run("sync")
        run("ls -allh %s/" % mnt_point_thin2)
        run("tail /var/log/messages")
        return False

    linux.sync()
    run("lvs -a")

    print(80 * "#")
    TestObj.tpass(f"PASS: Test on FS {filesystem} and errwhenfull={errwhenfull}")
    print(80 * "#")

    return True


def _clean_up():
    global vg_name, loop_dev

    linux.umount(mnt_point_thin1)
    linux.umount(mnt_point_thin2)

    # make sure any failed device is removed
    run("dmsetup remove_all")
    if not vg_remove(vg_name, force=True):
        TestObj.tfail('Could not delete VG "%s"' % vg_name)

    if loop_dev:
        if not pv_remove(loop_dev):
            TestObj.tfail('Could not delete PV "%s"' % loop_dev)
        linux.sleep(1)
        if not delete_loopdev(loop_dev):
            TestObj.tfail("Could not remove loop device %s" % loop_dev)


def main():
    global TestObj

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--filesystem",
        "-f",
        required=False,
        dest="fs",
        help="Filesystem name",
        metavar="filesytem",
    )

    args = parser.parse_args()

    TestObj = stqe.host.tc.TestClass()

    linux.install_package("lvm2")

    # test if IO fails when error_if_no_space and also if queue IO times out
    errwhenfull = ["y", "n"]

    filesystem = linux.get_default_fs()

    if args.fs:
        filesystem = args.fs

    for err in errwhenfull:
        try:
            start_test(filesystem, err)
        except Exception as e:
            print(e)
            traceback.print_exc()
            e = sys.exc_info()[0]
            TestObj.tfail("There was some problem while running the test (%s)" % e)
            print(e)

    _clean_up()

    if not TestObj.tend():
        print("FAIL: test failed")
        sys.exit(1)

    print("PASS: Test pass")
    sys.exit(0)


main()
