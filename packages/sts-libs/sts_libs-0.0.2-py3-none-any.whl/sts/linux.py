"""py: Module to get information from servers."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import errno
import os.path
import re  # regex
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Literal, Optional, Tuple, Union

from configobj import ConfigObj
from pkg_resources import parse_version

from sts import mp, scsi
from sts.utils import sts_print
from sts.utils.cmdline import exists, run


def hostname():
    ret, host = run("hostname", verbose=False, return_output=True)
    if ret != 0:
        sts_print("FAIL: hostname() - could not run command")
        print(host)
        return None
    return host


def linux_distribution():
    # Not using platform module, as it doesn't provide needed information
    # on recent python3 versions
    # see: https://bugzilla.redhat.com/show_bug.cgi?id=1920385
    # see: https://bugs.python.org/issue28167
    data = {}
    with Path("/etc/os-release").open(encoding="UTF-8") as f:
        for line in f:
            line = line.strip()  # noqa: PLW2901
            if line == "":
                continue
            k, v = line.split("=")
            data[k] = v.strip('"')
    return [data["ID"], data["VERSION_ID"]]


def dist_release():
    """Find out the release number of distribution."""
    # We are base on output of lsb_release -r -s, which is shipped by redhat-lsb rpm.
    # ret, release = run("lsb_release --release --short", verbose=False, return_output=True)
    # if ret == 0:
    #    return release
    dist = linux_distribution()
    if not dist:
        sts_print("FAIL: Could not determine dist release!")
        return None
    return dist[1]


def dist_ver():
    """Check the distribution version."""
    release = dist_release()
    if not release:
        return None
    m = re.match(r"(\d+).\d+", release)
    if m:
        return int(m.group(1))

    # See if it is only digits, in that case return it
    m = re.match(r"(\d+)", release)
    if m:
        return int(m.group(1))

    sts_print(f"FAIL: dist_ver() - Invalid release output {release}")
    return None


def dist_ver_minor():
    """Check the distribution minor version.
    For example: RHEL-7.4 returns 4.
    """
    release = dist_release()
    if not release:
        return None
    m = re.match(r"\d+.(\d+)", release)
    if m:
        return int(m.group(1))

    sts_print(f"FAIL: dist_ver_minor() - Release does not seem to have minor version: {release}")
    return None


def dist_name():
    """Find out the name of distribution."""
    # We are base on output of lsb_release -r -s, which is shipped by redhat-lsb rpm.
    # ret, release = run("lsb_release --release --short", verbose=False, return_output=True)
    # if ret == 0:
    #    return release
    dist = linux_distribution()
    if not dist:
        sts_print("FAIL: dist_name() - Could not determine dist name")
        return None

    if dist[0] == "rhel":
        return "RHEL"

    return dist[0]


def service_start(service_name):
    """Start service
    The arguments are:
    None
    Returns:
    True: Service started
    False: There was some problem.
    """
    cmd = f"systemctl start {service_name}"
    has_systemctl = True

    if not exists("systemctl"):
        has_systemctl = False
    if not has_systemctl:
        cmd = f"service {service_name} start"

    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        sts_print(f"FAIL: Could not start {service_name}")
        if has_systemctl:
            run(f"systemctl status {service_name}")
            run("journalctl -xn")
        return False
    return True


def service_stop(service_name):
    """Stop service
    The arguments are:
    Name of the service
    Returns:
    True: Service stopped
    False: There was some problem.
    """
    cmd = f"systemctl stop {service_name}"
    has_systemctl = True

    if not exists("systemctl"):
        has_systemctl = False
    if not has_systemctl:
        cmd = f"service {service_name} stop"

    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        sts_print(f"FAIL: Could not stop {service_name}")
        if has_systemctl:
            run(f"systemctl status {service_name}")
            run("journalctl -xn")
        return False
    return True


def service_restart(service_name, verbose=True):
    """Restart service
    The arguments are:
    Name of the service
    Returns:
    True: Service restarted
    False: There was some problem.
    """
    cmd = f"systemctl restart {service_name}"
    has_systemctl = True

    if not exists("systemctl"):
        has_systemctl = False
    if not has_systemctl:
        cmd = f"service {service_name} restart"
    service_timestamp = get_service_timestamp(service_name)
    if service_timestamp is not None:
        timestamp_struct = time.strptime(service_timestamp, "%a %Y-%m-%d %H:%M:%S %Z")
        actual_time = time.localtime()
        if time.mktime(actual_time) - time.mktime(timestamp_struct) < 5:
            print("Waiting 5 seconds before restart.")
            time.sleep(5)
    retcode = run(cmd, return_output=False, verbose=verbose)
    if retcode != 0:
        sts_print(f"FAIL: Could not restart {service_name}")
        if has_systemctl:
            run(f"systemctl status {service_name}")
            run("journalctl -xn")
        return False
    return True


def systemctl_is_enabled(unit: str) -> bool:
    retcode = run(f"systemctl is-enabled {unit}", return_output=False, verbose=False)
    if retcode != 0:
        return False
    return True


def is_service_enabled(service_name: str) -> bool:
    return systemctl_is_enabled(f"{service_name}.service")


def service_enable(service_name, now=False):
    """Enable service
    The arguments are:
    Name of the service
    Returns:
    True: Service got enabled
    False: There was some problem.
    """
    cmd = f"systemctl enable {service_name}"
    if now:
        cmd = cmd + " --now"

    retcode = run(cmd, return_output=False, verbose=True)
    if retcode != 0:
        sts_print(f"FAIL: Could not enable {service_name}")
        run(f"systemctl status {service_name}")
        run("journalctl -xn")
        return False
    return True


def service_status(service_name, verbose=True):
    """Check service status
    The arguments are:
    Name of service
    Returns:
    0 - service is running and OK
    1 - service is dead and /run pid file exists
    2 - service is dead and /lock lock file exists
    3 - service is not running
    4 - service could not be found.
    False - something went wrong.
    """
    cmd = f"systemctl status {service_name}"
    has_systemctl = True

    if not exists("systemctl"):
        has_systemctl = False
    if not has_systemctl:
        cmd = f"service {service_name} status"

    retcode = run(cmd, return_output=False, verbose=verbose)
    if retcode == 0:
        sts_print(f"INFO: Service {service_name} is running.")
    elif retcode == 1:
        sts_print(f"INFO: Service {service_name} is dead and /run pid file exists.")
    elif retcode == 2:
        sts_print(f"INFO: Service {service_name} is dead and /lock lock file exists.")
    elif retcode == 3:
        sts_print(f"INFO: Service {service_name} is not running.")
    elif retcode == 4:
        sts_print(f"INFO: Service {service_name} could not be found.")
    else:
        sts_print(f"INFO: Service {service_name} returned unknown code {retcode}.")
    return retcode


def is_service_running(service_name):
    """Check if service is running
    The arguments are:
    Name of service
    Returns:
     True: service is running
     False: service is not running.
    """
    return service_status(service_name, verbose=False) == 0


def os_arch():
    ret, arch = run("uname -m", verbose=False, return_output=True)
    if ret != 0:
        sts_print("FAIL: could not get OS arch")
        return None

    return arch


def is_installed(pack, verbose=False):
    """Checks if package is installed."""
    ret, ver = run(f"rpm -q {pack}", verbose=False, return_output=True)
    if ret == 0:
        if verbose:
            print(f"INFO: {pack} is installed ({ver})")
        return True

    if verbose:
        print(f"INFO: {pack} is not installed ")
    return False


def install_package(pack, check=True, verbose=True):
    """Install a package "pack" via `yum|dnf install -y`."""
    # Check if package is already installed
    if check and is_installed(pack, verbose):
        return True

    packmngr = "yum"
    if is_installed("dnf"):
        packmngr = "dnf"

    if run(f"{packmngr} install -y {pack}") != 0:
        msg = f"FAIL: Could not install {pack}"
        sts_print(msg)
        return False

    if verbose:
        print(f"INFO: {pack} was successfully installed")
    return True


def package_version(pkg):
    """Get the version of specific package."""
    if not pkg:
        sts_print("FAIL: package_version requires package name as parameter")
        return None

    release = dist_name().lower()
    if not release:
        sts_print("FAIL: package_version() - Couldn't get release")
        return None
    if exists("rpm"):
        ret, output = run(
            "rpm -qa --qf='%%{version}.%%{release}' %s" % pkg,
            return_output=True,
            verbose=False,
        )
        if ret != 0:
            sts_print(f"FAIL: Could not get version for package: {pkg}")
            print(output)
            return None
        return output

    sts_print(f"FAIL: package_version() - Unsupported release: {release}")
    return None


def compare_version(package: str, version: str, release: str, equal: bool = True) -> Union[bool, None]:
    """Returns 'True' if installed version is newer or equal than asked,
    'False' if older Return 'None' if the package is not installed (not found).

    Args:
      package: package name
      version: package version
      release: package release
      equal: return value if packaged are equal version (default 'True').
    """
    pkg = package_version(package)
    if pkg is None:
        return None
    if any(True for x in pkg if not isinstance(x, int)):
        # cut ending of package name containing string, parse_version() does not work with ints and strings at once
        pack = []
        for p in pkg[:].split("."):
            try:
                int(p)
            except ValueError:
                break
            pack.append(p)
        pkg = ".".join(pack)
    if equal:
        return parse_version(version + "." + release) <= parse_version(pkg)
    return parse_version(version + "." + release) < parse_version(pkg)


def wait_udev(sleeptime=15):
    """Wait udev to finish. Often used after scsi rescan."""
    sts_print("INFO: Waiting udev to finish storage scan")
    # For example, on RHEL 7 scsi_wait_scan module is deprecated
    if run("modinfo scsi_wait_scan", verbose=False) == 0:
        run("modprobe -q scsi_wait_scan")
        run("modprobe -r -q scsi_wait_scan")

    run("udevadm settle")
    sleep(sleeptime)

    return True


def get_all_loaded_modules():
    """Check /proc/modules and return a list of all modules that are loaded."""
    cmd = 'cat /proc/modules | cut -d " " -f 1'
    ret, output = run(cmd, return_output=True, verbose=False)
    if ret != 0:
        sts_print(f"FAIL: load_module() - Could not execute: {cmd}")
        print(output)
        return None

    return output.split("\n")


def load_module(module):
    """Run modprobe using module with parameters given as input
    Parameters:
    module:       module name and it's parameters.
    """
    if not module:
        sts_print("FAIL: load_module() - requires module parameter")
        return False
    cmd = f"modprobe {module}"
    if run(cmd) != 0:
        sts_print(f"FAIL: load_module() - Could not execute: {module}")
        return False
    return True


def unload_module(module_name, remove_dependent=False):
    """Run rmmod to unload module
    Parameters:
    module_name:       module name.
    """
    if not module_name:
        sts_print("FAIL: unload_module() - requires module_name parameter")
        return False
    cmd = f"modprobe -r {module_name}"

    if remove_dependent:
        dep_modules = get_dependent_modules(module_name)
        if dep_modules:  # print info only if there are any modules to remove
            sts_print(f"INFO: Removing modules dependent on {module_name}")
            for module in dep_modules:
                if not unload_module(module, remove_dependent=remove_dependent):
                    sts_print("FAIL: unload_module() - Could not unload dependent modules")
                    return False

    if run(cmd) != 0:
        sts_print(f"FAIL: unload_module() - Could not unload: {module_name}")
        return False

    return True


def get_dependent_modules(module_name):
    """Returns list of modules that loaded this module as a dependency
    Useful when removing parent modules (error "Module is in use by: ")
    Parameters:
    module_name:      module_name.
    """
    if not module_name:
        sts_print("FAIL: get_dependent_modules() - requires module_name parameter")
        return None
    cmd = f'cat /proc/modules | grep -Ew "^{module_name}" | cut -d \' \' -f 4 | tr "," " "'
    ret, dependent_modules = run(cmd, return_output=True, verbose=False)
    if dependent_modules == "-":
        return []  # No dependent modules found
    if ret != 0:
        sts_print("FAIL: get_dependent_modules() - failed to get a list of modules")
        return None
    return dependent_modules.split()


def is_module_loaded(module_name):
    """Check if given module is loaded
    Parameters:
    module_name:      module_name.
    """
    if module_name in get_all_loaded_modules():
        return True
    return False


def sleep(duration):
    """It basically calls sys.sleep, but as stdout and stderr can be buffered
    We flush them before sleep.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(duration)


