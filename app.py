from flask import Flask, render_template, request, url_for, redirect, flash, make_response, jsonify
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, TextAreaField
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
from faker import Faker

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    role = db.Column(db.String(20))
    team = db.Column(db.String(20))
    applications = db.relationship('Application')


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('user.username'), index=True)
    description = db.Column(db.Text)
    jira_ticket = db.Column(db.String(100), index=True)
    create_time = db.Column(db.DateTime, index=True)
    expected_time = db.Column(db.DateTime)
    test_data = db.Column(db.Text)
    branches = db.Column(db.String(300), default="master")
    notes = db.Column(db.Text, default="default")
    compare_branches = db.Column(db.String(100), default="master")
    if_report = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default="todo")
    test_report_link = db.Column(db.String(100))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class ApplicationForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired()])
    jira_ticket = StringField('Jira Ticket', validators=[DataRequired()])
    expect_time = StringField('Except Time')
    test_data = StringField('Test Data')
    submit = SubmitField('Submit')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/', methods=['POST', 'GET'])
def index(page=1):
    form = ApplicationForm()
    if form.validate_on_submit():
        if form.submit.data:
            application = Application(
                author=current_user.username,
                description=form.description.data,
                jira_ticket=form.jira_ticket.data,
                expected_time=datetime.strptime(form.expect_time.data, '%Y-%m-%d %H:%M'),
                test_data=form.test_data.data,
                create_time=datetime.strptime(datetime.now().strftime('%b-%d-%Y %H:%M:%S'), '%b-%d-%Y %H:%M:%S')
            )
            db.session.add(application)
            db.session.commit()
            flash("Submit success", "success")
            return redirect(url_for('index'))
    pagination = Application.query.order_by(Application.create_time.desc()).paginate(page, app.config[
        'APPLICATIONS_PER_PAGE'])
    return render_template('index.html', form=form, pagination=pagination)


@app.route('/page/<int:page>')
def get_page(page):
    pagination = Application.query.order_by(Application.create_time.desc()).paginate(page, app.config[
        'APPLICATIONS_PER_PAGE'])
    return render_template('paginations.html', pagination=pagination)


#
# @app.route('/page/<string:username>/<int:page>')
# def get_my_page(username, page=1):
#     print("username", username)
#     pagination = Application.query.filter_by(author=username).paginate(page, app.config['APPLICATIONS_PER_PAGE'])
#     return render_template('paginations.html', pagination=pagination)
#
#
# @app.route('/history/<string:username>/<int:page>', methods=['GET'])
# @app.route('/history/<string:username>', methods=['GET'])
# @app.route('/history')
# def get_history(username, page=1):
#     print("username", username)
#     pagination = Application.query.filter_by(author=username).paginate(page, app.config['APPLICATIONS_PER_PAGE'])
#     return render_template('paginations.html', pagination=pagination)


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
            flash("Log in success", 'success')
            return redirect(url_for('index'))
        flash('Please enter the correct username or password', category='error')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", category='success')
    return redirect(url_for('index'))


def auth_(form):
    if os.getenv("FLASK_ENV") == 'development':
        return make_response('', 200)
    return requests.get(url=os.getenv('RESTFUL_API_URL'),
                        auth=HTTPBasicAuth(str(form.username.data), str(form.password.data)))


@app.cli.command()
@click.option('--count', default=20, help='num of data')
def initdb(count):
    db.drop_all()
    db.create_all()
    click.echo("Start init db")
    fake = Faker()
    for i in range(count):
        username = fake.name()
        user = User(username=username,role=)
        application = Application(
            author=fake.name(),
            description=fake.sentence(),
            jira_ticket=fake.license_plate(),
            expected_time=fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None),
            test_data=fake.company(),
            create_time=datetime.strptime(datetime.now().strftime('%b-%d-%Y %H:%M:%S'), '%b-%d-%Y %H:%M:%S')
        )
        db.session.add(application)
    db.session.commit()
    click.echo("Initialized database")


if __name__ == '__main__':
    app.run()
