import pandas as pd
from datetime import timezone, datetime, timedelta
import json
import requests
from dateutil.relativedelta import relativedelta
from calendar import Calendar
import time
import pymysql
import pymysql.cursors


"""
Returns any scheduled holidays for the time period
"""
startdate = "2022-01-01"
enddate = "2023-01-01"

dbhost = "mysqlserver"
dbuser = "sched"
dbpwd  = "sched"
db     = "common"
hConn = pymysql.connect(host=dbhost, user=dbuser, password=dbpwd, db=db, cursorclass=pymysql.cursors.DictCursor)
hCursor = hConn.cursor()

query = 'SELECT * FROM holidays WHERE date>=%s and date<=%s'
result = hCursor.execute(query, (startdate,enddate,))
entries = hCursor.fetchall()

if hConn:
    hCursor.close()
    hConn.close()

holidays = []
for entry in entries:
    holidays.append(entry['date'].strftime('%Y-%m-%d'))

print(json.dumps(holidays)) 