#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/13 11:53 AM
# @Author  : Zhenxuan Xu
# @File    : settings.py
# @Software: Pycharm professional

import os


class BasicConfig(object):
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APPLICATIONS_PER_PAGE = 1


class DevelopmentConfig(BasicConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(os.path.dirname(__file__), 'development.db'))


class ProductionConfig(BasicConfig):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/{}" \
        .format(os.getenv('DATABASE_USERNAME'), os.getenv('DATABASE_PASSWORD'),
                os.getenv('DATABASE_ADDRESS'), os.getenv('DATABASE_PORT'), os.getenv('DATABASE_NAME'))


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
