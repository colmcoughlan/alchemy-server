#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 01:14:12 2017

@author: colm
"""

from flask import Flask, jsonify
from parse_likecharity import refresh_charities
import threading

refresh_rate = 24 * 60 * 60 #Seconds

# variables that are accessible from anywhere
payload = {}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
backgroundThread = threading.Thread()


app = Flask(__name__)

def update_charities():
  print('Updating charities in background thread')
  
  global payload
  global backgroundThread
  with dataLock:
  
    categories, charity_dict = refresh_charities()
    payload = {'categories':categories, 'charities':charity_dict}
    print('Running!')
  
  # Set the next thread to happen
  backgroundThread = threading.Timer(refresh_rate, update_charities, ())
  backgroundThread.start() 

@app.route("/")
def gci():
  return jsonify(payload)

if __name__ == "__main__":
  
  update_charities()
  app.run(host='0.0.0.0')
  backgroundThread.cancel()
  print('test')
