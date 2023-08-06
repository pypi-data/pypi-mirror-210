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

#
# Bugs related:
#   BZ1319937 - pool created without zeroing the first 4KiB (--zero n) can not have meta corrupted and then repaired
#


import sys

from libsan.host.cmdline import run
from libsan.host.linux import install_package
from libsan.host.loopdev import create_loopdev, delete_loopdev
from libsan.host.lvm import vg_create, vg_remove

import stqe.host.tc

TestObj = None

# global vg_name
# global pool_name

loop_dev0 = None
loop_dev1 = None

vg_name = "VG"
pool_name = "POOL"
lv_meta_swap = "meta_swap"


def main():
    global TestObj

    install_package("lvm2")

    TestObj = stqe.host.tc.TestClass()
    _clean_up()

    test_without_zero()
    _clean_up()

    test_with_zero()
    _clean_up()

    if not TestObj.tend():
        print("FAIL: test failed")
        sys.exit(1)

    print("PASS: Test pass")
    sys.exit(0)


def start(zero):
    global TestObj

    global loop_dev0, loop_dev1

    # create loop device of 10G
    loop_dev0 = create_loopdev("loop0", 5 * 1024)
    if not loop_dev0:
        TestObj.tfail("Could not create loop0 device")
    loop_dev1 = create_loopdev("loop1", 5 * 1024)
    if not loop_dev1:
        TestObj.tfail("Could not create loop1 device")

    pv_devs = loop_dev0 + " " + loop_dev1
    if not vg_create(vg_name, pv_devs):
        TestObj.tfail('Could not create VG "%s"' % vg_name)

    print("INFO: Creating LVs")
    TestObj.tok(f"lvcreate --thinpool {pool_name} --zero {zero} -L 1G --poolmetadatasize 4M {vg_name}")
    TestObj.tok(f"lvcreate --virtualsize 1G -T {vg_name}/{pool_name} -n origin")
    TestObj.tok(f"lvcreate --virtualsize 1G -T {vg_name}/{pool_name} -n other1")
    TestObj.tok(f"lvcreate --virtualsize 1G -T {vg_name}/{pool_name} -n other2")
    TestObj.tok(f"lvcreate --virtualsize 1G -T {vg_name}/{pool_name} -n other3")
    TestObj.tok(f"lvcreate --virtualsize 1G -T {vg_name}/{pool_name} -n other4")
    TestObj.tok("lvcreate -k n -s /dev/%s/origin -n snap" % vg_name)
    TestObj.tok("lvs -a -o +devices")
    print("INFO: tmeta is using:")
    TestObj.tok("lvs -a -o name,devices | grep %s_tmeta | awk {'print $2'}" % pool_name)

    print("INFO: Corrupting metadata")
    run(f"dd if=/dev/urandom of=/dev/mapper/{vg_name}-{pool_name}_tmeta count=512 seek=4096 bs=1")
    TestObj.tok("vgchange -an %s" % vg_name)

    print("INFO: Sanity checking pool device (%s) metadata" % pool_name)
    TestObj.tok(f"lvchange -an --yes --select 'lv_name={pool_name} || pool_lv={pool_name}'")

    print("INFO: create tmp lv in order to swap the existing metadata device")
    TestObj.tok(f"lvcreate -n {lv_meta_swap} -L 4M {vg_name}")

    print("INFO: swap the tmp device with the existing metadata device")
    TestObj.tok(f"lvconvert --yes --thinpool {vg_name}/{pool_name} --poolmetadata {vg_name}/{lv_meta_swap}")

    print("INFO: do the actual check")
    TestObj.tok(f"lvchange -ay {vg_name}/{lv_meta_swap}")
    TestObj.tnok(f"thin_check /dev/mapper/{vg_name}-{lv_meta_swap}")

    print("INFO: swap the devices back to their original positions")
    TestObj.tok(f"lvchange -an {vg_name}/{lv_meta_swap}")
    TestObj.tok(f"lvconvert --yes --thinpool {vg_name}/{pool_name} --poolmetadata {vg_name}/{lv_meta_swap}")

    print("INFO: remove tmp device")
    TestObj.tok(f"lvremove {vg_name}/{lv_meta_swap}")
    TestObj.tnok(f"lvchange -ay --yes --select 'lv_name={pool_name} || pool_lv={pool_name}'")

    print("INFO: Swap in new _tmeta device using lvconvert --repair")
    TestObj.tok(f"lvconvert --yes --repair {vg_name}/{pool_name} {loop_dev1}")
    print("INFO: tmeta is using:")
    TestObj.tok("lvs -a -o name,devices | grep %s_tmeta | awk {'print $2'}" % pool_name)
    TestObj.tok("vgchange -ay %s" % vg_name)

    print("INFO: Sanity checking pool device (%s) metadata again" % pool_name)
    TestObj.tok(f"lvchange -an --yes --select 'lv_name={pool_name} || pool_lv={pool_name}'")

    print("INFO: create tmp lv in order to swap the existing metadata device")
    TestObj.tok(f"lvcreate -n {lv_meta_swap} -L 4M {vg_name}")

    print("INFO: swap the tmp device with the existing metadata device")
    TestObj.tok(f"lvconvert --yes --thinpool {vg_name}/{pool_name} --poolmetadata {vg_name}/{lv_meta_swap}")

    print("INFO: do the actual check")
    TestObj.tok(f"lvchange -ay {vg_name}/{lv_meta_swap}")
    TestObj.tok(f"thin_check /dev/mapper/{vg_name}-{lv_meta_swap}")

    TestObj.tok(f"lvchange -an {vg_name}/{lv_meta_swap}")
    TestObj.tok(f"lvconvert --yes --thinpool {vg_name}/{pool_name} --poolmetadata {vg_name}/{lv_meta_swap}")

    print("INFO: remove tmp device")
    TestObj.tok(f"lvremove {vg_name}/{lv_meta_swap}")
    TestObj.tok(f"lvchange -ay --yes --select 'lv_name={pool_name} || pool_lv={pool_name}'")

    _clean_up()

    # sys.exit(0)
    return True


def _clean_up():
    global vg_name, loop_dev0, loop_dev1

    vg_remove(vg_name, force=True)

    if loop_dev0:
        run("pvremove --yes --force --force %s" % loop_dev0)
        if delete_loopdev(loop_dev0):
            loop_dev0 = None

    if loop_dev1:
        run("pvremove --yes --force --force %s" % loop_dev1)
        if delete_loopdev(loop_dev1):
            loop_dev1 = None
    return True


def test_without_zero():
    for i in range(1, 6):
        print("############################################################")
        print("INFO: Running test WITHOUT zeroing first 4KiB. Interaction %d" % i)
        print("############################################################")
        start("n")


def test_with_zero():
    for i in range(1, 6):
        print("############################################################")
        print("INFO: Running test ZEROING first 4KiB. Interaction %d" % i)
        print("############################################################")
        start("y")


main()
