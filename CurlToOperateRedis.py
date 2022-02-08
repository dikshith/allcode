# !/usr/bin/env python3
"""
Author:  Dixit <dixit@gmail.com>
Purpose:
# Use package REQUESTS from PYTHON instead of PYCurl library
# getattr() in Python is used to invoke a function call.
# The lambda keyword in Python is used to define an anonymous function.
# In case the user gives an invalid input, lambda will invoke the default function.
"""
import sys  # standard library
import os  # standard library
import argparse  # to parse arguments
import operator  # to sort list of classes objects by argument
import csv  # to write csv file
from datetime import datetime  # to get current time
import requests
from requests.exceptions import HTTPError

# ----------------------Variables----------------------
app_client = "63tck1s69o67lr5mlktkfrr5pe"
app_secret = "1g4t5ark2fteso8geq6di3vc4d8dtdnvcu4e145rlh7s62sdqp5b"
header_authorization = {"authorization": "Basic YWRtaW46VTdyRnFjZ1g0SXVlOUJMT1loSjl2b3hSQTQ5bHNXZ0J3NjJOVHlMZw==",
                        "Content-Type": "application/json;", "charset": "UTF-8"}
oauth2_url = "perf4-vlocity.auth.us-west-2.amazoncognito.com"
app_diagnostic = "https://api.perf4.vlocity.dc.vloc-dev.com/dc/app-diagnostic"
app_status = "https://api.perf4.vlocity.dc.vloc-dev.com/dc/app-status"
redis_url = "https://api.perf4.vlocity.dc.vloc-dev.com/admin/cache/flush"
url = 'https://perf4-vlocity.auth.us-west-2.amazoncognito.com/oauth2/token?grant_type=client_credentials' \
      '&client_id=' + app_client + \
      '&client_secret=' + app_secret
flush_url = "https://api.perf4.vlocity.dc.vloc-dev.com/admin/cache/flush"


class RedisOps:
    def switch(self, specifyOperation):
        default = "Incorrect Operation"
        return getattr(self, 'case_' + str(specifyOperation), lambda: default)()

    # --------------------------------------------
    @staticmethod
    def case_1():
        print("inside OAUTH2 flush")
        res_access_token = requests.post(url, headers={"content-type": "application/x-www-form-urlencoded"})
        # print(response.json())
        res_access_token_json = res_access_token.json()
        access_token = res_access_token_json["access_token"]
        header_bearer = {"authorization": "Bearer " + access_token, "Content-Type": "application/json",
                         "charset": "UTF-8"}
        res_cache_flush = requests.post(redis_url, headers=header_bearer)
        res_cache_flush_json = res_cache_flush.json()
        return res_cache_flush_json

    # --------------------------------------------
    @staticmethod
    def case_2():
        print("Inside Basic flush .............")
        res_flush = requests.post(flush_url, headers=header_authorization)
        res_flush_json = res_flush.json()
        res_flush_no_of_deleted_keys = res_flush_json["message"]
        print("No Of Deleted keys are : " + res_flush_no_of_deleted_keys)
        return res_flush_json

    # --------------------------------------------
    @staticmethod
    def case_3():
        res_appdiagnostic = requests.get(app_diagnostic, headers=header_authorization)
        res_appdiagnostic_json = res_appdiagnostic.json()
        return res_appdiagnostic_json

    # --------------------------------------------
    @staticmethod
    def case_4():
        res_appstatus = requests.get(app_status, headers=header_authorization)
        res_appstatus_json = res_appstatus.json()
        return res_appstatus_json

    # --------------------------------------------
    @staticmethod
    def case_5():
        sys.exit('User decided to quit')

    # --------------------------------------------

    @staticmethod
    def main():
        print("************ Main Menu For AWS Status Checks**************")
        choice = input("""
        FLUSH USING OAUTH2 REDIS: 1
        FLUSH REDIS: 2
        App Diagnostics: 3
        App Status: 4
        Quit: 5
        Please enter your choice: """)
        return choice


# --------------------------------------------
if __name__ == '__main__':
    s = RedisOps()
    val = s.main()
    # print(val)
    print(s.switch(val))
