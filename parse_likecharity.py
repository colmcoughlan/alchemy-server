#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 23:20:13 2017

@author: colm
"""

from bs4 import BeautifulSoup
import requests
import time
import json
from configparser import ConfigParser

def get_google_api_key(config_file = '/home/colm/alchemy-keys/google-api-keys.ini'):
  parser = ConfigParser()
  retval = parser.read(config_file)
  if len(retval) != 1:
    print('Error: could not find '+config_file)
    raise FileNotFoundError
    
  cx = parser['google_api_keys']['cx']
  key = parser['google_api_keys']['key']
  
  return cx, key

def update_logo_from_google(charity, cx, key):

  #print('Fetching logo for '+charity)
  r = requests.get('https://www.googleapis.com/customsearch/v1?q='+charity+' charity logo&searchType=image&cx='+cx+'&key='+key+'M&num=1')
  try:
    link = r.json()['items'][0]['link']
  except KeyError:
    link = ''
    
    time.sleep(1) # don't overload API with requests. Need to also bear in mind restriction of 100 reqs a day
  
  return link

def repair_charities(charity_dict, cx, api_key):
  
  repair_list = []
  
  for charity, info in charity_dict.items():
    print(info)
    time.sleep(3)
    if info['logo'] == '':
      repair_list.append(charity)
  
  if len(repair_list) > 0:
    print('Repairing '+str(len(repair_list))+' charities')
    for charity in repair_list:
      charity_dict[charity]['logo'] = update_logo_from_google(charity, cx, api_key)
  
  return charity_dict
  


# refresh list of charities
# load latest list
# search for more
#     - by category if possible
# if new ones are detected, get logos for them
# perform check for missing logos - get logos for them

def refresh_charities():
  
  try:
    with open('charity_info.json', 'r') as f:
      old_list = json.load(f)
      print(str(len(old_list)) + 'charities loaded from stored json.')
  except FileNotFoundError:
    old_list = {}
    print('No stored json found, will start from scratch.')
    
  cx, api_key = get_google_api_key()

  r = requests.get('https://api.likecharity.com/charities/')
  
  soup = BeautifulSoup(r.text, "lxml")
  
  categories_soup = soup.findAll("div", { "class" : "filter--categories" })
  categories_soup = categories_soup[0].findAll("option")
  categories = []
  for category in categories_soup:
    cat_name = category.findAll(text=True)[0]
    if 'Choose Category' != cat_name:
      categories.append(cat_name)
  
  print(categories)
  charity_dict = {}
  
  for category in categories:
    
    print('Working on '+category)
    
    r = requests.post('https://api.likecharity.com/charities/', data = {'category_name':category})
  
    soup = BeautifulSoup(r.text, "lxml")
  
    charities = soup.findAll("h3", { "class" : "charity" })
    charities_key_value = soup.findAll("div", { "class" : "keywords" })
    
    
    # get the info for the charities
  
    for charity, charity_key_value in zip(charities, charities_key_value):
      payload = {}
      payload['donation_list'] = {}
      payload['category'] = category
      payload['logo'] = ''
      payload['number'] = '50300'
      for entry in charity_key_value.findAll(text=True):
        key = entry.split(' - ')
        if len(key) != 2:
          print('Bad key value splitting')
          raise(Exception)
        payload['donation_list'][key[0]] = key[1]
      
      charity_name = ''.join(charity.findAll(text=True))
      charity_dict[charity_name] =  payload
    
    
  new_charities = set(charity_dict.keys()) - set(old_list.keys())
  
  if len(new_charities) > 0:
    print(str(len(new_charities))+' new charities detected. Pulling logos from google images.')
    for charity in new_charities:
      charity_dict[charity]['logo'] = update_logo_from_google(charity, cx, api_key)
    
  charity_dict = repair_charities(charity_dict, cx, api_key)
    
  with open('charity_info.json', 'w') as f:
    json.dump(charity_dict, f)
  
  return categories, charity_dict

if __name__ == "__main__":
  categories, charity_dict = refresh_charities()

