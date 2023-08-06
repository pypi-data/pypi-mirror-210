#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
from pathlib import Path

import pytest

from sts import fio
from sts.utils.cmdline import run


def test_fio():
    if not fio.install_fio():
        pytest.fail("Unable to install fio")

    output_file = "fio.test"

    # Create a file big enough to use by FIO
    run(f"dd if=/dev/zero of={output_file} count=20 bs=1024k")

    try:
        fio_pid = fio.fio_stress_background(output_file, size="1m")
    except Exception as e:
        pytest.fail(f"FAIL: Exception: {e}")

    # Make sure background process does not generate exception
    print("INFO: Waiting FIO process to finish")
    try:
        _, exit_status = os.waitpid(fio_pid, 0)
    except Exception as e:
        pytest.fail(f"FAIL: Exception: {e}")

    if exit_status != 0:
        pytest.fail("FAIL: there was some error running FIO")
    try:
        Path(output_file).unlink()
    except Exception:
        pytest.fail(f"FAIL: Could not delete {output_file}")

    assert 1
