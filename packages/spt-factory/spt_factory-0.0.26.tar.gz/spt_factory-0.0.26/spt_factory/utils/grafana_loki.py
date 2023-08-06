from typing import Dict, Any

import logging
import logging_loki


class GrafanaLoki:
    name = 'loki_logger'

    def __init__(
        self, url: str,
        tags: Dict[str, Any] = {},
        username: str = None,
        password: str = None
    ):
        self.url = url
        self.tags = tags
        self.__auth = (username, password)

    def get_logger(self) -> logging.Logger:
        """Returns logger with appended loki handler"""
        logger = logging.getLogger(self.name)
        logger.addHandler(self.get_handler())
        return logger

    def get_handler(self) -> logging_loki.LokiHandler:
        """
        Returns loki logging handler
        """
        return logging_loki.LokiHandler(
            url=self.url,
            tags=self.tags,
            auth=self.__auth,
            version="1",
        )
