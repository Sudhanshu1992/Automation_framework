"""
Base class for automating web pages using Selenium WebDriver
This is the base class that all the classes representing various pages
of application inherit from. This class contains all selenium actions.
"""
from abc import ABC, abstractmethod
from enum import Enum
from time import sleep
from retry import retry
# from pilkit.lib import Image
# from pilkit.lib import Image
from PIL import Image

from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from .driverfactory import DriverFactory
from selenium.webdriver.remote.webelement import WebElement


class NotClickableException(Exception):
    """Custom exception when object is not clickable"""
    pass


class PageBase(ABC):
    """
    Base Class for web related operations using Selenium WebDriver
    """

    def __init__(self, browser_type, driver=None, remote_flag=None,
                 remote_url=None, desired_caps=None):
        """
        Provides webdriver instance to the classes inheriting it
        :param browser_type: browser, e.g. IE, Firefox, Chrome
        :param driver: WebDriver object
        """
        self._driver = driver
        if self._driver is None:
            self._driver = DriverFactory(browser=browser_type).get_web_driver(remote_flag, remote_url, desired_caps=desired_caps)

        self.start()

    @abstractmethod
    def start(self):
        """
        Overwrite this method in your Page module
        if you want to visit a specific URL
        :return:
        """

    def open(self, url, wait_time=2):
        """
        Visit the page base_url + url
        :param url: URL to be opened
        :param wait_time: time to wait till url opens
        :return:
        """
        # url = self.base_url + url
        if self._driver.current_url != url:
            self._driver.get(url)
        self.sleep_in_seconds(wait_time)

    def get_current_driver(self):
        """
        Return current driver
        :return: current driver instance
        """
        return self._driver

    def set_implicit_timeout(self, timeout=10):
        """
        Return current driver
        :return: current driver instance
        """
        return self._driver.implicitly_wait(time_to_wait=timeout)

    def get_current_title(self):
        """
        Get the current title of the opened browser
        :return: current browser title
        """
        return self._driver.title

    def get_current_url(self):
        """
        Get the current URL
        :return: Return current URL
        """
        return self._driver.current_url

    def is_element_selected(self, locator):
        """
        Check whether provided element is selected
        :param locator: Element locator strategy
        :return: True or False about the element selection
        """
        element = self.find_element(locator)
        return element.is_selected()

    def is_element_enabled(self, locator):
        """
        Returns whether given element is enabled or not
        :param locator: Element locator strategy
        :return: True if given element is enabled else returns false
        """
        element = self.find_element(locator)
        return element.is_enabled()

    @retry((StaleElementReferenceException, ElementNotVisibleException, NotClickableException), tries=5, delay=2)
    def click(self, locator):
        """
        Clicks the given element
        :param locator: Element locator strategy
        :return: element
        """
        error_msg = "is not clickable"
        element = None
        if isinstance(locator, str):
            element = self.find_element(locator)
        elif isinstance(locator, WebElement):
            element = locator

        if element is not None:
            try:
                element.click()
            except Exception as e:
                if error_msg in e.__str__():
                    raise NotClickableException
                else:
                    raise e
        else:
            raise Exception("Could not click on the element with locator {}".
                            format(locator))

    def javascript_click(self, locator):
        element = None
        if isinstance(locator, str):
            element = self.find_element(locator)
        elif isinstance(locator, WebElement):
            element = locator

        if element is not None:
            self._driver.execute_script("arguments[0].click();", element)
        else:
            raise Exception("Could not click on locator " + locator)

    @retry(StaleElementReferenceException, tries=5, delay=2)
    def set_field(self, locator, element_value):
        """
        Locates the element by specified locator and then sets its value
        :param locator: Element locator strategy
        :param element_value: value to be written
        :return: element
        """
        webelement = self.find_element(locator)
        try:
            webelement.send_keys(Keys.CONTROL, 'a')
            webelement.clear()
            sleep(1)
            webelement.click()
            webelement.send_keys(element_value)
        except Exception as e:
            raise Exception("Could not write on the the element {} due to {}".
                            format(webelement, e))

        return webelement

    def get_text(self, locator):
        """
        get  the inner text of given element
        :param locator: Element locator strategy
        :return: text
        """
        try:
            element = self.find_element(locator)
        except Exception as e:
            raise Exception("Could not get the text of the the element with locator {} due to {}".
                            format(locator, e))
        return element.text

    def get_element_text(self, element):
        """
        get  the inner text of given element
        :param locator: Element locator strategy
        :return: text
        """
        # element = self.find_element(locator)
        return element.text

    def is_element_displayed(self, locator):
        """
        Returns whether given element is displayed or no
        :param locator: Element locator strategy
        :return: True if given element is displayed else returns false
        """
        try:
            element = self.find_element(locator)
        except:
            return False
        return element.is_displayed()

    def switch_to_frame(self, frame_id):
        """
        Switch to the given frame based on id
        :param frame_id: id of the frame (can be xpath also)
        :return:
        """
        self._driver.switch_to_frame(frame_id)

    def switch_to_main_window(self):
        """
        Switch to the main browser window
        :return:
        """
        self._driver.switch_to_default_content()

    def move_and_click(self, locator):
        """
        Move and click to the given element using
        selenium action class
        :param locator: Element locator strategy
        :return: element
        """
        element = self.find_element(locator)
        try:
            action = ActionChains(self._driver)
            action.move_to_element(element).click().perform()
        except Exception as e:
            raise Exception("Could Not click locator {} due to {}".format(element, e))
        return element

    def click_and_move_by_offset(self, locator, offset):
        element = self.find_element(locator)
        drawing = ActionChains(self._driver) \
            .move_to_element(element) \
            .click_and_hold(element) \
            .move_by_offset(*offset) \
            .release()
        drawing.perform()

    def find_element(self, locator, timeout=5):
        """
        Find and return element based on the given locator value
        E.g: draggableElement = ("xpath@@//div[@id='draggable']")
        :param locator: Element locator strategy
        :return: Element
        """
        try:
            return WebDriverWait(self._driver, timeout=timeout) \
                .until(EC.presence_of_element_located(self.__get_by(locator_with_strategy=locator)),message = "Timed out after {} seconds while waiting to find the element with locator {} ".format(timeout,locator))
        except Exception as e:
            raise Exception("Could Not Find Element with locator {} due to error {} ".format(locator,str(e)))

    @retry(StaleElementReferenceException, tries=5, delay=2)
    def find_child_element(self, element, locator, timeout=5):
        by = self.__get_by(locator_with_strategy=locator)
        return WebDriverWait(element, timeout).until(EC.presence_of_element_located(by))

    def find_child_elements(self, element, locator):
        by = self.__get_by(locator_with_strategy=locator)
        return element.find_elements(*by)

    def is_child_element_present(self, element, locator, timeout=5):
        try:
            self.find_child_element(element, locator, timeout)
        except:
            return False
        return True

    def __get_by(self, locator_with_strategy):
        """
        Get and return By instance based on the locator strategy
        :param locator_with_strategy: Element locator strategy
        :return: By instance of the element
        """

        if "@@" not in locator_with_strategy:
            locator_with_strategy = Strategy.ID.value + "@@" + locator_with_strategy

        strategy_and_locator = str(locator_with_strategy).split("@@")
        strategy = strategy_and_locator[0]
        locator = strategy_and_locator[1]
        by = None
        if strategy == Strategy.XPATH.value:
            by = (By.XPATH, locator)
        elif strategy == Strategy.ID.value:
            by = (By.ID, locator)
        elif strategy == Strategy.CSS.value:
            by = (By.CSS_SELECTOR, locator)
        elif strategy == Strategy.TAGNAME.value:
            by = (By.TAG_NAME, locator)
        else:
            raise Exception(" Incorrect locator specified . Locator has to be either xpath,id,css,tagname -->" + locator_with_strategy)
        return by

    def find_elements(self, locator):
        """
        Find and return the list of webelements based on the given locator value
        :param locator: Element locator strategy
        :return: list of the elements
        """
        try:
            return self._driver.find_elements(*self.__get_by(locator_with_strategy=locator))
        except Exception as e:
            raise Exception("Could Not Find Elements with locator {} due to error {}".format(locator,str(e)))

    def find_visible_elements(self, locator):
        """
        Find and return the list of webelements based on the given locator value
        :param locator: Element locator strategy
        :return: list of visible elements
        """
        elements = self._driver.find_elements(*self.__get_by(locator_with_strategy=locator))
        return [element for element in elements if element.is_displayed()]


    @retry(StaleElementReferenceException, tries=5, delay=2)
    def get_attribute(self, locator, attribute):
        """
        Get the provided attribute value for the given element
        :param locator: Element locator strategy
        :param attribute: attribute
        :return: value of the attribute
        """
        if isinstance(locator, WebElement):
            return locator.get_attribute(attribute)
        else:
            element = self.find_element(locator)
            return element.get_attribute(attribute)

    def drag_and_drop(self, draggable, droppable):
        """
        Performs drag and drop action using selenium action class
        :param draggable: draggable element
        :param droppable: droppable element
        :return:
        """
        if not isinstance(draggable, WebElement):
            draggable = self.find_element(draggable)

        if not isinstance(droppable, WebElement):
            droppable = self.find_element(droppable)
        try:
            action = ActionChains(self._driver)
            action.click_and_hold(draggable).move_to_element(droppable).perform()
            action.release(droppable).perform()
        except Exception as e:
            raise e

    def sleep_in_seconds(self, seconds=1):
        """
        Method for hard wait as per given seconds
        :param seconds: time in seconds
        :return:
        """
        sleep(seconds)

    def select_value_from_dropdown(self, locator, value):
        """
        It will select value from dropdown based on visible text
        :param locator: dropdwon Element locator strategy
        :return:
        """
        element = self.find_element(locator)
        select = Select(element)
        sleep(3)
        select.select_by_visible_text(value)

    def select_value_from_dropdown_by_index(self, locator, index):
        """
        It will select first value from dropdown
        :param locator: dropdwon Element locator strategy
        :param index: index of the dropdown element
        :return:
        """
        element = self.find_element(locator)
        select = Select(element)
        sleep(3)
        select.select_by_index(index)
        sleep(3)

    def select_value_from_value(self, locator, value):
        """
        It will select value from dropdown based on value attribute
        :param locator: dropdwon Element locator strategy
        :param value: value of dropdown element
        :return:
        """
        element = self.find_element(locator)
        select = Select(element)
        sleep(3)
        select.select_by_value(value)

    def explicit_wait(self, locator, timeout=10):
        """
        Smart Wait in Selenium, wait till element is clickable
        :param locator: Element locator strategy
        :return: Found Element
        """
        try:
            element = WebDriverWait(self._driver, timeout=timeout,
                                    ignored_exceptions=[NoSuchElementException,
                                                     ElementNotVisibleException,
                                                     ElementNotSelectableException]).\
                until(EC.element_to_be_clickable(self.__get_by(locator)))
        except Exception as e:
            raise e
        return element

    def explicit_wait_till_alert_is_present(self,timeout=10):
        """
        Smart Wait in Selenium, wait till alert is present
        :param locator: Element locator strategy
        :return: Found Element
        """
        try:
            element = WebDriverWait(self._driver, timeout).until(EC.alert_is_present())
        except Exception as e:
            raise e
        return element

    def select_dropdown_option(self, locator, option_text):
        """
        Selects the option in the drop-down based on the tag text
        :param locator: element
        :param option_text: value to be selected
        :return:
        """
        dropdown = self.find_element(locator)
        for option in dropdown.find_elements_by_tag_name('option'):
            if option.text == option_text:
                option.click()
                break

    def hit_enter(self, locator, wait_time=2):
        """
        Hit Enter
        :param locator: element
        :param wait_time: time to wait
        :return:
        """
        element = self.find_element(locator)
        try:
            element.send_keys(Keys.ENTER)
            self.sleep_in_seconds(wait_time)
        except Exception as e:
            raise e

    def send_keys(self, locator, *keys):
        """
        send keys to locator
        :param locator: element
        :param wait_time: time to wait
        :return:
        """
        element = self.find_element(locator)
        try:
            element.send_keys(*(keys))
        except Exception as e:
            raise e

    def scroll_down(self, locator, wait_time=2):
        """
        Scroll down WebPage
        :param locator: locator
        :param wait_time: time to wait
        :return:
        """
        element = self.find_element(locator)
        try:
            element.send_keys(Keys.PAGE_DOWN)
            self.sleep_in_seconds(wait_time)
        except Exception as e:
            raise e

    def hover(self, locator, wait_seconds=2):
        """
        Hover over the element
        :param locator: locator
        :param wait_seconds: time to wait
        :return:
        """
        element = self.find_element(locator)
        action_obj = ActionChains(self._driver)
        action_obj.move_to_element(element)
        action_obj.perform()
        self.sleep_in_seconds(wait_seconds)

    def read_browser_console_log(self, log_type='browser'):
        """
        Read Browser Console log
        :param log_type: driver.get_log('browser')
            driver.get_log('driver')
            driver.get_log('client')
            driver.get_log('server')
        :return: logs
        """
        return self._driver.get_log(log_type)

    def execute_javascript(self, js_script):
        """
        Execute javascipt
        :param js_script:
        :return:
        """
        try:
            self._driver.execute_script(js_script)
        except Exception as e:
            raise e

    def accept_alert(self):
        """
        Accepts Java Alert
        :return:
        """
        try:
            self._driver.switch_to_alert().accept()
        except NoAlertPresentException:
            raise NoAlertPresentException

    def dismiss_alert(self):
        """
        Dismiss Java Alert
        :return:
        """
        try:
            self._driver.switch_to_alert().dismiss()
        except NoAlertPresentException:
            raise NoAlertPresentException

    def wait_till_element_is_present(self, locator, timeout=10):
        """
        WebDriver Explicit wait till element is present
        :param locator: element to be checked
        :param timeout: timeout
        :return:
        """
        try:
            element = WebDriverWait(driver=self._driver, timeout=timeout).\
                until(EC.presence_of_element_located(self.__get_by(locator)))
            return element
        except Exception as e:
            raise e

    def wait_till_element_is_not_visible(self, locator, timeout=10):
        """
        WebDriver Explicit wait till element is visible, once disappeared wait will over
        :param locator: element to be checked
        :param timeout: timeout
        :return:
        """
        try:
            element = WebDriverWait(driver=self._driver, timeout=timeout,
                                    ignored_exceptions=[NoSuchElementException,
                                                         ElementNotVisibleException,
                                                            ElementNotSelectableException]). \
                until_not(EC.visibility_of_element_located(self.__get_by(locator)))
            return element
        except Exception as e:
            raise e

    def wait_till_element_is_visible(self, locator, timeout=10):
        """
        wait while element to be visible
        :param locator: element to be checked
        :param timeout: timeout
        :return:
        """
        try:
            element = WebDriverWait(driver=self._driver, timeout=timeout,
                                    ignored_exceptions=[NoSuchElementException,
                                                         ElementNotVisibleException,
                                                            ElementNotSelectableException, StaleElementReferenceException,]). \
                until(EC.visibility_of_element_located(self.__get_by(locator)))
            return element
        except Exception as e:
            raise e

    def wait_till_webdriver_element_to_be_visible(self, element, timeout=10):
        """
        wait while webdriver element to be visible
        :param element: WebDriver element
        :param timeout: timeout
        :return:
        """
        try:
            element = WebDriverWait(driver=self._driver, timeout=timeout,
                                    ignored_exceptions=[NoSuchElementException,
                                                         ElementNotVisibleException,
                                                            ElementNotSelectableException]). \
                until(EC.visibility_of(element=element))
            return element
        except Exception as e:
            raise e

    def wait_till_text_is_present_in_element(self, locator, text, timeout=10):
        """
        wait while element to be visible
        :param locator: element to be checked
        :param timeout: timeout
        :return:
        """
        try:
            element = WebDriverWait(driver=self._driver, timeout=timeout,
                                    ignored_exceptions=[NoSuchElementException,
                                                         ElementNotVisibleException,
                                                            ElementNotSelectableException]). \
                until(EC.text_to_be_present_in_element(self.__get_by(locator), text))
            return element
        except Exception as e:
            raise e

    def wait_till_text_is_present_in_element_value(self, locator, text, timeout=10):
        """
        wait while element to be visible
        :param locator: element to be checked
        :param timeout: timeout
        :return:
        """
        try:
            element = WebDriverWait(driver=self._driver, timeout=timeout,
                                    ignored_exceptions=[NoSuchElementException,
                                                         ElementNotVisibleException,
                                                            ElementNotSelectableException]). \
                until(EC.text_to_be_present_in_element_value(self.__get_by(locator), text))
            return element
        except Exception as e:
            raise e

    def wait_till_element_is_invisible(self, locator, timeout=10):
        """
        WebDriver Explicit wait till element is invisible
        :param locator: element to be checked
        :param timeout: timeout
        :return:
        """
        try:
            element = WebDriverWait(driver=self._driver, timeout=timeout,
                                    ignored_exceptions=[NoSuchElementException,
                                                         ElementNotVisibleException,
                                                            ElementNotSelectableException]). \
                until(EC.invisibility_of_element_located(self.__get_by(locator)))
            return element
        except Exception as e:
            raise e

    def wait_until_visible_and_click(self, locator):
        """
        conditional method for click until element its visible
        :param locator:
        :return:
        """
        self.wait_till_element_is_visible(locator)
        self.click(locator)

    def teardown_browser(self):
        """
        Close all browser instances
        :return:
        """
        self._driver.quit()

    def close_browser(self):
        """
        Close current browser instance
        :return:
        """
        self._driver.close()

    def disconnect_browser(self):
        """
        Disconnect browser
        :return:
        """
        # network_conditions = self.get_network_conditions()
        # self._driver.set_network_conditions(offline=True, latency=network_conditions["latency"],
        #                                     download_throughput=network_conditions["download_throughput"],
        #                                     upload_throughput=network_conditions["upload_throughput"])
        self._driver.set_network_conditions(
            offline=True,
            latency=1,  # additional latency (ms)
            download_throughput=500 * 1024,  # maximal throughput
            upload_throughput=500 * 1024)  # maximal throughput

    def connect_browser(self):
        """
        Connect browser
        :return:
        """
        # network_conditions = self.get_network_conditions()
        # self._driver.set_network_conditions(offline=False, latency=network_conditions["latency"],
        #                                     download_throughput=network_conditions["download_throughput"],
        #                                     upload_throughput=network_conditions["upload_throughput"])
        self._driver.set_network_conditions(
            offline=False,
            latency=1,  # additional latency (ms)
            download_throughput=500 * 1024,  # maximal throughput
            upload_throughput=500 * 1024)  # maximal throughput

    def get_network_conditions(self):
        """
        Gets Chrome network emulation settings
        :return: A dict. For example:
                {'latency': 4, 'download_throughput': 2, 'upload_throughput': 2,
                'offline': False}
        """
        return self._driver.get_network_conditions()

    def print_version(self):
        """
        Prints version
        :return:
        """
        print("print_version = 2.0")

    def maximize_browser(self):
        """
        Maximize the browser
        :return:
        """
        self._driver.maximize_window()

    def bring_to_front(self):
        """
        Brings the browser to front
        :return:
        """
        self._driver.switch_to_window(self._driver.window_handles[-1])

    def back(self):
        """
        browser back button
        :return:
        """
        self._driver.back()

    def is_element_present(self, locator, timeout=2):
        """
        Check the presence of element.
        :return: Boolean
        """
        try:
            WebDriverWait(self._driver, timeout=timeout) \
                .until(EC.presence_of_element_located(self.__get_by(locator)))
        except TimeoutException:
            return False
        except Exception as e:
            raise Exception("Could Not Verify Element Presence {} due to error {}".format(locator, str(e)))
        return True

    def get_css_value(self, locator, css_property):
        """"
        This method will get the CSS property of the element
        :return: CSS property Value

        Usage
        get_css_value(locator,"color")
        get_css_value(locator,"font-family")
        get_css_value(locator,"font-size")
        The above code will return value in RGB format such as “rgba(36, 93, 193, 1)”
        """
        element = self.find_element(locator)
        return element.value_of_css_property(css_property)

    def get_current_window_handle(self):
        """
        Returns the handle of the current window.
        :return: string containing current window handle
        """
        return self._driver.current_window_handle

    def get_window_handles(self):
        """
        Returns the list containing handles of all windows within the current session.
        :return: list containing all opened window handles in current session
        """
        return self._driver.window_handles

    def switch_to_new_window(self, win_handle):
        """
        Switch to window corresponding to windows handle id
        :return:
        """
        self._driver.switch_to_window(win_handle)

    def refresh_browser(self):
        """
        Refreshes the page
        :return:
        """
        self._driver.refresh()

    def get_element_screen_shot(self, locator, filename, offset_left=0, offset_right=0, offset_top=0, offset_bottom=0):
        element = self.find_element(locator)
        location = element.location
        size = element.size
        self.get_full_page_screen_shot(filename)
        im = Image.open(filename)  # uses PIL library to open image in memory

        left = location['x'] + offset_left
        top = location['y'] + offset_top
        right = location['x'] + size['width'] - offset_right
        bottom = location['y'] + size['height'] - offset_bottom

        im = im.crop((left, top, right, bottom))  # defines crop points
        im.save(filename)  # saves new cropped image

    def get_full_page_screen_shot(self, filename):
        self._driver.save_screenshot(filename)

    def get_page_cookies(self):
        return self._driver.get_cookies()

    def get_page_useragent(self):
        return self._driver.execute_script("return navigator.userAgent")

    def upload_file(self, locator, filename):
        """
        Upload file on the browser
        Condition: The element should be <input> and type='file'
        :param locator: Element locator strategy
        :param filename: Absolute file path with file extension
        :return:
        """
        element = self.find_element(locator)
        element.send_keys(filename)

    def set_browser_window_size(self, width=800, height=600):
        """
        Set window size
        :param width:
        :param height:
        :return:
        """
        self._driver.set_window_size(width=width, height=height)

class Strategy(Enum):
    """
    Locator Strategy Constants
    """
    XPATH = "xpath"
    ID = "id"
    CSS = "css"
    TAGNAME = "tag name"