def is_mounted(device=None, mountpoint=None):
    """Check if mountpoint is already mounted."""
    if device and run(f"mount | grep {device}", verbose=False) != 0:
        return False
    if mountpoint and run(f"mount | grep {mountpoint}", verbose=False) != 0:
        return False
    return True


def mount(device=None, mountpoint=None, fs=None, options=None):
    cmd = "mount"
    if fs:
        cmd += f" -t {fs}"
    if options:
        cmd += f" -o {options}"
    if device:
        cmd += f" {device}"
    if mountpoint:
        cmd += f" {mountpoint}"
    if run(cmd) != 0:
        sts_print("FAIL: Could not mount partition")
        return False

    return True


def umount(device=None, mountpoint=None):
    cmd = "umount"
    if device:
        cmd += f" {device}"
        if not is_mounted(device):
            # Device is not mounted
            return True

    if mountpoint:
        cmd += f" {mountpoint}"
        if not is_mounted(mountpoint=mountpoint):
            # Device is not mounted
            return True

    if run(cmd) != 0:
        sts_print("FAIL: Could not umount partition")
        return False

    return True


def get_default_fs():
    """Return the default FileSystem for this release."""
    if dist_name() == "RHEL" and dist_ver() > 6:
        return "xfs"

    return "ext4"


