from __future__ import annotations

import time
from abc import ABC, abstractmethod

from selenium.common.exceptions import WebDriverException

from seleniumbot.core.client import SeleniumClient
from seleniumbot.utils import get_logger

logger = get_logger()


class Action(ABC):
    name: str
    coefficient: float

    # If after specific action previous actions may be outdated, make this property True
    flush_actions: bool = False

    def execute(self, client: SeleniumClient, last_action: Action | None):
        try:
            logger.info(f'<{self.name}> started')
            result = self._execute(client, last_action)
            logger.info(f'<{self.name}> ended')
            return result
        except WebDriverException as e:
            logger.error(f'<{self.name}> Could not be performed. Error - {e}')

        # Since the time when `execute` function is called and someone is expecting result, it's given as list.
        return []

    @abstractmethod
    def _execute(self, client: SeleniumClient, last_action: Action | None):
        raise NotImplemented

    def __eq__(self, other):
        return self.name == other.name


class AFKAction(Action):
    name = 'AFKAction'
    coefficient = 0

    def _execute(self, client: SeleniumClient, last_action: Action | None) -> list[Action]:
        time.sleep(5)

        # Since this action can be used as `navigation` action, it must return some actions.
        return []
