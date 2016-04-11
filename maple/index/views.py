#!/usr/bin/env python
# -*- coding=UTF-8 -*-
# *************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   File Name: index.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2015-11-25 02:21:04
# *************************************************************************
from flask import Blueprint, render_template
from maple import login_manager
from maple.user.models import User
from maple.blog.models import Articles
from maple.question.models import Questions
from maple.admin.models import Notices

site = Blueprint('index', __name__, url_prefix='')


@login_manager.user_loader
def user_loader(id):
    user = User.query.get(int(id))
    return user


@site.route('/')
@site.route('/index')
def index():
    articles = Articles.query.order_by(Articles.publish.desc()).limit(7)
    questions = Questions.query.order_by(Questions.publish.desc()).\
        filter_by(private=False).limit(7)
    notice = Notices.query.order_by(Notices.publish.desc()).first()
    return render_template('index/index.html',
                           articles=articles,
                           questions=questions,
                           notice=notice)


@site.route('/about')
def about():
    about = Articles.query.filter_by(id=26).first()
    content = about.content
    return render_template('index/about_me.html', content=content)
