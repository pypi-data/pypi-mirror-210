#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from pathlib import Path
from unittest.mock import patch

import pytest

from sts import linux, scsi_debug


def test_os_info():
    os_info = linux.query_os_info()
    if not os_info:
        pytest.fail("FAIL: Could not query OS info")

    for info in os_info:
        print(f"{info}: {os_info[info]}")
    assert 1


def test_using_scsi_debug():
    if linux.is_docker():
        print("SKIP: Cannot create scsi_debug in container")
        return
    if not scsi_debug.scsi_debug_load_module():
        pytest.fail("FAIL: loading scsi_debug module")

    device = scsi_debug.get_scsi_debug_devices()[-1]

    if linux.get_parent_device(device) != device:  # scsi_debug does not have parent
        pytest.fail("FAIL: get_parent_device using scsi_debug")
    if linux.get_full_path(device) != f"/dev/{device}":
        pytest.fail("FAIL: get_full_path using scsi_debug")
    wwid = linux.get_device_wwid(device)
    if not wwid:
        pytest.fail("FAIL: get_device_wwid using scsi_debug")
    if linux.get_udev_property(device, "ID_MODEL") != "scsi_debug":
        pytest.fail("FAIL: device ID_MODEL should be 'scsi_debug'")
    if linux.is_dm_device(device):
        pytest.fail("FAIL: scsi_debug device should not be mapped by DM")

    if not scsi_debug.scsi_debug_unload_module():
        pytest.fail("FAIL: loading scsi_debug module")
    assert 1


def test_get_boot_device():
    get_boot = linux.get_boot_device()
    if get_boot is None and linux.is_docker() is False:
        pytest.fail("FAIL: Could not find '/boot' and '/'! ")
    print(f"INFO: Boot device is: {get_boot}")
    assert 1


def test_get_dist_release():
    release = linux.dist_release()
    if not release:
        pytest.fail("FAIL: Could not find distribution release")


def test_get_dist_ver():
    version = linux.dist_ver()
    if not version:
        pytest.fail("FAIL: Could not find distribution version")


def test_get_dist_name():
    name = linux.dist_name()
    if not name:
        pytest.fail("FAIL: Could not find distribution name")


@patch("sts.linux.download_repo_file")
def test_rpm_repo(get_mock):
    content = """[test-fedora-debuginfo]
name=testrepo
#baseurl=http://download.example/pub/fedora/linux/releases/$releasever/Everything/$basearch/debug/tree/
metalink=https://mirrors.fedoraproject.org/metalink?repo=fedora-debug-$releasever&arch=$basearch
enabled=1
repo_gpgcheck=0
type=rpm
skip_if_unavailable=False
"""

    def create_repo_file(_):
        with Path("/etc/yum.repos.d/test2.repo").open("w") as f:
            f.write(content)

    get_mock.side_effect = create_repo_file
    repo_metalink = "https://mirrors.fedoraproject.org/metalink?repo=fedora-debug-$releasever&arch=$basearch"
    repo_url = "https://testurl.com/test.repo"
    repo_name = "testrepo"
    linux.add_repo("test1", repo_metalink, metalink=True)
    if not linux.check_repo("test1"):
        pytest.fail("FAIL: Created repo is not working")
    if not linux.del_repo("test1"):
        pytest.fail("FAIL: Unable to delete repo")
    linux.download_repo_file(repo_url)
    if not linux.check_repo(repo_name):
        pytest.fail("FAIL: Test repo is not working")
    if not linux.del_repo("test2"):
        pytest.fail("FAIL: Unable to delete repo")
    if Path("/etc/yum.repos.d/test2.repo").exists():
        pytest.fail("FAIL: repo file should have been deleted")


@patch("sts.linux.run")
def test_is_mounted(run_func):
    run_func.return_value = 0
    if not linux.is_mounted("testdev"):
        pytest.fail("FAIL: device should have been mounted")
    if not linux.is_mounted(mountpoint="testdir"):
        pytest.fail("FAIL: mountpoint should have been mounted")
    run_func.return_value = 1
    if linux.is_mounted("testdev"):
        pytest.fail("FAIL: device should NOT have been mounted")
    if linux.is_mounted(mountpoint="testdir"):
        pytest.fail("FAIL: mountpoint should NOT have been mounted")
