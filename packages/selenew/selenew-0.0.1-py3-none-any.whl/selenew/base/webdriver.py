"""
Webdriver Factory module
"""

import atexit
from functools import partial
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options
from selenium.webdriver.chrome.service import Service
from ..common.exceptions import Exceptions
from ..common.logger import Logger
from colorama import Fore
from ..common.constants import Constants

log = Logger(Constants.FRAMEWORK)


class SeleNewDriver:
    def __init__(self):
        self.driver = webdriver
        self.browser = None

    def browser_open(self, use_browser: str, headless: bool = True):
        """
        To open required browser with headless False/True mode
        :param use_browser: browser name
        :param headless: True or False
        :return: Selected browser initialization
        """
        if use_browser.lower() == Constants.CHROME:
            driver = self.__chrome(headless=headless)
        elif use_browser.lower() == Constants.FIREFOX:
            driver = self.__firefox(headless=headless)
        elif use_browser.lower() == Constants.EDGE:
            driver = self.__edge(headless=headless)
        else:
            log.logger_method(f"[{Constants.FRAMEWORK}]: {use_browser} is not supported. "
                              f"Supported browsers: "
                              f"{Constants.SUPPORTED_BROWSERS}", Fore.GREEN)
            raise Exception(Exceptions.BrowserNotFound)
        atexit.register(partial(self.__browser_terminate, use_browser))
        return driver

    def __browser_terminate(self, browser):
        """
        To terminate browser due to idle
        :param browser: browser that was initialized befoew
        :return:
        """
        log.logger_method(f"[{Constants.FRAMEWORK}]: {browser} has been terminated due to idle")
        self.browser.quit()

    def __chrome(self, headless: bool = False):
        """
        To initialize Chrome browser
        :param headless: True or False
        :return: Chrome browser initialization
        """
        try:
            options = self.driver.ChromeOptions()
            if headless:
                options.add_argument("--headless")
            options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
            options.add_argument('--start-maximized')
            self.browser = self.driver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            log.logger_method(f"[{Constants.FRAMEWORK}]: {Constants.CHROME} has been started "
                              f"in headless '{headless}' mode", Fore.GREEN)
            return self.browser
        except Exception:
            log.logger_method(f"[{Constants.FRAMEWORK}]: {Constants.CHROME} has not been "
                              f"started", Fore.RED)
            raise Exception(Exceptions.DriverNotInitialized.format(self.browser))

    def __firefox(self, headless: bool = False):
        """
        To initialize Firefox browser
        :param headless: True or False
        :return: Firefox browser initialization
        """
        try:
            options = self.driver.FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument('--start-maximized')
            self.browser = self.driver.Firefox(service=FirefoxService(GeckoDriverManager().install()),
                                               options=options)
            log.logger_method(f"[{Constants.FRAMEWORK}]: {Constants.FIREFOX} has been started "
                              f"in headless '{headless}' mode", Fore.GREEN)
            return self.browser
        except Exception:
            log.logger_method(f"[{Constants.FRAMEWORK}]: {Constants.FIREFOX} has not been "
                              f"started", Fore.RED)
            raise Exception(Exceptions.DriverNotInitialized.format(self.browser))

    def __edge(self, headless: bool = False):
        """
        To initialize Edge browser
        :param headless: True or False
        :return: Edge browser initialization
        """
        try:
            options = Options()
            if headless:
                options.add_argument('headless')
            options.add_argument('--start-maximized')
            self.browser = self.driver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
            log.logger_method(f"[{Constants.FRAMEWORK}]: {Constants.EDGE} has been started in "
                              f"headless '{headless}' mode", Fore.GREEN)
            return self.browser
        except Exception:
            log.logger_method(f"[{Constants.FRAMEWORK}]: {Constants.EDGE} has not been started",
                              Fore.RED)
            raise Exception(Exceptions.DriverNotInitialized.format(self.browser))
