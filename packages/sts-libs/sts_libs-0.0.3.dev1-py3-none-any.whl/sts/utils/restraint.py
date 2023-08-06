"""restraint.py: Module to manage restraint."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import re
from pathlib import Path

from sts import linux
from sts.utils.cmdline import run


def sts_print(string):
    module_name = __name__
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ") ", string)
    string = re.sub("FAIL:", "FAIL:(" + module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ") ", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ") ", string)
    print(string)
    if "FATAL:" in string:
        raise RuntimeError(string)


def update_killtime(kill_time):
    """Change beaker watchdog kill time
    Parameter:
    kill_time     new kill time in hours
    Return:
    True
    or
    False.
    """
    if not is_restraint_job():
        return False

    if not kill_time:
        kill_time = 1

    result_server = os.environ["RESULT_SERVER"]
    jobid = os.environ["RSTRNT_JOBID"]
    test = os.environ["RSTRNT_TASKNAME"]
    testid = os.environ["RSTRNT_TASKID"]

    host = linux.hostname()
    cmd = "rhts-test-checkin {} {} {} {} {} {}".format(
        result_server,
        host,
        jobid,
        test,
        kill_time,
        testid,
    )
    ret, output = run(cmd, return_output=True, verbose=False)
    if ret != 0:
        sts_print("FAIL: Could not update beaker kill time")
        print(output)
        return False
    sts_print("INFO: beaker_update_killtime() - Watchdog timer successfully updated to %d hours" % kill_time)
    return True


def log_submit(log_file):
    """Upload log file."""
    if not is_restraint_job():
        return True

    if not log_file:
        sts_print("FAIL: log_submit() - requires log_file parameter")
        return False

    if not Path(log_file).exists():
        sts_print(f"FAIL: log_submit() - file ({log_file}) does not exist")
        return False

    cmd = f'rhts-submit-log -l "{log_file}"'
    ret, output = run(cmd, return_output=True, verbose=False)
    if ret != 0:
        sts_print(f"FAIL: Could not upload log {log_file}")
        print(output)
        return False
    sts_print(f"INFO: log_submit() - {log_file} uploaded successfully")
    return True


def get_recipe_id():
    """Get current recipe id
    Parameter:
    None
    Return:
    recipe_id:          Restraint recipe id
    or
    None:               When not running using restraint.
    """
    if not is_restraint_job():
        return None
    return os.environ["RSTRNT_RECIPEID"]


def get_task_id():
    """Get current task id
    Parameter:
    None
    Return:
    task_id:          Beaker task id
    or
    None:             Some error occurred.
    """
    if not is_restraint_job():
        return None
    return os.environ["RSTRNT_TASKID"]


def is_restraint_job():
    """Checks if it is restraint job."""
    need_env = ["RSTRNT_TASKNAME", "RSTRNT_TASKID"]
    return all(not var not in os.environ for var in need_env)
