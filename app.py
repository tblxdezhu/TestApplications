from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
import requests
from requests.auth import HTTPBasicAuth
import pymysql
import click
from datetime import datetime
from settings import config
import os

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    applications = db.relationship('Application')


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(300), index=True)
    description = db.Column(db.Text)
    jira_ticket = db.Column(db.String(100), index=True)
    create_time = db.Column(db.DateTime, default=datetime.now, index=True)
    expected_time = db.Column(db.DateTime)
    test_data = db.Column(db.String(100), default="default")
    branches = db.Column(db.String(300))
    configs = db.Column(db.String(100), default="default")
    compare_branches = db.Column(db.String(100), default="master")
    if_report = db.Column(db.Boolean)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if auth_(form).status_code == 200:
            username = form.username.data
            curr_user = User.query.filter_by(username=username).first()
            if curr_user is None:
                curr_user = User(username=username)
                db.session.add(curr_user)
                db.session.commit()
            login_user(user=curr_user, remember=form.remember.data)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", category='info')
    return redirect(url_for('login'))


def auth_(form):
    url = "https://stash.ygomi.com:7990/rest/api/1.0/users"
    return requests.get(url=url, auth=HTTPBasicAuth(str(form.username.data), str(form.password.data)))


@app.cli.command()
def initdb():
    db.drop_all()
    db.create_all()
    click.echo("Initialized database.")


if __name__ == '__main__':
    app.run()
