#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import uuid
import hashlib
import Image
import StringIO
import time
import json
import re
import urllib2
import tornado.web
import lib.jsonp
import pprint
import math
import datetime 
import os.path

from base import *
from lib.variables import *
from form.topic import *
from lib.variables import gen_random
from lib.xss import XssCleaner
from lib.utils import find_mentions
from lib.reddit import hot
from lib.utils import pretty_date

class PostHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
    	user_info = self.current_user
        template_variables["user_info"] = user_info
    	page = int(self.get_argument("page", "1"))
    	template_variables["hots"] = self.hot_model.get_hot_posts(current_page = page)

    	template_variables["post"] = self.post_model.get_post_by_post_id(post_id)
	
        self.render("post.html", **template_variables)

class CreatePostHandler(BaseHandler):
    def get(self, template_variables = {}):
    	user_info = self.current_user
        template_variables["user_info"] = user_info
        self.render("create.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        print "CreateHandler:post"
        template_variables = {}

        # validate the fields
        form = CreateForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed     
        post_info = {
            "author_id": self.current_user["uid"],           
            "title": form.title.data,
            "intro": form.title.data,
            "content": form.content.data,
            "channel_id": 0,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        post_id = self.post_model.add_new_post(post_info)

        std_id = self.std_model.add_new_std({"post_id": post_id, "created": time.strftime('%Y-%m-%d %H:%M:%S')})
        std_id = self.hot_model.add_new_hot({"post_id": post_id, "created": time.strftime('%Y-%m-%d %H:%M:%S')})     



        # process post thumb

        thumb_name = "%s" % uuid.uuid5(uuid.NAMESPACE_DNS, str(post_id))
        thumb_raw = self.request.files["thumb"][0]["body"]
        thumb_buffer = StringIO.StringIO(thumb_raw)
        thumb_origin = Image.open(thumb_buffer)

        # crop avatar if it's not square
        thumb_x = int(form.x1.data)
        thumb_y = int(form.y1.data)
        thumb_w = float(form.x2.data) - float(form.x1.data)
        thumb_h = float(form.y2.data) - float(form.y1.data)
        thumb_crop_region = (thumb_x, thumb_y, int(thumb_w), int(thumb_h))
        thumb = thumb_origin.crop(thumb_crop_region)

        thumb_125x83 = thumb.resize((125, 83), Image.ANTIALIAS)
        usr_home = os.path.expanduser('~')
        thumb_125x83.save(usr_home+"/www/mifan.tv/static/thumb/n_%s.png" % thumb_name, "PNG")


        thumb2_x = int(form.x3.data)
        thumb2_y = int(form.y3.data)
        thumb2_w = float(form.x4.data) - float(form.x3.data)
        thumb2_h = float(form.y4.data) - float(form.y3.data)
        thumb2_crop_region = (thumb2_x, thumb2_y, int(thumb2_w), int(thumb2_h))
        thumb2 = thumb_origin.crop(thumb2_crop_region)

        thumb_355x125 = thumb2.resize((355, 125), Image.ANTIALIAS)
        thumb_355x125.save(usr_home+"/www/mifan.tv/static/thumb/w_%s.png" % thumb_name, "PNG")

        result = self.post_model.set_post_thumb_by_post_id(post_id, "%s.png" % thumb_name)
        
        self.redirect("/")