def run_cmd_background(cmd):
    """Run Command on background
    Returns:
    subprocess.
    PID is on process.pid
    Exit code is on process.returncode (after run process.communicate())
    Wait for process to finish
    while process.poll() is None:
    sleep(1)
    Get stdout and stderr
    (stdout, stderr) = process.communicate().
    """
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if not process:
        sts_print(f"FAIL: Could not run '{cmd}' on background")
        return None
    sts_print("INFO: running %s on background. PID is %d" % (cmd, process.pid))
    return process


def kill_pid(pid):
    os.kill(pid, signal.SIGTERM)
    sleep(1)
    if check_pid(pid):
        os.kill(pid, signal.SIGKILL)
        sleep(1)
        if check_pid(pid):
            return False
    return True


def kill_all(process_name):
    ret = run(f"killall {process_name}", verbose=None)
    # Wait few seconds for process to finish
    sleep(3)
    return ret


def check_pid(pid):
    """Check there is a process running with this PID."""
    # try:
    # #0 is the signal, it does not kill the process
    # os.kill(int(pid), 0)
    # except OSError:
    # return False
    # else:
    # return True
    try:
        return os.waitpid(pid, os.WNOHANG) == (0, 0)
    except OSError as e:
        if e.errno != errno.ECHILD:
            raise


def time_stamp(utc: bool = False, in_seconds: bool = False):
    now = datetime.now(tz=timezone.utc if utc else None)

    # ts = "%s%s%s%s%s%s" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    ts = now.strftime("%Y%m%d%H%M%S")
    if in_seconds:
        ts = now.strftime("%s")
    return ts


def kernel_command_line():
    """Return the kernel command line used to boot."""
    retcode, output = run("cat /proc/cmdline", return_output=True, verbose=False)
    if retcode != 0:
        sts_print("FAIL: could not get kernel command line")
        print(output)
        return None
    return output


def kernel_version():
    """Usage
        kernel_version()
    Purpose
        Check out running kernel version. The same as output of `uname -r`
    Parameter
        N/A
    Returns
        kernel_version.
    """
    retcode, output = run("uname -r", return_output=True, verbose=False)
    if retcode != 0:
        sts_print("FAIL: could not get kernel version")
        print(output)
        return None
    # remove arch detail and kernel type
    return re.sub(r"\.%s.*" % os_arch(), "", output)


