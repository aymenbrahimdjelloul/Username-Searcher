#!usr/bin/env python3

"""
This code or file is pertinent to the 'BatterySense' Project
Copyright (c) 2022, Aymen Brahim Djelloul'. All rights reserved.
Use of this source code is governed by a MIT license that can be
found in the LICENSE file.


@author : Aymen Brahim Djelloul.
date : 16.09.2023
version : 1.1
LICENSE : MIT

    // This is the main module to search through all social media in 'Username Searcher' App

"""

# IMPORTS
import sys
import json
import requests
import re
import os
from requests.exceptions import SSLError, ReadTimeout, ConnectionError, TooManyRedirects


def is_connected():
    """ This function will check if we are online"""
    try:
        requests.get(url="https://8.8.8.8")
        return True

    except ConnectionError:
        return False


class Searcher:

    __results_dict = {}
    __search_data = json.load(open(f"{os.getcwd()}\\logic\\search_data.json", "r"))
    process_killed = False

    def __init__(self, username: str):
        self.username = username

    @staticmethod
    def __get_url_format(url: str, username: str) -> str:
        """ this method will return the url with the username ready to search"""
        return url.replace('{}', username)

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

    def new_search(self):
        """ this is the master method will run the whole thing"""

        # clear search results from the previous search
        self.__results_dict.clear()

        for website in self.__search_data.keys():

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
            url_to_check = self.__get_url_format(url, self.username)

            # check if the url is valid
            try:
                if self.__check_is_url_valid(url_to_check, error_type, error_msg, request_method):
                    self.__results_dict.update({website: url_to_check})

            except TimeoutError:
                continue

        return self.__results_dict


if __name__ == "__main__":
    sys.exit()
