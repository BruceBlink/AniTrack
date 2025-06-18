import logging
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import RotatingFileHandler


def init_logger(level=logging.DEBUG, log_file=None):
    """
    全局日志初始化：
      - level：日志级别
      - log_file：可选，写入文件，自动切分
    """
    logger = getLogger()  # root logger
    logger.setLevel(level)

    fmt = "%(asctime)s %(levelname)-8s [%(name)s:%(lineno)d] %(message)s"
    formatter = Formatter(fmt)

    # 控制台
    sh = StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # 如果指定了 log_file，再加一个滚动文件 handler
    if log_file:
        fh = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