def kernel_type():
    """Usage
        kernel_type()
    Purpose
        Check the kernel type. Current we support detection of these types:
            1. default kernel.
            2. debug kernel.
            3. rt kernel.
    Parameter
        N/A
    Returns
        kernel_type        # 'debug|rt|default'.
    """
    retcode, version = run("uname -r", return_output=True, verbose=False)
    if retcode != 0:
        sts_print("FAIL: kernel_type() - could not get kernel version")
        print(version)
        return None

    if re.match(r".*\.debug$", version):
        return "debug"

    if re.match(r".*\.rt$", version):
        return "rt"

    return "default"


def kmem_leak_start():
    """Usage
        kmem_leak_start()
    Purpose
        Start and clear kernel memory leak detection.
    Parameter
        N/A
    Returns
        True
          or
        False       # not debug kernel or failure found.
    """
    k_type = kernel_type()

    if not k_type or k_type != "debug":
        sts_print("WARN: Not debug kernel, will not enable kernel memory leak check")
        return False

    arch = os_arch()
    if arch == "i386" or arch == "i686":
        print("INFO: Not enabling kmemleak on 32 bits server.")
        return False

    k_commandline = kernel_command_line()
    if not re.search("kmemleak=on", k_commandline):
        sts_print("WARN: kmem_leak_start(): need 'kmemleak=on' kernel_option to enable kernel memory leak detection")

    check_debugfs_mount_cmd = 'mount | grep "/sys/kernel/debug type debugfs"'
    retcode = run(check_debugfs_mount_cmd, verbose=False)
    if retcode != 0:
        # debugfs is not mounted
        mount_debugfs_cli_cmd = "mount -t debugfs nodev /sys/kernel/debug"
        run(mount_debugfs_cli_cmd, verbose=True)
        check_debugfs_mount_cmd = 'mount | grep "/sys/kernel/debug type debugfs"'
        retcode, output = run(check_debugfs_mount_cmd, return_output=True, verbose=False)
        if retcode != 0:
            sts_print("WARN: Failed to mount debugfs to /sys/kernel/debug")
            print(output)
            return False

    # enable kmemleak and clear
    sts_print("INFO: Begin kernel memory leak check")
    if run("echo scan=on > /sys/kernel/debug/kmemleak") != 0:
        return False
    if run("echo stack=on > /sys/kernel/debug/kmemleak") != 0:
        return False
    if run("echo clear > /sys/kernel/debug/kmemleak") != 0:
        return False
    return True


def kmem_leak_check():
    """Usage
        kmem_leak_check()
    Purpose
        Read out kernel memory leak check log and then clear it up.
    Parameter
        N/A
    Returns
        kmemleak_log
          or
        None       # when file '/sys/kernel/debug/kmemleak' not exists
                  # or no leak found.
    """
    sysfs_kmemleak = "/sys/kernel/debug/kmemleak"
    if not Path(sysfs_kmemleak).is_file():
        return None

    with Path(sysfs_kmemleak).open() as f:
        if not f:
            sts_print(f"FAIL: Could not read {sysfs_kmemleak}")
            return None
        kmemleak_log = f.read()

    if kmemleak_log:
        sts_print(f"WARN: Found kernel memory leak:\n{kmemleak_log}")
        sts_print("INFO: Clearing memory leak for next check")
        run(f"echo 'clear' > {sysfs_kmemleak}")
        return kmemleak_log

    sts_print("INFO: No kernel memory leak found")
    return None


def kmem_leak_disable():
    """Usage
        kmem_leak_disable()
    Purpose
        Disable kmemleak by 'scan=off' and 'stack=off' to
        '/sys/kernel/debug/kmemleak'.
    Parameter
        N/A
    Returns
        True           # disabled or not enabled yet
          or
        False       # failed to run 'echo' command.
    """
    sysfs_kmemleak = "/sys/kernel/debug/kmemleak"
    if not Path(sysfs_kmemleak).is_file():
        return True

    sts_print("INFO: kmem_leak_disable(): Disabling kernel memory leak detection")
    ok1, ok1_output = run(f"echo scan=off > {sysfs_kmemleak}", return_output=True)
    ok2, ok2_output = run(f"echo stack=off > {sysfs_kmemleak}", return_output=True)
    if ok1 != 0 or ok2 != 0:
        print("FAIL: kmem_leak_disable(): Failed to disable kernel memory leak detection")
        print(ok1_output)
        print(ok2_output)
        return False

    sts_print("INFO: kmem_leak_disable(): Kernel memory leak detection disabled")
    return True


def query_os_info():
    """Query OS information and set a reference below:
        os_info = {
            dist_name       = dist_name,
            dist_release    = dist_release,
            kernel_version  = kernel_version,
            os_arch         = os_arch,
            arch            = os_arch,
            pkg_arch        = pkg_arch, #as, for example, rpm on i386 could return different arch then uname -m.

        }
    Parameter
        N/A
    Returns
        os_info_dict
            or
        None       # got error
    """
    return {
        "dist_name": dist_name(),
        "dist_version": dist_ver(),
        "dist_release": dist_release(),
        "os_arch": os_arch(),
        "arch": os_arch(),
        "pkg_arch": os_arch(),
        "kernel_version": kernel_version(),
        "kernel_type": kernel_type(),
    }


