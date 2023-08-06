#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import unittest

from sts.utils.persistent_vars import recursive_read_value


class TestChangeType(unittest.TestCase):
    def test_to_float(self):
        assert recursive_read_value("0.1") == 0.1
        assert recursive_read_value("1.0") == 1.0
        assert recursive_read_value("1.1") == 1.1

    def test_to_int(self):
        assert recursive_read_value("0") == 0
        assert recursive_read_value("1") == 1
        assert recursive_read_value("1234") == 1234

    def test_to_str(self):
        assert recursive_read_value("0123") == "0123"
        assert recursive_read_value("string") == "string"

    def test_to_none(self):
        assert recursive_read_value("None") is None

    def test_to_bool(self):
        assert recursive_read_value("true") is True
        assert recursive_read_value("false") is False
        assert recursive_read_value("True") is True
        assert recursive_read_value("False") is False
        assert recursive_read_value("TRUE") is True
        assert recursive_read_value("FALSE") is False

    def test_to_list(self):
        assert recursive_read_value("[1, string]") == [1, "string"]
        assert recursive_read_value("[None]") == [None]
        assert recursive_read_value("['string', 0.1]") == ["string", 0.1]
        assert recursive_read_value("['/dev/sda', '/dev/sdb', '/dev/sdc']") == [
            "/dev/sda",
            "/dev/sdb",
            "/dev/sdc",
        ]
