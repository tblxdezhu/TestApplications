#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/27 4:11 PM
# @Author  : Zhenxuan Xu
# @File    : default_settings.py
# @Software: Pycharm professional


class DefaultConfig(object):
    SERVER_ADDRESS = "10.69.140.184"
    DATABASE_USERNAME = "root"
    DATABASE_PASSWORD = "test1234"
    DATABASE_ADDRESS = "10.69.140.184"
    DATABASE_PORT = "3306"
    RESTFUL_API_URL = "https://stash.ygomi.com:7990/rest/api/1.0/users"
    MAIL_SERVER = "mail-chengdu.ygomi.net"
    MAIL_PORT = "25"
    MAIL_USE_TLS = True
    FLASK_ENV = "production"
    FLASK_RUN_HOST = "0.0.0.0"
    FLASK_RUN_PORT = 9999
    DATABASE_NAME = "test_application"
    SECRET_KEY = "123456789"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APPLICATIONS_PER_PAGE = 3
