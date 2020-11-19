from enum import Enum

from selenium import webdriver


class BrowserType(Enum):
    CHROME = "chrome"
    IE = "ie"
    FIREFOX = 'firefox'
    CHROME_REMOTE = "chrome_remote"
    OPERA = "opera"
    SAFARI = "safari"


class DriverFactory(object):
    def __init__(self, browser='ff', browser_version=None, os_name=None):
        """
        Constructor for the Driver factory
        :param browser: browser to be used
        :param browser_version: browser version
        :param os_name: os name
        :return:
        """
        self._browser = browser
        self.browser_version = browser_version
        self.os_name = os_name

    def _run_local(self, browser):
        """
        Return the local driver
        :param browser: browser name
        :return: Local Driver Instance
        """
        local_driver = None
        if browser.lower() == "ff" or browser.lower() == BrowserType.FIREFOX.value:
            local_driver = webdriver.Firefox()
        elif browser.lower() == BrowserType.IE.value:
            local_driver = webdriver.Ie()
        elif browser.lower() == BrowserType.CHROME.value:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--use-fake-device-for-media-stream")
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            # chrome_options.add_argument("--disable-popup-blocking")
            #

            # path = os.path.dirname(swagger_generic.__file__)
            # local_driver = webdriver.Chrome(path + "\\exes\\chromedriver.exe", chrome_options=chrome_options)
            local_driver = webdriver.Chrome("c:\\chromedriver.exe", chrome_options=chrome_options)
        elif browser.lower() == BrowserType.OPERA.value:
            local_driver = webdriver.Opera()
        elif browser.lower() == BrowserType.SAFARI.value:
            local_driver = webdriver.Safari()
        local_driver.maximize_window()
        return local_driver

    def get_web_driver(self, remote_flag=False, remote_url=None, desired_caps=None):
        """
        Return the appropriate driver
        :Param remote_flag: flag to decide tu run local or remote
        :Param remote_url: remote_url
        :Param desired_caps: desired capabilities of remote driver
        :return:
        """
        if remote_flag:
            return self._run_remote(remote_url, desired_caps)
        else:
            return self._run_local(self._browser)

    def _run_remote(self, remote_url, desired_caps):
        """
        Set the remote driver with supplied desired capabilities
        :return: remote webdriver
        """
        remote_driver = webdriver.Remote(remote_url, desired_caps)
        return remote_driver

        # def get_firefox_driver(self):
        #     "Return the Firefox driver"
        #     driver = webdriver.Firefox(firefox_profile=self.get_firefox_profile())
        #     return driver


        # def get_firefox_profile(self):
        #     "Return a firefox profile"
        #
        #     return self.set_firefox_profile()


        # def set_firefox_profile(self):
        #     "Setup firefox with the right preferences and return a profile"
        #     try:
        #         self.download_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','downloads'))
        #         if not os.path.exists(self.download_dir):
        #             os.makedirs(self.download_dir)
        #     except Exception as e:
        #         self.write("Exception when trying to set directory structure")
        #         self.write(str(e))
        #
        #     profile = webdriver.firefox.firefox_profile.FirefoxProfile()
        #     set_pref = profile.set_preference
        #     set_pref('browser.download.folderList', 2)
        #     set_pref('browser.download.dir', self.download_dir)
        #     set_pref('browser.download.useDownloadDir', True)
        #     set_pref('browser.helperApps.alwaysAsk.force', False)
        #     set_pref('browser.helperApps.neverAsk.openFile', 'text/csv,application/octet-stream,application/pdf')
        #     set_pref('browser.helperApps.neverAsk.saveToDisk', 'text/csv,application/vnd.ms-excel,application/pdf,application/csv,application/octet-stream')
        #     set_pref('plugin.disable_full_page_plugin_for_types', 'application/pdf')
        #     set_pref('pdfjs.disabled',True)
        #
        #     return profile
