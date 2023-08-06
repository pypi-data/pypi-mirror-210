from remotemanager import SendableMixin, LoggingMixin


class placeholder_option(SendableMixin, LoggingMixin):
    """
    .. warning::
        This class is intended to be subclassed by the optional and required
        placeholders.

    Stub class to sit in place of an option within a computer.

    Args:
        mode (string):
            storage mode, required or optional
        flag (string):
            flag to append value to (`--nodes`, `--walltime`, etc)
    """

    def __init__(self, mode, flag, min, max):
        self._mode = mode
        self._flag = flag
        self._value = None
        self._bool = False

        self._min = min
        self._max = max

    def __hash__(self):
        return hash(self._mode)

    def __str__(self):
        return str(self.value)

    def __bool__(self):
        """
        Makes objects "falsy" if no value has been set, "truthy" otherwise
        """
        return self.value is not None

    @property
    def flag(self):
        return self._flag

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def value(self):
        if hasattr(self, "default") and self._value is None:
            return self.default

        return self._value

    @value.setter
    def value(self, value):
        try:
            value / 1
            isnumeric = True
        except TypeError:
            isnumeric = False

        if isnumeric:
            if self.min is not None and value < self.min:
                raise ValueError(
                    f"{value} for {self.flag} " f"is less than minimum value {self.min}"
                )
            if self.max is not None and value > self.max:
                raise ValueError(
                    f"{value} for {self.flag} " f"is more than maximum value {self.max}"
                )

        self._bool = True
        self._value = value


class required(placeholder_option):
    """
    This option is _required_, and should raise an error if no value is found

    Args:
        flag (string):
            flag to append value to (`--nodes`, `--walltime`, etc)
    """

    def __init__(self, flag, min=None, max=None):
        super().__init__("required", flag, min, max)


class optional(placeholder_option):
    """
    This option is not required, and should have an accessible default if
    no value is found

    Args:
        flag (string):
            flag to append value to (`--nodes`, `--walltime`, etc)
        default:
            default value to use if none is assigned
    """

    def __init__(self, flag, default=None, min=None, max=None):
        super().__init__("optional", flag, min, max)

        self._default = default

    @property
    def default(self):
        try:
            return self._default()
        except TypeError as E:
            self._logger.warning(f"recieved error from default attempt: {E}")
            return self._default
