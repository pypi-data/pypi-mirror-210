import logging


def set_logger(level: int = 0) -> None:
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
    LOG_LEVELS = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }

    # Set default format and log level specified by user.
    # By default application is not using CRITICAL level at all,
    # so setting level to 0 disables logging entirely.
    # When level is not in dictionary, let's use the most verbose mode,
    # because it probably means that user specified too much -v flags.
    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVELS.get(level, 3), force=True)


logger = logging.getLogger("metadefender-scan")
