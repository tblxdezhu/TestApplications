from flask import Flask, render_template, request, url_for, redirect, flash, make_response, jsonify, current_app
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, RadioField, \
    IntegerField
from wtforms.validators import DataRequired, Length, URL, InputRequired
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
from flask_mail import Mail, Message
from default_settings import DefaultConfig

app = Flask(__name__)
app.config.from_object(config[DefaultConfig.FLASK_ENV])
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)
db = SQLAlchemy(app)
mail = Mail(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    role = db.Column(db.String(20))
    team = db.Column(db.String(20))
    email = db.Column(db.String(20))
    applications = db.relationship('Application', back_populates='author')


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    author = db.relationship('User', back_populates='applications')
    description = db.Column(db.Text)
    jira_ticket = db.Column(db.String(100), index=True)
    create_time = db.Column(db.DateTime, index=True)
    expected_time = db.Column(db.DateTime, nullable=True)
    test_data = db.Column(db.Text)
    branches = db.Column(db.Text)
    notes = db.Column(db.Text, default="default")
    compare_branches = db.Column(db.Text)
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
    test_data = TextAreaField('Test Data')
    compare_branches = TextAreaField('Base Branches')
    notes = TextAreaField('Notes')
    team = SelectField('Team', choices=[('SLAM', 'SLAM'), ('SVM', 'SVM')])
    submit = SubmitField('Submit')


class ResultForm(FlaskForm):
    id = StringField('Application id', validators=[DataRequired()])
    link = StringField('Test Report Link / PR')
    status = SelectField('Status', choices=[('Pass', 'Pass'), ('Failed', 'Failed')], validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Confirm')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/', methods=['POST', 'GET'])
def index(page=1):
    form = ApplicationForm()
    if form.validate_on_submit():
        if form.submit.data:
            branches = get_branch(request)
            application = Application(
                author_id=current_user.id,
                description=form.description.data,
                jira_ticket=form.jira_ticket.data,
                expected_time=datetime.strptime(form.expect_time.data, '%Y-%m-%d %H:%M'),
                test_data=form.test_data.data,
                create_time=datetime.strptime(datetime.now().strftime('%b-%d-%Y %H:%M:%S'), '%b-%d-%Y %H:%M:%S'),
                branches=branches[0],
                compare_branches=branches[1],
                notes=form.notes.data
            )
            application.author = current_user
            application.author.team = form.team.data
            db.session.add(application)
            db.session.commit()
            send_mail(mail_type='application', application=application)
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


def get_branch(_request):
    test_branches = [{
        'repo': 'others',
        'branch': _request.form['others_branch']
    }]
    base_branches = [{
        'repo': 'others',
        'branch': _request.form['others_basebranch'] if _request.form['others_basebranch'] else 'master'
    }]
    for _data in _request.form:
        if 'test_branch' in _data:
            i = int(_data[-1])
            test_branches.append({
                'repo': _request.form['test_repo{}'.format(i)],
                'branch': _request.form['test_branch{}'.format(i)]
            })
        if 'base_branch' in _data:
            i = int(_data[-1])
            base_branches.append({
                'repo': _request.form['base_repo{}'.format(i)],
                'branch': _request.form['base_branch{}'.format(i)]
            })
    return str(test_branches), str(base_branches)


def send_mail(mail_type, application):
    current_user_email = current_user.username + "@ygomi.com",
    message = Message(
        subject=application.jira_ticket,
        sender=current_user_email[0],
        cc=['zhixun.xia@ygomi.com', 'ming.lei@ygomi.com', 'nan.jia@ygomi.com']
    )

    if mail_type == 'reply':
        message.recipients = [application.author.username + "@ygomi.com"]
        message.cc.extend(['zhenxuan.xu@ygomi.com', 'xin.li@ygomi.com'])
        message.body = render_template('reply.txt', application=application, server=app.config['SERVER_ADDRESS'],
                                       port=app.config['FLASK_RUN_PORT'])
    else:
        if application.author.team == 'SLAM':
            message.recipients = ['zhenxuan.xu@ygomi.com']
            message.cc.append('xin.li@ygomi.com')
        else:
            message.recipients = ['xin.li@ygomi.com']
            message.cc.append('zhenxuan.xu@ygomi.com')
        message.body = render_template('application.txt', name=current_user.username, application=application,
                                       server=app.config['SERVER_ADDRESS'], port=app.config['FLASK_RUN_PORT'])
    # mail.send(message)
    print("sender: ", message.sender)
    print("recipients:  ", message.recipients)
    print("cc:  ", message.cc)


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


@app.route('/applications/<int:application_id>')
def get_application(application_id):
    try:
        application = Application.query.get(application_id)
        branches = eval(application.branches)
        base_branches = eval(application.compare_branches)
        return render_template('application.html', application=application, branches=branches, base_branches=base_branches)
    except Exception as e:
        print(e)
        return render_template('404.html'), 404


@app.route('/management', methods=['POST', 'GET'])
@login_required
def admin():
    if not current_user.username == 'zhenxuan.xu' or current_user.username == 'xin.li':
        flash('You are not authorized to access this page', category='error')
        return redirect(url_for('index'))
    form = ResultForm()
    if form.validate_on_submit():
        application = Application.query.get(request.form['id'])
        application.test_report_link = form.link.data
        application.status = form.status.data
        db.session.commit()
        flash("Successfully modified", 'success')
        send_mail(mail_type='reply', application=application)
        return redirect(url_for('admin'))
    applications = Application.query.order_by(Application.id.desc())
    return render_template('my_applications.html', applications=applications, form=form)


# @app.route('/version')
def get_version():
    return render_template('release.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", category='success')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def auth_(form):
    if app.config['FLASK_ENV'] == 'development':
        return make_response('', 200)
    return requests.get(url=app.config['RESTFUL_API_URL'],
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
        user = User(username=username, role="developer", team="SLAM")
        application = Application(
            author_id=user.id,
            description=fake.sentence(),
            jira_ticket=fake.license_plate(),
            expected_time=fake.date_time_this_decade(before_now=True, after_now=False, tzinfo=None),
            test_data=fake.company(),
            create_time=datetime.strptime(datetime.now().strftime('%b-%d-%Y %H:%M:%S'), '%b-%d-%Y %H:%M:%S'),
            branches=fake.sentence(),
            compare_branches=fake.sentence(),
            notes=fake.sentence()
        )
        application.author = user
        db.session.add(user)
        db.session.add(application)
    db.session.commit()
    click.echo("Initialized database")


if __name__ == '__main__':
    app.run(host=app.config['FLASK_RUN_HOST'], port=app.config['FLASK_RUN_PORT'])
