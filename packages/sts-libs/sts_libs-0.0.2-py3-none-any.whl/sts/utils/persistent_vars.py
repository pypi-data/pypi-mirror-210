"""persistent_vars.py: Module to share variables between scripts using writing to file."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
from pathlib import Path
from typing import Any, Literal, Tuple, Union

from sts.utils.cmdline import run


def get_persistent_files_dir() -> str:
    """Returns directory of persistent vars."""
    return "/var/tmp/"


def get_persistent_vars_file_name() -> str:
    """Returns file name of persistent vars file."""
    return "FILE_NAMES"


def exists_persistent_vars_file() -> bool:
    """Returns True if persistent vars filer exists, default /tmp/FILE_NAMES."""
    return Path(get_persistent_files_dir() + get_persistent_vars_file_name()).exists()


def _check_0_start(value) -> bool:
    """Checks if value starts with 0 but is not 0. This prevents from changing '02314' but allows changing '0'.

    Args:
      value (string): value to check
    """
    return all([value.startswith("0"), value != "0"])


def _read_to_float(value: Union[str, Any]) -> Tuple[bool, Any]:
    """Args:
      value (Any, preferable string): Value to try to change to float.

    Returns:
      tuple: (False, original value) or (True, float(value))
    """
    try:
        return (True, float(value)) if not all([_check_0_start(value), not value.startswith("0.")]) else (False, value)
    except ValueError:
        return False, value


def _read_to_int(value: Union[str, Any]) -> Tuple[bool, Any]:
    """Args:
      value (Any, preferable string): Value to try to change to integer.

    Returns:
      tuple: (False, original value) or (True, int(value))
    """
    try:
        return (True, int(value)) if not _check_0_start(value) else (False, value)
    except ValueError:
        return False, value


def _read_to_list(value: Union[str, Any]) -> Tuple[bool, Any]:
    """This does not support nested lists!

    Args:
      value (Any, preferable string): Value to try to change to list

    Returns:
      tuple.: (False, original value) or (True, list(value))
    """
    try:
        if value.startswith("["):
            return True, value[1:-1].split(", ")
        else:  # noqa: RET505
            return False, value
    except AttributeError:
        return False, value


def _read_to_none(value: Union[str, Any]) -> Tuple[bool, Any]:
    """Args:
      value (Any, preferable string): Value to try to change to None.

    Returns:
      tuple: (False, original value) or (True, None)
    """
    if value == str(None):
        return True, None
    return False, value


def _read_to_bool(value: Union[str, Any]) -> Tuple[bool, Any]:
    """Checks if value is "true" or "false" string, returns bool equivalent.

    Args:
      value (Any, preferable string): Value to try to change to bool

    Returns:
      tuple.: (False, original value) or (True, True/False)
    """
    if value.lower() == "true":
        return True, True
    if value.lower() == "false":
        return True, False
    return False, value


def _remove_quotes(value: str) -> str:
    """Removes any characters ' or " from any string.

    Args:
      value (string): Value to remove quotes from

    Returns:
      original string without quotes
    """
    return "".join([char for char in value if char not in ["'", '"']])


def recursive_read_value(value: str) -> Any:
    """Given string tries to change type of the string to different types. Returns value of new type of possible.
    Supported new types: list, int, float, None, bool
    Example: str("21654") changes to int(21654).

    Args:
      value (string): value to be retyped

    Returns:
      value of new type
    """
    value = _remove_quotes(value)
    for func in [
        _read_to_list,
        _read_to_int,
        _read_to_float,
        _read_to_none,
        _read_to_bool,
    ]:
        ret, value = func(value)
        if ret:
            if func == _read_to_list:
                return [recursive_read_value(val) for val in value]
            return value
    return value


def read_var(var: str) -> Any:
    """Args:
      var (string): variable name saved in file of the same name in get_persistent_files_dir() location.

    Returns:
      Any(_recursive_read_value): Value saved in the file with proper type
    """
    if not Path(get_persistent_files_dir() + var).is_file():
        if var != get_persistent_vars_file_name():
            print(f"WARN: File {get_persistent_files_dir() + var} does not exist.")
        return None
    with Path(get_persistent_files_dir() + var).open() as f:
        value = f.read()
    return recursive_read_value(value)


def read_env(var: str) -> Any:
    """This does not handle KeyError, it is intentional.

    Args:
      var (string): os.environ variable

    Returns:
      Any(_recursive_read_value).: value of environ variable
    """
    return recursive_read_value(os.environ[var])


def _write_to_string(value: Any) -> Tuple[bool, Union[str, Any]]:
    """Args:
      value (Any): Value to try to change to string.

    Returns:
      tuple: (False, original value) or (True, str(value))
    """
    try:
        return True, str(value)
    except ValueError:
        return False, value


def _write_from_list(value: Any) -> Tuple[bool, Union[str, Any]]:
    """Args:
      value: Value to try to change to list.

    Returns:
      tuple.: (False, original value) or (True, str(list(value)) without '' or "").
    """
    if isinstance(value, list):
        return True, f"[{', '.join([str(x) for x in value[:]])}]"
    return False, value


def write_var(var: dict) -> Literal[0, 1]:
    """Args:
      var (dict): variable to write to file in format {var_name: var_value}.

    Returns:
      int: 0 pass, 1 fail
    """
    if not isinstance(var, dict):
        print("FAIL: var manipulation requires var as a dict. {name: value}")
        return 1
    file_name = list(var.keys()).pop()
    write_file(file_name, list(var.values()).pop())
    add_file_to_list(file_name)
    return 0


def write_file(file_name: str, value) -> None:
    """Args:
      file_name (string): File name to write to location get_persistent_files_dir() + file_name
      value: value to write to the file.

    Returns:
      None: None
    """
    with Path(get_persistent_files_dir() + file_name).open("w") as f:
        for func in (_write_from_list, _write_to_string):
            ret, value_to_write = func(value)
            if ret:
                break
        f.write(value_to_write)


def add_file_to_list(file_name: str) -> None:
    """This is for adding file names to persistent list, so we can clean them later.

    Args:
      file_name (string): name of the persistent vars file

    Returns:
      None: None
    """
    file_names = read_var(get_persistent_vars_file_name()) or []
    if file_name not in file_names:
        file_names.append(file_name)
    write_file(get_persistent_vars_file_name(), file_names)


def clean_var(var: str) -> Literal[0]:
    """Cleans persistent var file from filesystem.

    Args:
      var (string): variable name to clean

    Returns:
      int.: 0
    """
    Path(get_persistent_files_dir() + var).unlink()
    return 0


def clean_all_vars(prefix: str = "") -> Literal[0]:
    """This uses list of persistent vars files from get_persistent_files_dir() and get_persistent_vars_file_name() and
    cleans them from filesystem.

    Args:
      prefix (string): prefix to clean only some, for example "LSM_"

    Returns:
      int.: 0
    """
    prefix = prefix or ""
    variables = get_persistent_var_names(prefix)
    if exists_persistent_vars_file() and get_persistent_vars_file_name() not in variables:
        variables.append(get_persistent_vars_file_name())
    print("INFO: Will clean these variables: \n\t%s" % "\n\t".join(variables))
    for var in variables:
        clean_var(var)
    return 0


def get_persistent_var_names(prefix: str = "") -> list:
    """Gets persistent vars from get_persistent_vars_file_name() file
       or filesystem in get_persistent_files_dir() location.

    Args:
      prefix (string): prefix to clean only some, for example "LSM_"

    Returns:
      list.: List of persistent vars file names having the specified prefix
    """
    if exists_persistent_vars_file():
        variables = read_var(get_persistent_vars_file_name())
    else:
        _, variables = run(f"ls -la {get_persistent_files_dir()}", return_output=True, verbose=False)
        variables = [line.split().pop() for line in variables.splitlines()[3:]]
    return [value for value in variables if value.startswith(prefix)]
