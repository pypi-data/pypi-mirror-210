#!/usr/bin/python


import os
import unittest

from libsan.host.mp import mpath_conf_match, mpath_conf_remove, mpath_conf_set


class TestAugeas(unittest.TestCase):
    def test_validate_mpath_conf(self):
        test_string = "TEST123"
        conf_file = "/etc/multipath.conf"
        # This tests if changes done to multipath.conf are valid
        if not os.path.exists(conf_file):
            os.mknod(conf_file)
        assert mpath_conf_set("/blacklist/wwid[last()+1]", test_string) is True
        assert mpath_conf_remove(mpath_conf_match("/blacklist/wwid", test_string), test_string) is True
        with open(conf_file) as f:
            assert test_string not in f
