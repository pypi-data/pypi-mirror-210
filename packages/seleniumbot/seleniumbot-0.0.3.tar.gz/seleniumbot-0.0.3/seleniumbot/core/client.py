from __future__ import annotations

import random
import time

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire.webdriver import Chrome

from seleniumbot.utils import Randomizer


class SeleniumClient:

    def __init__(self, options: Options | None = None, seleniumwire_options: dict | None = None, **kwargs):
        self._driver = self.__get_driver(options, seleniumwire_options)

        self.__min_action_delay = kwargs.get('min_action_delay', 0.7)
        self.__max_action_delay = kwargs.get('max_action_delay', 3)
        self.__webdriver_wait_time = kwargs.get('webdriver_wait_time', 60)

    @staticmethod
    def _delay(foo):
        def wrapper(self, *args, **kwargs):
            delay = random.uniform(self.__min_action_delay, self.__max_action_delay)
            time.sleep(delay)
            return foo(self, *args, **kwargs)

        return wrapper

    @_delay
    def goto(self, link: str) -> None:
        self._driver.get(link)

    @_delay
    def scroll(self, height: int, second_height: int | None = None) -> None:
        if second_height:
            height = Randomizer.between(height, second_height)

        direction = '__add__' if height > 0 else '__sub__'
        comparison = '__lt__' if height > 0 else '__gt__'
        height = abs(height)

        current_height = int(self._driver.execute_script('return document.documentElement.scrollTop'))
        target_height = getattr(current_height, direction)(height)
        while getattr(current_height, comparison)(target_height):
            current_height = getattr(current_height, direction)(random.randint(10, 100))
            self._driver.execute_script(f'window.scrollTo(0, {current_height})')

            time.sleep(Randomizer.between(0.01, 0.1))

    @_delay
    def find_elements(self, by: str, value: str | None) -> list[WebElement]:
        elements = self._driver.find_elements(by, value)
        elements = [element for element in elements if element.is_displayed()]
        return elements

    @_delay
    def find_element(self, by: str, value: str | None) -> WebElement | None:
        expect = expected_conditions.presence_of_element_located((by, value))
        return WebDriverWait(self._driver, self.__webdriver_wait_time).until(expect)

    @_delay
    def send_keys(self, element: WebElement, value: str) -> None:
        element.send_keys(value)

    def __del__(self):
        self._driver.close()

    def __get_driver(self, options: Options | None, seleniumwire_options: dict | None) -> Chrome:
        if not options:
            options = self.__get_default_options()
        if not seleniumwire_options:
            seleniumwire_options = {}

        driver = Chrome(chrome_options=options, seleniumwire_options=seleniumwire_options)
        return driver

    @staticmethod
    def __get_default_options() -> Options:
        options = Options()
        options.add_argument('window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')

        return options
