#-*- coding:utf-8 -*-
import os
from flask import Flask
from flask import request
from flask import redirect

#-- create app --
app = Flask(__name__)
app.config.from_object("rrd.config")

@app.errorhandler(Exception)
def all_exception_handler(error):
    print "exception: %s" %error
    return u'dashboard 暂时无法访问，请联系管理员', 500

from view import api, chart, screen, index

@app.before_request
def before_request():
    sig = request.cookies.get('sig')
    if not sig:
        return redirect(config.JSONCFG['redirectUrl'], code=302)
