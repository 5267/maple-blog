# *************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   File Name: db_create.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2016-02-11 13:34:38
# *************************************************************************
# !/usr/bin/env python
# -*- coding=UTF-8 -*-
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from maple import app, db
from maple.user.models import User
from getpass import getpass
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

migrate = Migrate(app, db)
manager = Manager(app)


@manager.command
def run():
    return app.run()


@manager.command
def init_db():
    """
    Drops and re-creates the SQL schema
    """
    db.drop_all()
    db.configure_mappers()
    db.create_all()
    db.session.commit()


@manager.command
def babel_init():
    pybabel = 'pybabel'
    os.system(pybabel +
              ' extract -F babel.cfg -k lazy_gettext -o messages.pot maple')
    os.system(pybabel + ' init -i messages.pot -d translations -l zh')
    os.unlink('messages.pot')


@manager.command
def babel_update():
    pybabel = 'pybabel'
    os.system(
        pybabel +
        ' extract -F babel.cfg -k lazy_gettext -o messages.pot maple templates')
    os.system(pybabel + ' update -i messages.pot -d translations')
    os.unlink('messages.pot')


@manager.command
def babel_compile():
    pybabel = 'pybabel'
    os.system(pybabel + ' compile -d translations')


@manager.option('-u', '--username', dest='username', default='admin')
@manager.option('-e', '--email', dest='email')
@manager.option('-w', '--password', dest='password')
def create_user(username, email, password):
    if username == 'admin':
        username = input('Username(default admin):')
    if email is None:
        email = input('Email:')
    if password is None:
        password = getpass('Password:')
    user = User()
    user.username = username
    user.password = generate_password_hash(password)
    user.email = email
    user.is_superuser = True
    user.is_confirmed = True
    user.roles = 'super'
    user.registered_time = datetime.utcnow()
    user.confirmed_time = datetime.utcnow()
    db.session.add(user)
    db.session.commit()


@manager.option('-h', '--host', dest='host', default='127.0.0.1')
@manager.option('-p', '--port', dest='port', type=int, default=8000)
@manager.option('-w', '--workers', dest='workers', type=int, default=2)
def gunicorn(host, port, workers):
    """use gunicorn"""
    from gunicorn.app.base import Application

    class FlaskApplication(Application):
        def init(self, parser, opts, args):
            return {'bind': '{0}:{1}'.format(host, port), 'workers': workers}

        def load(self):
            return app

    application = FlaskApplication()
    return application.run()


manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
