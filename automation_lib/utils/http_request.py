import requests
requests.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)

from automation_lib.utils.logger import Logger

logger = Logger.log(__name__)

class HttpRequest(object):

    session = None

    def __init__(self):
        self.session = requests.session()

    def send_request_with_data(self, url, data=None, headers=None, redirects=True):
        try:
            conn = self.session.post(url, headers=headers, data=data, verify= False, allow_redirects=redirects)
        except Exception as exception:
            logger.error(exception)
            return False
        return conn

    def get_request(self, url, headers=None, params=None):
        try:
            conn = self.session.get(url, headers=headers, params=params, verify= False)
        except Exception as exception:
            logger.error(exception)
            return False
        return conn

    def delete(self, url, headers=None, params=None):
        try:
            conn = self.session.delete(url, headers=headers, params=params, verify=False)
        except Exception as exception:
            logger.error(exception)
            return False
        return conn

    def head_request(self, url, headers=None, redirects=True):
        try:
            conn = self.session.head(url, headers=headers, verify= False, allow_redirects=redirects)
        except Exception as exception:
            logger.error(exception)
            return False
        return conn

    def upload_file(self, url, filepath):
        """
        Upload file to remote fileserver
        :return:
        """
        try:
            files = {'file': open(filepath, "rb")}
            response = requests.post(url, verify=False, files=files)
        except Exception as exception:
            logger.error(exception)
            return False
        return response

    def put(self, url, data=None, json = None, params=None, headers=None):
        """

        :param url:
        :param data:
        :param headers:
        :param redirects:
        :return:
        """
        try:
            conn = self.session.put(url, headers=headers, data=data, json=json, params=params ,verify= False)
        except Exception as exception:
            logger.error(exception)
            return False
        return conn