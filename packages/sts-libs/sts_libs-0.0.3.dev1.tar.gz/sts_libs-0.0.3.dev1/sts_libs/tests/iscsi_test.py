#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import patch

import pytest

from sts import iscsi

target = "localhost"


def test_install_initiator():
    if not iscsi.install():
        pytest.fail("FAIL: Could not install iSCSI initiator package")
    assert 1


@patch("sts.iscsi.run")
def test_query_discovery(iscsi_run_func):
    discovery_output = """
SENDTARGETS:
DiscoveryAddress: localhost,3260
Target: iqn.2009-10.com.redhat:storage-0
    Portal: [::1]:3260,1
        Iface Name: default
iSNS:
No targets found.
STATIC:
No targets found.
FIRMWARE:
No targets found.
"""
    iscsi_run_func.return_value = (0, discovery_output)

    expected_ret = {
        "SENDTARGETS": {
            "localhost,3260": {
                "disc_addr": "localhost",
                "disc_port": "3260",
                "mode": "sendtargets",
                "targets": {
                    "iqn.2009-10.com.redhat:storage-0": {
                        "portal": {"address": "[::1]", "port": "3260"},
                        "iface": ["default"],
                    },
                },
            },
        },
        "iSNS": {},
        "STATIC": {},
        "FIRMWARE": {},
    }
    if iscsi.query_discovery() != expected_ret:
        pytest.fail("FAIL: Could not  query discovery iSCSI target")
    assert 1


@patch("sts.iscsi.run")
def test_discovery(iscsi_run_func):
    discovery_output = "[::1]:3260,1 iqn.2009-10.com.redhat:storage-0"
    iscsi_run_func.return_value = (0, discovery_output)

    if not iscsi.discovery_st(target):
        pytest.fail("FAIL: Could not discovery iSCSI target")
    assert 1


@patch("sts.linux.service_restart")
def test_set_iscsid_parameter(service_restart_func):
    service_restart_func.return_value = True
    if not iscsi.set_iscsid_parameter({"node.session.cmds_max": "4096", "node.session.queue_depth": "128"}):
        pytest.fail("FAIL: Unable to set iscsid parameter")
    assert 1
