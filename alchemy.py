# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 17:56:25 2017

@author: colmc
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from flask_sqlalchemy.SQLAlchemy import Table, MetaData, bindparam, create_engine
import os

source_url = 'https://api.likecharity.com/charities/'
source_country = 'Ireland'
source_number = '50300'

def update_charities(conn):

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
            payload['donation_list'] = {}
            payload['category'] = category
            payload['number'] = source_number
            payload['country'] = source_country
            for entry in charity_key_value.findAll(text=True):
                key = entry.split(' - ')
                if len(key) != 2:
                    print('Bad key value splitting')
                    raise(Exception)
                payload['donation_list'][key[0]] = key[1]
                
            payloads.append(payload)
            
    charities = pd.DataFrame(payloads)
    query = 'SELECT * FROM CHARITY'
    saved_charities = pd.read_sql_query(query, conn)
    
    metadata = MetaData(conn)
    charity = Table('charity', metadata, autoload=True)
    
    # update existing tables
    query = charity.update().\
                          where(charity.c.name == bindparam('name')).\
                          values(donation_list=bindparam('donation_list'), category=bindparam('category'))
    conn.execute(query, [saved_charities['name', 'donation_list', 'category'].to_dict()])
    
    # add new ones
    charities = charities[-charities['name'].isin(saved_charities['name'])]
    charities['load_time'] = datetime.utcnow()
    charities.to_sql(name='charity', con=conn, if_exists = 'append', index=False)
        
if __name__ == "__main__":
    
    conn = create_engine(os.environ['SQLALCHEMY_DATABASE_URI']).connect()
    
    categories, charity_dict = update_charities(conn)
    conn.close()
            
