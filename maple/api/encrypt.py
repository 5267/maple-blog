#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ********************************************************************************
# Copyright © 2018 jianglin
# File Name: encrypt.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-03-17 17:52:05 (CST)
# Last Update: Saturday 2018-03-17 21:29:24 (CST)
#          By:
# Description:
# ********************************************************************************
from flask import jsonify, request, current_app
from flask.views import MethodView
from base64 import urlsafe_b64encode

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from maple.extension import csrf


class Encrypt(object):
    def __init__(self, password, salt):
        if isinstance(salt, str):
            salt = salt.encode("utf-8")
        self.fernet = Fernet(self.password(password, salt))

    def password(self, raw_password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend())
        return urlsafe_b64encode(kdf.derive(raw_password.encode("utf-8")))

    def encrypt(self, text):
        return self.fernet.encrypt(text.encode("utf-8")).decode("utf-8")

    def decrypt(self, text):
        return self.fernet.decrypt(text.encode("utf-8")).decode("utf-8")


class EncryptAPI(MethodView):
    decorators = (csrf.exempt, )

    def post(self):
        request_data = request.data
        password = request_data.pop('password', '')
        content = request_data.pop('content', '')
        if not password or not content:
            return jsonify(status=401, msg='params required.')
        ec = Encrypt(password, current_app.config['SECRET_KEY_SALT'])
        try:
            return jsonify(status=200, data=ec.decrypt(content))
        except InvalidToken:
            return jsonify(status=401, msg='password is not correct')
