"""Common logging setup."""
# vim: tw=120 wm=120 ts=4 sw=4 smarttab smartindent expandtab
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
__logger_channel = logging.StreamHandler()
__logger_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s - %(module)s:%(lineno)d: %(message)s")
__logger_formatter.default_time_format = "%Y-%m-%d %H:%M:%S"
__logger_formatter.default_msec_format = "%s.%03d"
__logger_channel.setFormatter(__logger_formatter)
logger.addHandler(__logger_channel)
