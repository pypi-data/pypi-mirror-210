"""cmdline.py: Module to execute a command line."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import subprocess
import sys
import time
from shutil import which


def run(cmd, return_output=False, verbose=True, force_flush=False, timeout=None):
    """Run a command line specified as cmd.

    The arguments are:
    cmd (str):    Command to be executed
    verbose:      if we should show command output or not
    force_flush:  if we want to show command output while command is being executed. e.g. hba_test run
    timeout (int):timeout for the process in seconds
    return_output (Boolean): Set to True if output result is to be returned as tuple. Default is False
    Returns:
    int: Return code of the command executed
    str: As tuple of return code if return_output is set to True.
    """
    # by default print command output
    if verbose:
        # Append time information to command
        date = 'date "+%Y-%m-%d %H:%M:%S"'
        p = subprocess.Popen(date, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        stdout = stdout.decode("ascii", "ignore")
        stdout = stdout.rstrip("\n")
        print(f"INFO: [{stdout}] Running: '{cmd}'...")

    stderr = b""
    if not force_flush:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        try:
            stdout, stderr = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            stdout, stderr = p.communicate()
            print("WARN: Timeout reached")
            p.returncode = 124  # to stay consistent with bash Timeout return code
        sys.stdout.flush()
        sys.stderr.flush()
    else:
        start_time = time.time()
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout = b""
        while p.poll() is None:
            new_data = p.stdout.readline()
            stdout += new_data
            if verbose:
                sys.stdout.write(new_data.decode("ascii", "ignore"))
            sys.stdout.flush()
            if timeout and time.time() - start_time > timeout:
                print("WARN: Timeout reached")
                p.kill()
                p.returncode = 124  # to stay consistent with bash Timeout return code
                break

    retcode = p.returncode

    # print "stdout:(" + stdout + ")"
    # print "stderr:(" + stderr + ")"
    output = stdout.decode("ascii", "ignore") + stderr.decode("ascii", "ignore")

    # remove new line from last line
    output = output.rstrip()

    # by default print command output
    # if force_flush we already printed it
    if verbose and not force_flush:
        print(output)

    # print "stderr " + err
    # print "returncode: " + str(retcode)
    if not return_output:
        return retcode
    return retcode, output


def exists(cmd):
    if not which(str(cmd)):
        return False
    return True
