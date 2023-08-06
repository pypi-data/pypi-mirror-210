"""qemu_img.py: Module to manipulate disk image using QEMU disk image utility."""
from pathlib import Path

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from sts import linux
from sts.utils import sts_print
from sts.utils.cmdline import run

_QCOW_SUPPORTED_OPTIONS = [
    "compat",
    "backing_file",
    "encryption",
    "cluster_size",
    "preallocation",
    "lazy_refcounts",
]


def _get_package_name():
    return "qemu-img"


def _get_image_file(name, image_path):
    return f"{image_path}/{name}.img"


def get_qcow_supported_options():
    """Return supported options for qcow image.

    Returns:
      List of strings.
    """
    return _QCOW_SUPPORTED_OPTIONS


def install_qemu_img():
    """Install qemu-img tool.

    Returns:
    True: If qemu-img is installed correctly
    False: If some problem happened
    """
    if not linux.install_package(_get_package_name()):
        sts_print(f"FAIL: Could not install {_get_package_name()}")
        return False
    return True


def qemu_create(filename, size="1024", fmt=None, img_path="/var/tmp", **options):
    """Create the new disk image.

    Args:
      filename: is a disk image filename
      size: is the disk image size in bytes
      fmt: is the disk image format
      img_path: is the full path to output directory
      **options: see supported options for a qcow image

    Returns:
    True: if success
    False: in case of failure
    """
    if not linux.is_installed(_get_package_name()):
        install_qemu_img()
    if not filename:
        sts_print("FAIL: qemu_create() requires parameter filename")
        return False
    if img_path:
        filename = _get_image_file(filename, img_path)
    cmd = _get_package_name() + " create "
    if fmt is not None:
        cmd += f"-f {fmt}"
    if fmt == "qcow2" and options:
        cmd += " -o "
        option = [str(i) + "=" + str(options[i]) for i in options if i in _QCOW_SUPPORTED_OPTIONS]
        cmd += ",".join(option)
    cmd += f" {filename} {size}"
    ret = run(cmd)
    if ret != 0:
        sts_print("FAIL: Could not create disk image.")
        return False
    return True


def delete_image(name, image_path="/var/tmp"):
    """Delete the disk image.

    Args:
      name: is the image filename
      image_path: is the full path to the image directory

    Returns:
    True: if success
    False: in case of failure
    """
    if not name:
        sts_print("FAIL: delete_image() - requires name parameter")
        return False

    print(f"INFO: Deleting image device {name}")
    fname = _get_image_file(name, image_path)
    if Path(fname).is_file():
        cmd = f"rm -f {fname}"
        retcode = run(cmd)
        if retcode != 0:
            sts_print(f"FAIL: Could not delete image disk file {fname}")
            return False
    return True
