import sys
import logging


class LoggerRedirector:

    """
    Trickush to get unittest to display logs of code failing tests. See
    https://stackoverflow.com/questions/69200881/how-to-get-python-unittest-to-show-log-messages-only-on-failed-tests
    for more details.
    """

    # Keep a reference to the real streams so we can revert
    _real_stdout = sys.stdout
    _real_stderr = sys.stderr

    @staticmethod
    def all_loggers():
        loggers = [logging.getLogger()]
        loggers += [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        return loggers

    @classmethod
    def redirect_loggers(cls, fake_stdout=None, fake_stderr=None):
        if ((not fake_stdout or fake_stdout is cls._real_stdout)
                and (not fake_stderr or fake_stderr is cls._real_stderr)):
            return
        for logger in cls.all_loggers():
            for handler in logger.handlers:
                if hasattr(handler, 'stream'):
                    if handler.stream is cls._real_stdout:
                        handler.setStream(fake_stdout)
                    if handler.stream is cls._real_stderr:
                        handler.setStream(fake_stderr)

    @classmethod
    def reset_loggers(cls, fake_stdout=None, fake_stderr=None):
        if ((not fake_stdout or fake_stdout is cls._real_stdout)
                and (not fake_stderr or fake_stderr is cls._real_stderr)):
            return
        for logger in cls.all_loggers():
            for handler in logger.handlers:
                if hasattr(handler, 'stream'):
                    if handler.stream is fake_stdout:
                        handler.setStream(cls._real_stdout)
                    if handler.stream is fake_stderr:
                        handler.setStream(cls._real_stderr)