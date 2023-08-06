#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import unittest
from unittest.mock import patch

from sts import lvm


class TestPV(unittest.TestCase):
    pvs_output = "  /dev/vda1,lvm_test,lvm2,a--,98.41g,0"
    pv_query_output = {
        "/dev/vda1": {
            "vg": "lvm_test",
            "fmt": "lvm2",
            "attr": "a--",
            "psize": "98.41g",
            "pfree": "0",
        },
    }

    def test_pv_query(self):
        with patch("sts.lvm.run") as run_func:
            run_func.return_value = [0, self.pvs_output]
            assert self.pv_query_output == lvm.pv_query()

    def test_pv_create(self):
        with patch("sts.lvm.run") as run_func:
            run_func.return_value = 0
            assert lvm.pv_create("/dev/vda1")
        with patch("sts.lvm.run") as run_func:
            run_func.return_value = 1
            assert not lvm.pv_create("/dev/vda1")

    @patch("sts.lvm.pv_query")
    def test_pv_remove(self, mock):
        mock.return_value = self.pv_query_output
        with patch("sts.lvm.run") as run_func:
            run_func.return_value = 0
            assert lvm.pv_remove("/dev/vda1")
        with patch("sts.lvm.run") as run_func:
            run_func.return_value = 1
            assert not lvm.pv_remove("/dev/vda1")


class TestVG(unittest.TestCase):
    vgs_output = "  lvm_test,1,3,0,wz--n-,98.41g,0"
    vg_query_output = {
        "lvm_test": {
            "num_pvs": "1",
            "num_lvs": "3",
            "num_sn": "0",
            "attr": "wz--n-",
            "vsize": "98.41g",
            "vfree": "0",
        },
    }

    def test_vg_query(self):
        with patch("sts.lvm.run") as run_func:
            run_func.return_value = [0, self.vgs_output]
            assert self.vg_query_output == lvm.vg_query()

    def test_pv_create(self):
        with patch("sts.lvm.run") as run_func:
            run_func.return_value = 0
            assert lvm.vg_create("lvm_test", "/dev/vda1")
        with patch("sts.lvm.run") as run_func:
            run_func.return_value = 1
            assert not lvm.vg_create("lvm_test", "/dev/vda1")

    @patch("sts.lvm.pv_query")
    def test_pv_remove(self, mock):
        mock.return_value = self.vg_query_output
        with patch("sts.lvm.run") as run_func:
            run_func.return_value = 0
            assert lvm.pv_remove("lvm_test")
        with patch("sts.lvm.run") as run_func:
            run_func.return_value = 1
            assert not lvm.pv_remove("lvm_test")