def get_driver_info(driver: str):
    if not driver:
        sts_print("FAIL: get_driver_info() - requires driver parameter")
        return None

    sys_fs_dir = "/sys/module"
    sys_fs_path = Path(sys_fs_dir)
    if not sys_fs_path.is_dir():
        sts_print(f"FAIL: get_driver_info() - {sys_fs_path} is not a valid directory")
        return None

    sysfs_driver_folder = sys_fs_path / driver
    if not sysfs_driver_folder.is_dir():
        sts_print(f"FAIL: get_driver_info() - module {driver} is not loaded")
        return None

    driver_info = {}
    infos = ["srcversion", "version", "taint"]
    for info in infos:
        info_path = sysfs_driver_folder / info
        if not Path(info_path).is_file():
            continue
        _, output = run(f"cat {info_path}", return_output=True, verbose=False)
        driver_info[info] = output

    sys_driver_parameter = sysfs_driver_folder / "parameters"
    if sys_driver_parameter.is_dir():
        # Need to add driver parameters
        param_files = list(sys_driver_parameter.iterdir())
        for param in param_files:
            _, output = run(f"cat {sys_driver_parameter}/{param}", return_output=True, verbose=False)
            if "parameters" not in driver_info:
                driver_info["parameters"] = {}
            driver_info["parameters"][param] = output
    return driver_info


def mkdir(new_dir):
    if Path(new_dir).is_dir():
        sts_print(f"INFO: {new_dir} already exist")
        return True
    cmd = f"mkdir -p {new_dir}"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        sts_print(f"FAIL: could create directory {new_dir}")
        print(output)
        return False
    return True


def rmdir(dir_name):
    """Remove directory and all content from it."""
    if not Path(dir_name).is_dir():
        sts_print(f"INFO: {dir_name} does not exist")
        return True
    cmd = f"rm -rf {dir_name}"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        sts_print(f"FAIL: could remove directory {dir_name}")
        print(output)
        return False
    return True


def mkfs(device_name, fs_type, force=False):
    """Create a Filesystem on device."""
    if not device_name or not fs_type:
        sts_print("INFO: mkfs() requires device_name and fs_type")
        return False

    force_option = "-F"
    if fs_type == "xfs":
        force_option = "-f"

    cmd = f"mkfs.{fs_type} "
    if force:
        cmd += f"{force_option} "
    cmd += device_name
    retcode, output = run(cmd, return_output=True, verbose=True)
    if retcode != 0:
        sts_print(f"FAIL: could create filesystem {fs_type} on {device_name}")
        print(output)
        return False
    return True


def sync(directory=None):
    cmd = "sync"
    if directory:
        cmd += f" {directory}"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        sts_print("FAIL: could not sync")
        print(output)
        return False
    return True


def get_free_space(path):
    """Get free space of a path.
    Path could be:
    /dev/sda
    /root
    ./.
    """
    if not path:
        return None

    cmd = f"df -B 1 {path}"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        sts_print(f"FAIL: get_free_space() - could not run {cmd}")
        print(output)
        return None
    fs_list = output.split("\n")
    # delete the header info
    del fs_list[0]

    if len(fs_list) > 1:
        # Could be the information was too long and splited in lines
        tmp_info = "".join(fs_list)
        fs_list[0] = tmp_info

    # expected order
    # Filesystem    1B-blocks       Used   Available Use% Mounted on
    free_space_regex = re.compile(r"\S+\s+\d+\s+\d+\s+(\d+)")
    m = free_space_regex.search(fs_list[0])
    if m:
        return int(m.group(1))
    return None


def get_block_device_name(device):
    """Returns kernel name from block device
    eg. lvm1 from /dev/mapper/lvm1.
    """
    if not device.startswith("/dev/"):
        device = get_full_path(device)
    if not device:
        sts_print("FAIL: get_block_device_name - unknown device")
    cmd = f"lsblk -ndlo NAME {device}"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        sts_print(f"FAIL: run {cmd}")
        print(output)
        return None
    return output


def get_full_path(device_name):
    """Returns full block device path, eg. from device: /dev/mapper/device."""
    cmds = [
        f"lsblk -pnalo NAME  | grep {device_name} -m1",  # should be more robust
        f"find /dev/ -name {device_name}",
    ]  # older OS(rhel-6), will fail with partitions

    for cmd in cmds:
        retcode, output = run(cmd, return_output=True, verbose=False)
        if retcode == 0 and output != "":
            return output

    sts_print(f"FAIL: get_full_path() - {device_name}")
    return None


def get_parent_device(child_device, only_direct=False):
    """Returns block device's parent device: eg. sda, nvme0n1
    child_device: eg. /dev/sda2, nvme0n1p1, /dev/mapper/device
    only_direct: returns only the direct parent. eg. lvm -> sda3, not sda.
    """
    if not child_device.startswith("/dev/"):
        child_device = get_full_path(child_device)
    if not child_device:  # get_full_path would return None if device does not exist
        sts_print(f"FAIL: get_parent_device - unknown child_device '{child_device}'")
    cmd = f"lsblk -nsl {child_device} -o KNAME | tail -n 1"
    if only_direct:
        cmd = f"lsblk -nsl {child_device} -o KNAME | sed -n 2p"  # if no parent, returns nothing
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        sts_print(f"FAIL: run {cmd}")
        print(output)
        return None
    if output == "" or output == child_device:
        sts_print("WARN: get_parent_device - device has no parent")
        return None
    return output


