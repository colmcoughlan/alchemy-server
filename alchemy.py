# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 17:56:25 2017

@author: colmc
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from sqlalchemy import Table, MetaData, create_engine
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser
import json
import os

from models import Charity, Logo ,Description

source_url = 'https://api.likecharity.com/charities/'
source_country = 'Ireland'
source_number = '50300'

def get_google_api_key(config_file = '../etc/alchemy-keys/google-api-keys.ini'):
    parser = ConfigParser()
    retval = parser.read(config_file)
    if len(retval) != 1:
            print('Error: could not find '+config_file)
            raise FileNotFoundError
    
    cx = parser['google_api_keys']['cx']
    key = parser['google_api_keys']['key']

    return cx, key


def update_charities(session):

    r = requests.get(source_url)
    
    soup = BeautifulSoup(r.text, "lxml")
    
    categories_soup = soup.findAll("div", { "class" : "filter--categories" })
    categories_soup = categories_soup[0].findAll("option")
    categories = []
    for category in categories_soup:
        cat_name = category.findAll(text=True)[0]
        if 'Choose Category' != cat_name:
            categories.append(cat_name)
    
    payloads = []
    for category in categories:
        
        print('Working on '+category)
        
        r = requests.post(source_url, data = {'category_name':category})
    
        soup = BeautifulSoup(r.text, "lxml")
    
        charities = soup.findAll("h3", { "class" : "charity" })
        charities_key_value = soup.findAll("div", { "class" : "keywords" })
        
        
        # get the info for the charities
        for charity, charity_key_value in zip(charities, charities_key_value):
            payload = {}
            payload['name'] = ''.join(charity.findAll(text=True))
            payload['donation_options'] = {}
            payload['category'] = category
            payload['number'] = source_number
            payload['country'] = source_country
            for entry in charity_key_value.findAll(text=True):
                key = entry.split(' - ')
                if len(key) != 2:
                    print('Bad key value splitting')
                    raise(Exception)
                payload['donation_options'][key[0]] = key[1]
                
            payload['donation_options'] = json.dumps(payload['donation_options'])
                
            payloads.append(payload)
            
    charities = pd.DataFrame(payloads)
    
    session.query(Charity).delete()
    session.commit()
    
    # add new ones, replacing old ones
    charities['load_time'] = datetime.utcnow()
    charities.to_sql(name='charity', con=session.bind, if_exists = 'append', index=False)
    
    return 0

def get_descriptions(session):
    
    charities = session.query(Charity.name)\
    .outerjoin(Description, Charity.name == Description.name)
    
    cx, key = get_google_api_key()

    payloads = []
    for charity in charities:
        try:
            r = requests.get('https://www.googleapis.com/customsearch/v1?q='+charity.name+' charity ireland&cx='+cx+'&key='+key+'M&num=1')
            payloads.append({'name':charity.name, 'description':r.json()['items'][0]['snippet']})
            break
        except KeyError:
            break    # must be out of quota, no point in trying for more

    if len(payloads) > 0:
        charities = pd.DataFrame(payloads)
        charities['load_time'] = datetime.utcnow()
        charities.to_sql(name='description', con=session.bind, if_exists = 'append', index=False)

    return len(payloads)
        
if __name__ == "__main__":
    
    db = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=db)
    session = Session()
    
    update_charities(session)
    get_descriptions(session)
    
    session.close()
    db.dispose()
            
