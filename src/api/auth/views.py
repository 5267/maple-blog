#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2016 jianglin
# File Name: views.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2016-12-25 15:28:39 (CST)
# Last Update:星期二 2017-1-31 9:54:27 (CST)
#          By:
# Description:
# **************************************************************************
from flask import request, url_for, render_template, redirect
from flask.views import MethodView
from flask_login import login_user, logout_user, current_user, login_required
from flask_babelex import gettext as _
from flask_maple.serializer import Serializer
from .forms import (LoginForm, RegisterForm, ForgetForm, form_validate)
from maple.user.models import User
from common.response import HTTPResponse
from random import sample
from string import ascii_letters, digits


class LoginView(MethodView):
    def get(self):
        form = LoginForm()
        data = {'form': form}
        return render_template('auth/login.html', **data)

    @form_validate(LoginForm)
    def post(self):
        form = LoginForm()
        post_data = form.data
        username = post_data.pop('username', None)
        password = post_data.pop('password', None)
        remember = post_data.pop('remember', None)
        remember = True if remember else None
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            serializer = Serializer(user, many=False, depth=1)
            return HTTPResponse(
                HTTPResponse.NORMAL_STATUS, data=serializer.data).to_response()
        return HTTPResponse(
            HTTPResponse.AUTH_USER_OR_PASSWORD_ERROR).to_response()


class LogoutView(MethodView):
    @login_required
    def get(self):
        logout_user()
        return redirect(request.args.get('next') or '/')


class RegisterView(MethodView):
    def get(self):
        form = RegisterForm()
        data = {'form': form}
        return render_template('auth/register.html', **data)

    @form_validate(RegisterForm)
    def post(self):
        form = RegisterForm()
        post_data = form.data
        username = post_data.pop('username', None)
        email = post_data.pop('email', None)
        password = post_data.pop('password', None)
        user = User.query.filter_by(username=username).first()
        if user is not None:
            return HTTPResponse(HTTPResponse.AUTH_USERNAME_UNIQUE).to_response(
            )
        user = User.query.filter_by(email=email).first()
        if user is not None:
            return HTTPResponse(HTTPResponse.AUTH_EMAIL_UNIQUE).to_response()
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        login_user(user)
        self.email(user)
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()

    def email(self, user):
        token = user.email_token()
        confirm_url = url_for(
            'auth.confirm_token', token=token, _external=True)
        html = render_template('templet/email.html', confirm_url=confirm_url)
        subject = _("Please confirm  your email!")
        user.send_email(subject=subject, html=html)


class ForgetView(MethodView):
    def get(self):
        form = ForgetForm()
        data = {'form': form}
        return render_template('auth/forget.html', **data)

    @form_validate(ForgetForm)
    def post(self):
        form = ForgetForm()
        post_data = form.data
        email = post_data.pop('email', None)
        user = User.query.filter_by(email=email).first()
        if not user:
            return HTTPResponse(
                HTTPResponse.AUTH_EMAIL_NOT_REGISTER).to_response()
        password = ''.join(sample(ascii_letters + digits, 12))
        user.set_password(password)
        user.save()
        self.email(user)
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()

    def email(self, user):
        html = render_template(
            'templet/forget.html', confirm_url=user.password)
        subject = "Please update your password in time"
        user.send_email(html, subject)


class ConfirmView(MethodView):
    @login_required
    def post(self):
        if current_user.is_confirmed:
            return HTTPResponse(
                HTTPResponse.AUTH_USER_IS_CONFIRMED).to_response()
        token = current_user.email_token()
        confirm_url = url_for(
            'auth.confirm_token', token=token, _external=True)
        html = render_template('templet/email.html', confirm_url=confirm_url)
        subject = _("Please confirm  your email")
        current_user.send_email(html, subject)
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()


class ConfirmTokenView(MethodView):
    def get(self, token):
        user = User.check_email_token(token)
        if not user:
            return HTTPResponse(
                HTTPResponse.AUTH_TOKEN_VERIFY_FAIL).to_response()
        if user.is_confirmed:
            return HTTPResponse(
                HTTPResponse.AUTH_USER_IS_CONFIRMED).to_response()
        user.is_confirmed = True
        user.save()
        return HTTPResponse(HTTPResponse.NORMAL_STATUS).to_response()
