"""
Base module that handle element search strategy
"""

from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from ..common.exceptions import Exceptions
from ..common.logger import Logger
from ..common.constants import Constants
from colorama import Fore

log = Logger(Constants.FRAMEWORK)


class SeleNew:
    def __init__(self, driver, go_around=3):
        """
        To initialize browser that is needed
        :param driver: name of browser
        :param go_around: attempts number
        """
        self.driver = driver
        self.go_around = go_around

    def _find_element(self, locator, timeout=3, element_state=Constants.SINGLE_VISIBLE):
        """
        To find element
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        :return: element that was found
        """
        element = None
        attempt = 0
        while attempt < self.go_around:
            try:
                if element_state == Constants.SINGLE_VISIBLE:
                    element = WebDriverWait(self.driver, timeout=timeout).until(
                        ec.visibility_of_element_located(self._get_by_locator(locator))
                    )
                elif element_state == Constants.CLICKABLE:
                    element = WebDriverWait(self.driver, timeout=timeout).until(
                        ec.element_to_be_clickable(self._get_by_locator(locator))
                    )
                elif element_state == Constants.INVISIBLE:
                    element = WebDriverWait(self.driver, timeout=timeout).until(
                        ec.invisibility_of_element(self._get_by_locator(locator))
                    )
                elif element_state == Constants.MULTIPLE_VISIBLE:
                    elements = WebDriverWait(self.driver, timeout=timeout).until(
                        ec.visibility_of_all_elements_located(self._get_by_locator(locator))
                    )
                    return elements
                else:
                    log.logger_method(
                        f"[{Constants.FRAMEWORK}]: Requested state {element_state} not supported. "
                        f"Supported states: {Constants.SUPPORTED_ELEMENT_STATES}",
                        Fore.RED)
                    raise ValueError(Exceptions.StateNotFound.format(element_state))
                break
            except TimeoutException:
                attempt += 1
                if attempt > 1:
                    log.logger_method(f"[{Constants.FRAMEWORK}]: Go around to find element: {locator} "
                                      f"#{attempt} attempt", Fore.YELLOW)
        if not element:
            log.logger_method(
                f"[{Constants.FRAMEWORK}]: Requested element with '{element_state}' state not found "
                f"after {attempt} attempts",
                Fore.RED)
            raise TimeoutException(Exceptions.ElementNotFound.format(locator, attempt))
        return element

    def click(self, locator, timeout=3, element_state=Constants.CLICKABLE):
        """
        Click on element
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        element.click()

    def send_keys(self, locator: str, text: str, timeout: int = 3, element_state: str = Constants.SINGLE_VISIBLE):
        """
        Type text on field
        :param text: text to type in the field
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        element.send_keys(text)

    def switch_to_window(self, which_window: int):
        """
        Switch to window
        :param which_window: window index
        """
        required_window = self.driver.window_handles[which_window]
        self.driver.switch_to.window(required_window)

    def switch_to_frame(self, locator: str, timeout: int = 3, element_state: str = Constants.SINGLE_VISIBLE):
        """
        Switch to frame
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        """
        frame = self._find_element(locator, timeout=timeout, element_state=element_state)
        self.driver.switch_to.frame(frame)

    def switch_out_frame(self):
        """
        Switch out to main html
        """
        self.driver.switch_to.default_content()

    def hover(self, locator: str, timeout: int = 3, element_state: str = Constants.SINGLE_VISIBLE):
        """
        Hover over element
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        ActionChains(self.driver).move_to_element(element).perform()

    def select_by_value(self, locator: str, value: str, timeout: int = 3, element_state: str = Constants.SINGLE_VISIBLE):
        """
        Select dropdown option by value
        :param value: value
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        Select(element).select_by_value(value)

    def select_by_index(self, locator: str, index: str, timeout: int = 3, element_state: str = Constants.SINGLE_VISIBLE):
        """
        Select dropdown option by index
        :param index: index
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        Select(element).select_by_index(index)

    def select_by_text(self, locator: str, text: str, timeout: int = 3, element_state: str = Constants.SINGLE_VISIBLE):
        """
        Select dropdown option by text
        :param text: text
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        Select(element).select_by_visible_text(text)

    def get_text(self, locator: str, timeout: int = 3, element_state: str = Constants.SINGLE_VISIBLE):
        """
        Get text from element
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        :return: text
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        return element.text

    def get_attribute(self, locator: str, attribute_name: str, timeout: int = 3,
                      element_state: str = Constants.SINGLE_VISIBLE):
        """
        Get attribute of element
        :param attribute_name: name of the attribute
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        :return: attribute
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        return element.get_attribute(attribute_name)

    def drag_and_drop(self, source_locator: str, target_locator: str, timeout: int = 3,
                      element_state: str = Constants.SINGLE_VISIBLE):
        """
        Drag and drop element
        :param target_locator: locator to element to be dragged
        :param source_locator: locator to element on which dragged element to be dropped
        :param timeout: required seconds
        :param element_state: required state
        """
        source_element = self._find_element(source_locator, timeout=timeout, element_state=element_state)
        target_element = self._find_element(target_locator, timeout=timeout, element_state=element_state)
        action_chains = ActionChains(self.driver)
        action_chains.drag_and_drop(source_element, target_element).perform()

    def drag_to_coordinates(self, locator: str, x_offset: int, y_offset: int, timeout: int = 3,
                            element_state: str = Constants.SINGLE_VISIBLE):
        """
        Drag to offset coordinates
        :param locator: locator
        :param x_offset: coordinate
        :param y_offset: coordinate
        :param timeout: required seconds
        :param element_state: required state
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        action_chains = ActionChains(self.driver)
        action_chains.drag_and_drop_by_offset(element, x_offset, y_offset).perform()

    def press_key(self, locator: str, key: str, timeout: int = 3, element_state: str = Constants.SINGLE_VISIBLE):
        """
        Press key
        :param locator: locator
        :param key: key
        :param timeout: required seconds
        :param element_state: required element
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        element.send_keys(key)

    def get_css_property(self, locator: str, property_name: str, timeout: int = 3,
                         element_state: str = Constants.SINGLE_VISIBLE):
        """
        Get css property of element
        :param property_name: name of the property
        :param locator: locator
        :param timeout: required seconds
        :param element_state: required state
        :return: css property
        """
        element = self._find_element(locator, timeout=timeout, element_state=element_state)
        return element.value_of_css_property(property_name)

    def get_url(self):
        """
        Take current URL
        :return: URL
        """
        return self.driver.current_url

    @staticmethod
    def go(driver, url):
        """
        Open browser
        :param driver: initialized browser
        :param url: URL
        """
        driver.get(url)

    @staticmethod
    def kill(driver):
        """
        Kill browser explicitly
        :param driver: initialized browser
        """
        driver.quit()

    @staticmethod
    def close(driver):
        """
        Close the tab
        :param driver: initialized browser
        """
        driver.close()

    def _get_by_locator(self, locator: str):
        """
        Find element by locator
        :param locator: locator
        :return: element
        """
        if locator.startswith("."):
            return By.CSS_SELECTOR, locator
        elif locator.startswith("#"):
            return By.CSS_SELECTOR, locator
        elif locator.startswith("["):
            return By.CSS_SELECTOR, locator
        elif locator.startswith("/"):
            return By.XPATH, locator
        else:
            try:
                self.driver.find_element(By.ID, locator)
                return By.ID, locator
            except NoSuchElementException:
                pass

            try:
                self.driver.find_element(By.CLASS_NAME, locator)
                return By.CLASS_NAME, locator
            except NoSuchElementException:
                pass

            try:
                self.driver.find_element(By.NAME, locator)
                return By.NAME, locator
            except NoSuchElementException:
                pass

            return By.TAG_NAME, locator