def get_udev_property(device_name: str, property_key: str) -> Union[str, None]:
    """Given an /dev device name, returns specified property using udevadm.

    Args:
      device_name: e.g. 'sda', 'mpatha', 'dm-0', 'nvme0n1', 'sr0', ...
      property_key: eg. 'ID_SERIAL', 'DM_WWN', 'ID_PATH', ...
    :return property_value: eg. for ID_SERIAL: '360fff19abdd9f5fb943525d45126ca27'
    """
    if not device_name:
        sts_print("WARN: get_udev_property() - requires device_name parameter")
        return None

    # Converts for example mpatha to /dev/mapper/mpatha or sda to /dev/sda
    device = get_full_path(device_name)
    if not device:
        sts_print(f"FAIL: get_udev_property - unknown device_name '{device_name}'")

    # Trying to catch wrong key name when dm-multipath is used.
    if mp.is_mpath_device(device_name, print_fail=False):  # noqa: SIM102
        if property_key.startswith("ID_") and not property_key.startswith("ID_FS_"):
            property_key = property_key.replace("ID_", "DM_")

    ret, property_value = run(
        f"udevadm info -q property --name={device} | grep {property_key}= | cut -d = -f 2",
        return_output=True,
        verbose=False,
    )
    if ret:
        sts_print(f"WARN: Could not get udevadm info of device '{device}'")
        return None
    if not property_value:
        sts_print(f"WARN: Could not find property '{property_key}' in udevadm info of device '{device}'")
        return None

    return property_value


def get_boot_device(parent_device=False, full_path=False):
    """Returns boot device, eg. 'sda1'
    parent_device, eg. 'sda'
    full_path, eg. '/dev/sda1'.
    """
    boot_mount = "/boot"
    root_mount = "/"
    # get boot device
    cmd = f"mount | grep ' {boot_mount} ' | cut -d ' ' -f 1"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        sts_print(f"FAIL: run {cmd}")
        print(output)
        return None
    boot_device = output
    # get root device
    cmd = f"mount | grep ' {root_mount} ' | cut -d ' ' -f 1"
    retcode, output = run(cmd, return_output=True, verbose=False)
    if retcode != 0:
        sts_print(f"FAIL: run {cmd}")
        print(output)
        return None
    root_device = output

    if not boot_device and not root_device:
        sts_print("FAIL: Could not find '/boot' and '/' mounted!")
        return None
    if not boot_device:
        # /boot is not mounted on openstack virtual machines
        sts_print("INFO: Could not find /boot mounted... Assuming this is a virtual machine")
        boot_device = root_device
    if boot_device == "overlay":
        sts_print("INFO: / mounted on overlay device. Assuming running in a container")
        return None

    if parent_device:
        boot_device = get_parent_device(boot_device)
    if full_path:
        return get_full_path(boot_device)
    return get_block_device_name(boot_device)


def is_dm_device(device_name: str) -> bool:
    """Checks if device is mapped by device-mapper.

    Args:
      device_name: e.g. 'sda', 'mpatha', ...
    """
    # Converts for example mpatha to /dev/mapper/mpatha or sda to /dev/sda
    device = get_full_path(device_name)
    if not device:
        sts_print(f"FAIL: is_dm_device - unknown device_name '{device_name}'")
        return False
    ret, name = run(f"udevadm info -q name --name={device}", return_output=True)
    if ret:
        sts_print(f"FAIL: Could not get udevadm info for device '{device}'")
        return False
    if not name:
        sts_print(f"FAIL: Could not find udev name for '{device}'")
        return False

    if name.startswith("dm"):
        return True

    return False


def is_nvme_device(device):
    """Checks if device is nvme device."""
    return bool(re.match("^nvme[0-9]n[0-9]$", device))


def get_wwid_of_nvme(device):
    """Reads WWID from udev ID_WWN."""
    return get_udev_property(device, property_key="ID_WWN")


def get_device_wwid(device):
    """Given an SCSI, NVMe or multipath device, returns its WWID."""
    if device.startswith("vd"):
        print(f"INFO: {device}: Presuming virtual disk does not have wwid.")
        return None

    serial = get_udev_property(device_name=device, property_key="ID_SERIAL")
    if not serial and is_dm_device(device):  # RHEL-6 workaround
        dm_uuid = get_udev_property(device_name=device, property_key="DM_UUID")
        serial = dm_uuid.replace("mpath-", "")
    if not serial:
        sts_print(f"INFO: get_device_wwid() - Could not find WWID for {device}")
        return None

    return serial


def remove_device_wwid(wwid):
    if not wwid:
        sts_print("FAIL: remove_device_wwid() - requires wwid as parameter")
        return False

    mpath_wwid = mp.mpath_name_of_wwid(wwid)
    if mpath_wwid:
        mp.remove_mpath(mpath_wwid)

    scsi_ids_wwid = scsi.scsi_ids_of_wwid(wwid)
    if scsi_ids_wwid:
        for scsi_id in scsi_ids_wwid:
            scsi_name = scsi.get_scsi_disk_name(scsi_id)
            if not scsi_name:
                continue
            sts_print(f"INFO: detaching SCSI disk {scsi_name}")
            scsi.delete_disk(scsi_name)
    return True


def clear_dmesg():
    cmd = "dmesg --clear"
    if dist_ver() < 7:
        cmd = "dmesg -c"
    run(cmd, verbose=False)
    return True


