"""cli_tools.py: Module to provide tools of wrapping command line tools for further usage."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from sts.utils import sts_print


class WrongCommandExceptionError(Exception):
    def __init__(self, cmd):
        self.command = cmd
        super().__init__()

    def __str__(self):
        return repr(WrongCommandExceptionError.__name__ + ", caused by " + repr(self.command))


class WrongArgumentExceptionError(Exception):
    def __init__(self, arg, cmd=None, args=None):
        self.argument = arg
        self.command = cmd
        self.arguments = args
        super().__init__()

    def __str__(self):
        return repr(WrongArgumentExceptionError.__name__ + ", caused by " + repr(self.argument))


class FailedCheckExceptionError(Exception):
    def __init__(self, arg=None):
        self.argument = arg
        super().__init__()

    def __str__(self):
        message = repr(FailedCheckExceptionError.__name__)
        if self.argument:
            message += ", caused by " + repr(self.argument)
        return message


class Wrapper:
    def __init__(self, commands, arguments, disable_check):
        self.commands = commands
        self.arguments = arguments
        self.disable_check = disable_check

    def _add_command(self, cmd):
        # Checks if given command is provided by CLI and returns its correct syntax
        if cmd in self.commands:
            return self.commands[cmd]
        raise WrongCommandExceptionError(cmd)

    def _get_arg(self, name):
        if not self.disable_check:
            if name in self.arguments:
                return self.arguments[name][1]
            raise WrongArgumentExceptionError(name)
        return self.arguments[name][1]

    def _get_cmd(self, name):
        if self.disable_check:
            return self.commands["all"]
        if name in self.arguments:
            return self.arguments[name][0]
        raise WrongCommandExceptionError(name)

    @staticmethod
    def _get_value(string, command, return_type=str):
        _value = string.split(command)[1].split()[0]
        try:
            value = return_type(_value)
        except ValueError as e:
            sts_print(f"WARN: Got ValueError: {e}.")
            return None
        return value

    def _get_possible_arguments(self, command=None):
        # Returns possible arguments for said command if specified
        args = []
        if command:
            for key in list(self.arguments.keys()):
                if list(self.commands.keys())[list(self.commands.values()).index(command)] in self._get_cmd(key):
                    args.append(key)
        else:
            args = list(self.arguments.keys())
        return args

    @staticmethod
    def _add_value(value, command, argument):
        if argument[-1:] in ["=", "&"]:
            if argument[-1:] == "&":
                argument = argument[:-1] + " "
            if isinstance(value, list):
                # allows to use repeatable arguments as a list of values
                for val in value:
                    command += argument + "'" + str(val) + "'"
            else:
                command += argument + "'" + str(value) + "'"
        else:
            command += argument
        return command

    def _check_allowed_argument(self, arg, command):
        if arg not in self.arguments and not self.disable_check:
            raise WrongArgumentExceptionError(arg)
        cmd = command.split()[0]
        args = self._get_possible_arguments(cmd)
        if arg not in args:
            raise WrongArgumentExceptionError(arg, cmd, args)

    def _add_argument(self, arg, value, command):
        # Checks if given argument is allowed for given command and adds it to cmd string
        self._check_allowed_argument(arg, command)
        return self._add_value(value, command, self._get_arg(arg))

    def _add_arguments(self, cmd, **kwargs):
        command = cmd
        for kwarg in kwargs:
            # skip adding this argument if the value is False
            if kwargs[kwarg] is False:
                continue
            command = self._add_argument(kwarg, kwargs[kwarg], command)
        return command
