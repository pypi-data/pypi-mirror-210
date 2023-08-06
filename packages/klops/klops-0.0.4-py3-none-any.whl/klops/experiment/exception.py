"""Experiment exception module.

Put all the exception handlers here.
"""

class ExperimentFailedException(Exception):
    """Experiment Failed Exception

    Raised when the experiment got failed.
    """

    def __init__(self, message: str, *args: object) -> None:
        """The Experiment Failed Constructor

        Message would store the root causes.
        Args:
            message (str): _description_
        """
        self.message = message
        super(ExperimentFailedException, self).__init__(*args)

    def __str__(self):
        return self.message


class InvalidArgumentsException(ValueError):
    """Invalid Arguments Passed

    Raised when the given arguments are invalid.
    """

    def __init__(self, message: str,*args: object) -> None:
        """The Exception Constructor

        Args:
            message (str): message that would be displayed to the user.
        """
        self.message = message
        super(InvalidArgumentsException, self).__init__(*args)

    def __str__(self) -> str:
        return self.message


class LogMetricException(Exception):
    """Log Metric Exception

    Raised when the Logging the metrics are failed.
    """

    def __init__(self, message: str, *args: object) -> None:
        """The Log Metric Exception Constructor

        Message would store the root causes.
        Args:
            message (str): _description_
        """
        self.message = message
        super(LogMetricException, self).__init__(*args)

    def __str__(self):
        return self.message


class UnknownExperimentTunerTypeException(ValueError):
    """Unknown Experiment Tunner Exception

    Raised when the tuner is not one of `default` | `gridsearch` | `hyperopt`.
    """

    def __init__(self, message, *args: object) -> None:
        """The Exception Constructor.

        Args:
            message (_type_): The Exception message would be displayed.
        """
        self.message = message
        super(UnknownExperimentTunerTypeException, self).__init__(*args)

    def __str__(self) -> str:
        return self.message
