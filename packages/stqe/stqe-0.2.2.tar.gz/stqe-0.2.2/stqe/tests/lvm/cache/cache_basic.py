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

from libsan.host import dm, linux, lvm
from libsan.host.cmdline import run
from libsan.host.loopdev import create_loopdev, delete_loopdev

import stqe.host.tc

TestObj = None

loop_dev = {}

vg_name = "vgcache"
slow_lv = "slow_lv"
fast_lv = "cache_lv"
fast_meta_lv = "cache_metadata_lv"
mnt_point = "/mnt/cache_test"


def start_test(filesystem):
    global TestObj

    print(80 * "#")
    print("INFO: Starting test on FS %s" % filesystem)
    print(80 * "#")

    _clean_up()

    global loop_dev
    loop_dev["slow_dev"] = create_loopdev(size=4096)
    if not loop_dev["slow_dev"]:
        # Skip test if we are not able to create loopdev
        TestObj.tskip("Could not create loop device to be used as slow_dev")
        return 2

    loop_dev["fast_dev"] = create_loopdev(size=2048)
    if not loop_dev["fast_dev"]:
        TestObj.tskip("Could not create loop device to be used as fast_dev")
        return 2

    if not lvm.vg_create(vg_name, "{} {}".format(loop_dev["slow_dev"], loop_dev["fast_dev"])):
        TestObj.tfail('Could not create VG "%s"' % vg_name)
        return 1

    print("INFO: Creating Slow LV")
    if run("lvcreate -n {} -L 3G {} {}".format(slow_lv, vg_name, loop_dev["slow_dev"])) != 0:
        TestObj.tfail("Could not create %s" % slow_lv)
        return 1
    print("INFO: Creating Cache LV")
    if run("lvcreate -n {} -L 1G {} {}".format(fast_lv, vg_name, loop_dev["fast_dev"])) != 0:
        TestObj.tfail("Could not create %s" % fast_lv)
        return 1
    print("INFO: Creating  Cache metadata LV")
    if run("lvcreate -n {} -L 12M {} {}".format(fast_meta_lv, vg_name, loop_dev["fast_dev"])) != 0:
        TestObj.tfail("Could not create %s" % fast_meta_lv)
        return 1

    print("INFO: Creating cache pool logical volume")
    if (
        run(
            "lvconvert --yes --type cache-pool --cachemode writethrough --poolmetadata %s/%s %s/%s"
            % (vg_name, fast_meta_lv, vg_name, fast_lv),
        )
        != 0
    ):
        TestObj.tfail("Could not create cache pool LV")
        return 1

    print("INFO: Creating cache logical volume")
    if run(f"lvconvert --yes --type cache --cachepool {vg_name}/{fast_lv} {vg_name}/{slow_lv}") != 0:
        TestObj.tfail("Could not create cache LV")
        return 1

    print("INFO: Displaying LVs")
    run("lvs -a -o +devices")

    dm.dm_show_table()

    lv_device = f"/dev/mapper/{vg_name}-{slow_lv}"
    print(f"INFO:Going to create FS({filesystem}) on {lv_device}")
    if run(f"mkfs.{filesystem} {lv_device}") != 0:
        TestObj.tfail(f"Could not create FS({filesystem}) on {lv_device}")
        return 1

    if not linux.mkdir(mnt_point):
        TestObj.tfail(f"Could not create directory {mnt_point} - FS({filesystem})")
        return 1

    if not linux.mount(lv_device, mnt_point):
        TestObj.tfail(f"Could not mount {mnt_point} - FS({filesystem})")
        return 1

    print("INFO: Going create file on %s" % mnt_point)
    filename = "file1.img"
    if run(f"dd conv=fdatasync if=/dev/urandom of={mnt_point}/{filename} bs=1M count=2000") != 0:
        TestObj.tfail(f"Could not create file on {mnt_point} - FS({filesystem})")
        return 1

    linux.sync()
    run("lvs -a")

    print(80 * "#")
    TestObj.tpass("PASS: Test on FS %s" % filesystem)
    print(80 * "#")

    return 0


def _clean_up():
    global vg_name, loop_dev

    linux.umount(mnt_point)

    # make sure any failed device is removed
    run("dmsetup remove_all")
    if not lvm.vg_remove(vg_name, force=True):
        TestObj.tfail('Could not delete VG "%s"' % vg_name)

    if loop_dev:
        for dev in loop_dev:
            if loop_dev[dev]:
                if not lvm.pv_remove(loop_dev[dev]):
                    TestObj.tfail('Could not delete PV "%s"' % loop_dev[dev])
                linux.sleep(1)
                if not delete_loopdev(loop_dev[dev]):
                    TestObj.tfail("Could not remove loop device %s" % loop_dev[dev])


def main():
    global TestObj

    parser = argparse.ArgumentParser(description="cache_basic")
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

    filesystem = linux.get_default_fs()

    if args.fs:
        filesystem = args.fs

    ret = start_test(filesystem)

    _clean_up()

    if not TestObj.tend():
        print("FAIL: test failed")
        sys.exit(1)

    if ret == 2:
        print("SKIP: Test has been skipped because loop device could not be created!")
        sys.exit(2)

    print("PASS: Test pass")
    sys.exit(0)


main()