def get_regex_pci_id():
    regex_pci_id = r"(?:([0-0a-f]{4}):){0,1}"  # domain id (optional)
    regex_pci_id += r"([0-9a-f]{2})"  # bus id
    regex_pci_id += r":"
    regex_pci_id += r"([0-9a-f]{2})"  # slot id
    regex_pci_id += r"\."
    regex_pci_id += r"(\d+)"  # function id
    return regex_pci_id


def get_partitions(device):
    """Return a list of all parition numbers from the device."""
    if not device:
        sts_print("WARN: get_partitions() - requires device as parameter")
        return None

    cmd = f"parted -s {device} print"
    ret, output = run(cmd, verbose=False, return_output=True)
    if ret != 0:
        # sts_print("FAIL: get_partitions() - Could not read partition information from %s" % device)
        # print output
        return None

    lines = output.split("\n")
    if not lines:
        return None

    header_regex = re.compile(r"Number  Start   End     Size    Type")
    partition_regex = re.compile(r"\s(\d+)\s+\S+")
    partitions = []
    found_header = False
    for line in lines:
        if header_regex.match(line):
            found_header = True
            continue
        if found_header:
            m = partition_regex.match(line)
            if m:
                partitions.append(m.group(1))

    return partitions


def delete_partition(device, partition):
    """Delete specific partition from the device."""
    if not device or not partition:
        sts_print("FAIL: delete_partition() - requires device and partition as argument")
        return False

    cmd = f"parted -s {device} rm {partition}"
    ret, output = run(cmd, verbose=False, return_output=True)
    if ret != 0:
        sts_print("FAIL: delete_partition() - Could not delete partition %d from %s" % (partition, device))
        print(output)
        return False

    return True


def add_repo(name, address, metalink=False):
    """Adds yum repository to /etc/yum.repos.d/NAME.repo."""
    repo = Path(f"/etc/yum.repos.d/{name.lower()}.repo")
    if repo.is_file():
        sts_print(f"INFO: Repo {repo} already exists.")
        return True

    url = "metalink" if metalink else "baseurl"

    repo_conf_table = {
        "name": name,
        url: address,
        "enabled": "1",
        "gpgcheck": "0",
        "skip_if_unavailable": "1",
    }

    repo_conf = f"[{name}]\n"
    for setting, value in repo_conf_table.items():
        repo_conf += f"{setting}={value}\n"

    with repo.open(mode="w") as f:
        f.write(repo_conf)

    return True


def download_repo_file(url, name=None, overwrite=True):
    """Downloads .repo file to /etc.repos.d/."""
    if not url:
        print("FAIL: repo file url argument required")
        return False
    if not name:
        name = url.split("/")[-1]
    if name[-5:] != ".repo":
        name = f"{name}.repo"
    path = f"/etc/yum.repos.d/{name}"

    if Path(path).is_file():
        if overwrite is False:
            print(f"WARN: {name} exits, skipping repo file download")
            return True
        print(f"WARN: {name} exits, overwriting .repo file")
    install_package("curl", check=True, verbose=False)
    if not run(f"curl {url} --output {path}", verbose=True):
        return False

    return True


def del_repo(name):
    """Removes .repo file."""
    try:
        Path(f"/etc/yum.repos.d/{name}.repo").unlink()
    except FileNotFoundError:
        sts_print(f"WARN: Removing repository {name} failed.")
        return False
    return True


def check_repo(name, check_if_enabled=True):
    """Checks if repository works and is enabled."""
    if not name:
        print("FAIL: repo name argument required")
        return False

    cmd = f"yum repoinfo {name} | grep Repo-status"  # yum=dnf alias works here
    ret, out = run(cmd, return_output=True)
    if ret != 0:
        print(f"{name} repo is not present")
        return False
    if check_if_enabled and "enabled" not in out:
        print(f"{name} repo is not enabled")
        return False

    return True


def is_docker():
    """Check if we are running inside docker container."""
    cmd = "cat /proc/self/cgroup | grep docker"
    ret = run(cmd, verbose=False, return_output=False)
    if ret == 0:
        # It is docker
        return True
    return False


def get_memory(units="m", total=False):
    """Returns data from 'free' as a dict."""
    possible_units = "b bytes k kilo m mega  g giga tera peta".split()
    if units not in possible_units:
        sts_print("FAIL: 'units' must be one of %s" % [str(x) for x in possible_units])
        return None

    memory = {}
    columns = []

    if len(units) > 1:
        units = "-" + units
    cmd = f"free -{units}"
    if total:
        cmd += " -t"
    ret, mem = run(cmd=cmd, return_output=True)
    if ret != 0:
        sts_print(f"FAIL: Running '{cmd}' failed.")
        return None

    for row, m in enumerate(mem.splitlines()):
        if row == 0:
            columns = [c.strip() for c in m.split()]
            continue
        m = [x.strip() for x in m.split()]  # noqa: PLW2901
        key = m.pop(0)[:-1].lower()
        memory[key] = {}
        for i, value in enumerate(m):
            memory[key][columns[i]] = int(value)

    return memory


