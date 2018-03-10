#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2018 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2018-01-08 14:24:18 (CST)
# Last Update: Saturday 2018-03-10 16:37:14 (CST)
#          By:
# Description:
# **************************************************************************
from .index import (IndexView, AboutView, FriendView)
from .blog import BlogListView, BlogView, ArchiveView
from .timeline import TimeLineView


def init_app(app):
    index_view = IndexView.as_view('index')
    about_view = AboutView.as_view('about')
    friend_view = FriendView.as_view('friend')
    app.add_url_rule('/', view_func=index_view)
    app.add_url_rule('/index', view_func=index_view)
    app.add_url_rule('/about', view_func=about_view)
    app.add_url_rule('/friends', view_func=friend_view)

    app.add_url_rule('/blog', view_func=BlogListView.as_view('blog.bloglist'))
    app.add_url_rule('/blog/<int:pk>', view_func=BlogView.as_view('blog.blog'))
    app.add_url_rule(
        '/archives', view_func=ArchiveView.as_view('blog.archive'))

    app.add_url_rule(
        '/timeline', view_func=TimeLineView.as_view('timeline'))
