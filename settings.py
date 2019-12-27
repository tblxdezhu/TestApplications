#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/13 11:53 AM
# @Author  : Zhenxuan Xu
# @File    : settings.py
# @Software: Pycharm professional

import os
from default_settings import DefaultConfig


class DevelopmentConfig(DefaultConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(os.path.dirname(__file__), 'development.db'))


class ProductionConfig(DefaultConfig):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/{}".format(
        DefaultConfig.DATABASE_USERNAME,
        DefaultConfig.DATABASE_PASSWORD,
        DefaultConfig.DATABASE_ADDRESS,
        DefaultConfig.DATABASE_PORT,
        DefaultConfig.DATABASE_NAME)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
