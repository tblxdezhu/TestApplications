#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/27 10:28 AM
# @Author  : Zhenxuan Xu
# @File    : __init__.py
# @Software: Pycharm professional

import os
from flask import Flask
from .settings import config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)
db = SQLAlchemy(app)
mail = Mail(app)
