#-*- coding:utf-8 -*-
from flask import request
from flask import redirect
import MySQLdb
import datetime
import time
import json
import os

from flask import render_template
from rrd import app
from rrd import config

"""
* @def name:		queryDB(config, sig)
* @description:		This function returns query result of given SQL command.
* @related issues:	OWL-117
* @param:			list config
* @param:			string sig
* @return:			list rows
* @author:			Don Hsieh
* @since:			10/13/2015
* @last modified:	10/14/2015
* @called by:		def index()
*					 in rrd/view/index.py
"""
def queryDB(sig):
    rows = None
    table = config.JSONCFG['database']['table']
    print table
    fields = 'id, expired'
    # fields = '`id`, `expired`'
    where = '`sig`="' + sig + '"'
    sql = 'SELECT ' + fields + ' FROM `' + table + '`' + ' WHERE ' + where
    try: 
        mydb = MySQLdb.connect(
            host=config.JSONCFG['database']['host'],
            port=int(config.JSONCFG['database']['port']),
            user=config.JSONCFG['database']['account'],
            passwd=config.JSONCFG['database']['password'],
            db=config.JSONCFG['database']['db'],
            charset='utf8'
        )
        cursor = mydb.cursor()
        args = None
        cursor.execute(sql, args)
        rows = cursor.fetchall()
        mydb.commit()
        cursor.close()
        return rows
    except:
        print 'Unexpected error.'
        mydb.rollback()
        mydb.commit()
        cursor.close()
        return rows

@app.route("/")
def index():
	sig = request.cookies.get('sig')
	if sig is None or sig == '':
		return redirect(config.JSONCFG['redirectUrl'], code=302)
		# return redirect("http://portal.owlemon.com", code=302)

	f = open('dashboard.log', 'a')
	f.write('\n' + 'sig = ' + sig + '\n')

	rows = queryDB(sig)
	if rows is None or len(rows) == 0:
		f.close()
		return redirect(config.JSONCFG['redirectUrl'], code=302)

	f.write('rows = ' + str(rows) + '\n')
	row = rows[0]
	# f.write('row = ' + str(row) + '\n')
	id = row[0]
	expiredTime = row[1]
	current_time = datetime.datetime.now()
	f.write('current_time = ' + str(current_time) + '\n')

	now = int(time.time())
	f.write('now = ' + str(now) + '\n')
	f.write('expired time = ' + str(expiredTime) + '\n')
	expired = now > expiredTime
	f.write('expired = ' + str(expired) + '\n')
	f.close()

	if expired:
		return redirect(config.JSONCFG['redirectUrl'], code=302)

	return render_template("index.html", config=config, **locals())
