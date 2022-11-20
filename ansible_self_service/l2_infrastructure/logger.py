import logging

from ansible_self_service.l4_core.protocols import LoggerProtocol


class BasicLogger(LoggerProtocol):
    def debug(self, msg: str):
        logging.debug(msg)

    def info(self, msg: str):
        logging.info(msg)

    def warning(self, msg: str):
        logging.warning(msg)

    def error(self, msg: str):
        logging.error(msg)
