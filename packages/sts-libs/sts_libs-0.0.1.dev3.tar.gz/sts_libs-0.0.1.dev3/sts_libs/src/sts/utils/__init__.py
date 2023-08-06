#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import inspect
import re
import sys


def sts_print(string):
    # name of the module that called the function
    module_name = inspect.currentframe().f_back.f_globals["__name__"]
    string = re.sub("DEBUG:", "DEBUG:(" + module_name + ")", string)
    string = re.sub("FAIL:", "FAIL:(" + module_name + ")", string)
    string = re.sub("FATAL:", "FATAL:(" + module_name + ")", string)
    string = re.sub("WARN:", "WARN:(" + module_name + ")", string)
    print(string)
    sys.stdout.flush()
    if "FATAL:" in string:
        raise RuntimeError(string)
