#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 meiritugua.com

import tornado.web
import lib.session
import time
import helper

class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.session = lib.session.Session(self.application.session_manager, self)
        self.jinja2 = self.settings.get("jinja2")
        self.jinja2 = helper.Filters(self.jinja2).register()

    @property
    def db(self):
        return self.application.db

    @property
    def loader(self):
        return self.application.loader

    @property
    def mc(self):
        return self.application.mc

    def render(self, template_name, **template_vars):
        html = self.render_string(template_name, **template_vars)
        self.write(html)

    def render_string(self, template_name, **template_vars):
        template_vars["xsrf_form_html"] = self.xsrf_form_html
        template_vars["current_user"] = self.current_user
        template_vars["request"] = self.request
        template_vars["request_handler"] = self
        template = self.jinja2.get_template(template_name)
        return template.render(**template_vars)

    def render_from_string(self, template_string, **template_vars):
        template = self.jinja2.from_string(template_string)
        return template.render(**template_vars)

    @property
    def user_model(self):
        return self.application.user_model

    @property
    def post_model(self):
        return self.application.post_model

    @property
    def head1_model(self):
        return self.application.head1_model

    @property
    def head2_model(self):
        return self.application.head2_model

    @property
    def std_model(self):
        return self.application.std_model

    @property
    def ooxx_model(self):
        return self.application.ooxx_model

    @property
    def hot_model(self):
        return self.application.hot_model

    @property
    def comment_model(self):
        return self.application.comment_model

    @property
    def nav_model(self):
        return self.application.nav_model

    @property
    def channel_model(self):
        return self.application.channel_model

    @property
    def head_model(self):
        return self.application.head_model

    @property
    def post_tag_model(self):
        return self.application.post_tag_model

    @property
    def tag_model(self):
        return self.application.tag_model

    @property
    def vote_model(self):
        return self.application.vote_model

    @property
    def item_model(self):
        return self.application.item_model

    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        return self.user_model.get_user_by_uid(int(user_id))