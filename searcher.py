#!/usr/bin/env python3

"""
This code or file is pertinent to the 'Username Searcher' Project
Copyright (c) 2022, Aymen Brahim Djelloul'. All rights reserved.
Use of this source code is governed by a MIT license that can be
found in the LICENSE file.


@author : Aymen Brahim Djelloul.
date : 16.09.2023
version : 1.2
LICENSE : MIT

    // This is the main module to search through all social media in 'Username Searcher' App

"""

# IMPORTS
import sys
import re
import os
import time
import json
import requests
import socket
import concurrent.futures
from requests.exceptions import SSLError, ReadTimeout, ConnectionError, TooManyRedirects, RequestException


def is_connected(timeout: int = 3) -> bool:
    """
    Check if the system has an active internet connection using socket.

    Tries to establish a socket connection to known public DNS servers.
    Faster than HTTP requests and sufficient for connectivity checks.

    Args:
        timeout (int): Connection timeout in seconds (default: 3).

    Returns:
        bool: True if connected to the internet, False otherwise.
    """
    test_hosts = [("8.8.8.8", 53), ("1.1.1.1", 53)]  # DNS servers (UDP port 53)

    for host, port in test_hosts:
        try:
            with socket.create_connection((host, port), timeout):
                return True
        except (OSError, socket.timeout):
            continue

    return False

class Searcher:
    """
    A class responsible for performing username or data searches across multiple platforms.

    This class manages search operations, stores results, and provides mechanisms to
    track the search state, including handling interruptions.

    Class Attributes:
        __results_dict (dict): A dictionary to store search results, typically mapping platform names to results.
        process_killed (bool): Flag indicating if the search process was forcibly stopped or interrupted.

    """

    __results_dict: dict = {}
    process_killed: bool = False

    def __init__(self, username: str, timeout=10, max_workers=10) -> None:
        self.username = username
        self.timeout = timeout
        self.max_workers = max_workers
        self.__load_search_data()

    def __load_search_data(self):
        """Load search data from JSON configuration file"""
        try:
            config_path = f"{os.getcwd()}\\resources\\search_data.json"
            self.__search_data = json.load(open(config_path, "r"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading search data: {e}")
            sys.exit(1)

    @staticmethod
    def __get_url_format(url: str, username: str) -> str:
        """ this method will return the url with the username ready to search"""
        return url.replace('{}', username)

    def __check_is_url_valid(self, url_to_check, error_type, error_msg, request_method, headers=None) -> bool:
        """ this method make a http request and check if url is valid or not"""

        # Prepare headers if needed
        if headers is None:
            headers = {}

        # Track response time (useful for debugging)
        start_time = time.time()

        # get response first
        try:
            r = requests.request(
                url=url_to_check,
                method=request_method,
                timeout=self.timeout,
                headers=headers
            )
            response_code = r.status_code
            response_time = time.time() - start_time

        # handle errors
        except (SSLError, ReadTimeout, ConnectionError, TooManyRedirects, RequestException):
            return None

        # verify http request with status code
        if response_code == 200 or response_code == 405 or response_code == 304:
            # These status codes usually indicate a valid profile
            if error_type == 'message':
                if re.search(error_msg, r.text):
                    return False
                else:
                    return True
            return True
        elif response_code == 404 or response_code == 410:
            # These typically indicate a non-existent profile
            return False
        elif response_code == 403 or response_code == 429:
            # Rate limiting or access forbidden - we consider the profile might exist
            if error_type == 'message':
                if re.search(error_msg, r.text):
                    return False
                else:
                    return True
            return None  # Maybe flag this as "unknown" rather than a definite match
        elif response_code == 301 or response_code == 302:
            # Handle redirects
            return None
        else:
            # Handle other status codes
            return None

    def __check_single_site(self, website):
        """Check a single website for the username"""
        url = self.__search_data[website]['url']
        error_type = self.__search_data[website]['errorType']
        error_msg = None

        try:
            # Get request method, default to GET if not specified
            request_method = self.__search_data[website].get('request_method', 'GET')

            # Get custom headers if specified
            headers = self.__search_data[website].get('headers', {})

            if error_type == 'message':
                error_msg = self.__search_data[website]['errorMsg']

            # first get url format with username
            url_to_check = self.__get_url_format(url, self.username)

            # check if the url is valid
            result = self.__check_is_url_valid(url_to_check, error_type, error_msg, request_method, headers)

            if result is True:
                return website, url_to_check

        except Exception:
            # Skip any errors for this site
            pass

        return None

    def new_search(self) -> dict:
        """ this is the master method will run the whole thing"""

        # First check if we're online
        if not is_connected():
            print("Error: No internet connection detected")
            return {}

        # clear search results from the previous search
        self.__results_dict.clear()

        # Use ThreadPoolExecutor for concurrent searches
        sites = list(self.__search_data.keys())

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_site = {executor.submit(self.__check_single_site, site): site for site in sites}

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_site):
                # Check if the process was killed
                if self.process_killed:
                    break

                result = future.result()
                if result:
                    website, url = result
                    self.__results_dict.update({website: url})

        return self.__results_dict

    def get_stats(self) -> dict:
        """Return statistics about the search"""
        return {
            "username": self.username,
            "total_sites_searched": len(self.__search_data),
            "profiles_found": len(self.__results_dict),
            "search_time": None  # Could be populated if we track search time
        }


# Add a simple CLI interface if run directly
if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
        print(f"Searching for username: {username}")

        searcher = Searcher(username)
        results = searcher.new_search()

        if results:
            print(f"\nFound {len(results)} profiles:")
            for site, url in results.items():
                print(f"- {site}: {url}")
        else:
            print("No profiles found.")
    else:
        print("Usage: python username_searcher.py <username>")
        sys.exit(1)