def get_service_timestamp(service_name: str) -> Union[str, None]:
    """Returns active enter timestamp of a service.

    Args:
      service_name: Name of the service

    Returns:
    Time in format: a YYYY-MM-DD hh:mm:ss Z
    None: systemctl is not installed or timestamp does not exist
    """
    if not exists("systemctl"):
        cmd = f"systemctl show {service_name} --property=ActiveEnterTimestamp"
        ret, data = run(cmd, return_output=True)
        if ret == 0:
            timestamp = data.split("=")
            if timestamp[1] != "":
                return timestamp[1]
            return None
        sts_print(f"WARN: Could not get active enter timestamp of service: {service_name}")
    return None


def get_system_logs(
    length: Optional[int] = None,
    reverse: bool = False,
    kernel_only: bool = False,
    since: Optional[str] = None,
    grep: Optional[str] = None,
    options: Optional[List[str]] = None,
    verbose: bool = False,
    return_output: bool = True,
) -> Union[Literal[0, 1], Tuple[Literal[0, 1]], Any]:
    """Gets system logs using journalctl.

    Args:
      length: Get last $length messages.
      reverse: Get logs in reverse.
      kernel_only: Get only kernel messages.
      since: Get messages since some time, can you '+' and '-' prefix.
      grep: String to test_filter messages using 'grep'.
      options: Any other possible options with its value as a string.
      verbose: Print the journal when getting it.
      return_output: Should the function return only retcode or also the output.

    Returns:
      retcode / (retcode, data)
    """
    cmd = "journalctl"
    if kernel_only:
        cmd += " -k"
    if length:
        cmd += f" -n {length}"
    if reverse:
        cmd += " -r"
    if since:
        # since can be used with '+' and '-', see man journalctl
        cmd += f" -S {since}"
    if options:
        cmd += " " + " ".join(options)

    if grep:
        cmd += f" | grep '{grep}'"

    ret, journal = run(cmd, return_output=return_output, verbose=verbose)
    if ret:
        sts_print(f"FAIL: cmd '{cmd}' failed with retcode {ret}.")
        return None
    if not return_output:
        return ret

    # shorten the hostname to match /var/log/messages format
    data = ""
    for line in journal.splitlines():
        line = line.split()  # noqa: PLW2901
        if len(line) < 4:
            continue
        line[3] = line[3].split(".")[0]
        data += " ".join(line) + "\n"
    return ret, data


def edit_config(
    file: str,
    parameters: dict,
    update: bool = False,
    file_error: bool = True,
    list_values: bool = True,
) -> bool:
    """Merges configuration file with dict using configobj
    For more complex operations see https://configobj.readthedocs.io.

    Args:
      file: Path to the configuration file.
      parameters: Accepts also nested sections, e.g. {'logging':{'a': 'a.log', 'b': 'b.log'}}.
      update: Use update() instead of merge(). Will remove section entries not in parameters dict.
      file_error: Set False to allow creating new files.
      list_values: If False, values are not parsed for list values. Single line values are not unquoted.
    """
    try:
        config = ConfigObj(file, file_error=file_error, list_values=list_values)
    except OSError as e:
        print(e)
        return False

    config.filename = file

    sts_print(f"INFO: Updating {file}")
    if update:
        config.update(parameters)
    else:
        config.merge(parameters)

    config.write()
    return True


def remove_from_config(file, parameters_to_remove, section=None, warn=True) -> bool:
    """Removes objects from a configuration file.

    Args:
      file: (str) Path to the configuration file.
      parameters_to_remove: (list) Parameters to remove.
      section: (str) Specify section of config file parameters are nested in.
      warn: (bool) Set False to supress warning when deleting nonexistent parameter.
    """
    try:
        config = ConfigObj(file, file_error=True)
    except OSError as e:
        sts_print("FAIL: Unable to open {}. It might not exist")
        print(e)
        return False

    config.filename = file
    fail = False
    for param in parameters_to_remove:
        sts_print(f'INFO: Removing "{param}" from {file}')
        try:
            if section:
                config[section].pop(param)
            else:
                config.pop(param)
        except KeyError:
            if warn:
                sts_print("WARN: Parameter to remove is not in config")
            fail = True

    config.write()
    if fail:
        return False
    return True


def generate_sosreport(skip_plugins=None, plugin_timeout=300, timeout=900):
    """Generates a sos report.

    Args:
      skip_plugins: (string) comma separated list of plugins to skip (no space after comma)
      plugin_timeout: (int) timeout in seconds to allow each plugin to run for (only applicable to rhel-8+)
      timeout: (int) timeout for the sosreport proces in seconds. Use `None` for no timeout.
    """
    cmd = f"sos report --batch --plugin-timeout {plugin_timeout}"
    dist = dist_ver()
    if dist < 8:
        cmd = "sosreport --batch"

    if not install_package("sos", check=True):
        print("FAIL: unable to install sos package")
        return False

    mount_flag = False
    if is_mounted("/var/crash"):
        print("INFO: Unmounting /var/crash to avoid sosreport being hang there")
        umount("/var/crash")
        mount_flag = True

    if skip_plugins:
        cmd = cmd + f" --skip-plugins {skip_plugins}"

    ret_code, sosreport_ret = run(cmd, return_output=True, timeout=timeout)
    if ret_code != 0:
        print("FAIL: sosreport command failed")
        if mount_flag:
            mount("/var/crash")
        return False

    sos_report = None
    for line in sosreport_ret.split("\n"):
        if "/tmp/sosreport" in line:
            sos_report = line.strip()
            break

    if mount_flag:
        mount("/var/crash")

    return sos_report
