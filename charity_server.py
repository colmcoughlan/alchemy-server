#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 01:14:12 2017

@author: colm
"""

from flask import Flask, jsonify
from parse_likecharity import refresh_charities
from datetime import datetime
import os

app = Flask(__name__)

refresh_rate = 24 * 60 * 60 #Seconds
start_time = datetime.now()
initialized = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.env['SQLALCHEMY_DATABASE_URI']

# variables that are accessible from anywhere
payload = {}

@app.route("/gci")
def gci():
  global payload
  global initialized
  delta = datetime.now() - start_time
  if delta.total_seconds() > refresh_rate or not(initialized):
      categories, charity_dict = refresh_charities()
      initialized = True
      payload = {'categories':categories, 'charities':charity_dict}
  return jsonify(payload)

if __name__ == "__main__":
  categories, charity_dict = refresh_charities()
  app.run(host='0.0.0.0')
  print('test')
