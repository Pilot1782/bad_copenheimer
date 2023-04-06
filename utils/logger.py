import logging
import os
import sys

norm = sys.stdout


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, level: int = logging.INFO):
        self.logger = logger
        self.level = level
        self.linebuf = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

    def read(self):
        with open("log.log", "r") as f:
            return f.read()


# This code is used in the main function to set the logging level to INFO and the format to the specified format
# The logging level is set to INFO so that only the INFO level and above will be logged
# The logging format is set to the specified format so that the time, level, name, and message will be logged
# The logging file is set to log.log so that the logs will be written to the log.log file
# The logging file mode is set to append so that the logs will be appended to the log.log file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
    filename="log.log",
    filemode="a",
)

# This code is used in the main function to set the logger name to STDOUT and the logging level to INFO
log = logging.getLogger("STDOUT")

# This code is used in the main function to set the stream to the logger and the logging level to INFO
out = StreamToLogger(log, logging.INFO)

# This code is used in the main function to set the standard output to the stream and the logging level to ERROR
sys.stdout = out

# This code is used in the main function to set the standard error to the stream and the logging level to ERROR
sys.stderr = StreamToLogger(log, logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
    filename=".." + ("\\" if os.name == "nt" else "/") + "log.log",
    filemode="a",
)

log = logging.getLogger("STDOUT")
out = StreamToLogger(log, logging.INFO)
sys.stdout = out
sys.stderr = StreamToLogger(log, logging.ERROR)


class Logger:
    def __init__(self, DEBUG=False):
        """Initializes the logger class

        Args:
            DEBUG (bool, optional): Show debugging. Defaults to False.
        """
        self.DEBUG = DEBUG
        self.logger = logging

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        sys.stdout = norm  # output to console
        print(message)
        sys.stdout = out  # output to log.log
        self.logger.error(message)

    def debug(self, *args, **kwargs):
        self.logger.debug(" ".join([str(arg) for arg in args]))
        if self.DEBUG:
            self.print(*args, **kwargs)

    def warning(self, message):
        self.logger.warning(message)

    def critical(self, message):
        self.logger.critical(message)

    def exception(self, message):
        self.logger.exception(message)

    def read(self):
        with open("log.log", "r") as f:
            return f.read()

    def print(self, *args, **kwargs):
        msg = " ".join([str(arg) for arg in args])
        sys.stdout = norm  # output to console
        print(msg, **kwargs)
        sys.stdout = out  # output to log.log
        self.info(msg)

    def clear(self):
        with open("log.log", "w") as f:
            f.write("")

    def __repr__(self):
        return self.read()

    def __str__(self):
        return self.read()
