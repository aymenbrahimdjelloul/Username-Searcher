#!usr/bin/env python3
"""
@author : Aymen Brahim Djelloul.
project date : 02.10.2022

"""

# imports
import sys
import json
import requests
import re
from requests.exceptions import SSLError, ReadTimeout, ConnectionError, TooManyRedirects
from threading import Thread
from urllib import request
from urllib.error import URLError


def check_if_connect():
    """ this function will check if the user is connected to the internet"""
    try:
        request.urlopen('https://www.google.com', timeout=3)
        return True
    except URLError:
        return False


def _load_json_data():
    """ this function load data from json data file"""
    with open("./logic/SearchData.json", 'rb') as f:
        return json.load(f)


class NewSearch:

    """
    this is the main class to create a new search object

    """
    _results_dict = {}
    __search_data = _load_json_data()
    process_killed = False

    def __init__(self, username: str):
        self.username = username


    def __get_url_format(self, url_to_format):
        """ this method will return the url with the username ready to search"""
        return url_to_format.replace('{}', self.username)

    @staticmethod
    def __check_is_url_valid(url_to_check,
                             error_type,
                             error_msg,
                             request_method):

        """ this method make a http request and check if url is valid or not"""

        # get response first
        try:
            r = requests.request(url=url_to_check, method=request_method, timeout=10)
            response_code = r.status_code

        # handle errors
        except (SSLError, ReadTimeout,
                ConnectionError, TooManyRedirects):
            return


        # verify http request with status code
        if response_code == 200 or response_code == 405 or response_code == 500 or response_code == 403:
            if error_type == 'message':
                if re.search(error_msg, r.text):
                    return False
                else:
                    return True

            return True


    def __search__(self):
        """ this is the master method will run the whole thing"""

        # clear search results from the previous search
        self._results_dict.clear()

        for website in self.__search_data.keys():

            print(website)

            # url_name = str(website)
            url = self.__search_data[website]['url']
            error_type = self.__search_data[website]['errorType']
            error_msg = None

            # check if the process was killed
            if self.process_killed:
                break

            try:
                request_method = self.__search_data[website]['request_method']
            except KeyError:
                request_method = "GET"

            if error_type == 'message':
                error_msg = self.__search_data[website]['errorMsg']

            # first get url format with username
            url_to_check = self.__get_url_format(url)
            # print(url_to_check, '\n', )
            # check if the url is valid
            try:
                if self.__check_is_url_valid(url_to_check, error_type, error_msg, request_method):
                    self._results_dict.update({website: url_to_check})

            except TimeoutError:
                continue

        return self._results_dict


if __name__ == "__main__":
    sys.exit()
