# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 17:56:25 2017

@author: colmc
"""

import requests
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser
import json
import time
import os
import cv2

from models import Charity, Logo, Description
from logo_check import check_for_faces

source_url = 'https://api.likecharity.com/charities/?json'
source_country = 'Ireland'
source_number = '50300'


def get_google_api_key(config_file = '../etc/alchemy-keys/google-api-keys.ini'):
    '''
    Get the google API key from local storage
    '''
    parser = ConfigParser()
    retval = parser.read(config_file)
    if len(retval) != 1:
            print('Error: could not find '+config_file)
            raise FileNotFoundError
    
    cx = parser['google_api_keys']['cx']
    key = parser['google_api_keys']['key']

    return cx, key


def update_charities(session):
    '''
    Use the LIKECHARITY API to get charity donation options as json, parse them into a pandas DF and replace existing SQL table
    Note the json comes as a list of 1 entry per keyword, NOT per charity
    '''

    r = requests.post(source_url)
    charities = {}
    
    for keyword in r.json():
        if keyword['CharityName'] not in charities:
            payload = {}
            payload['category'] = keyword['Category']
            payload['donation_options'] = {keyword['Keyword']:'€'+str(int(float(keyword['Amount'])/100.0))}
            charities[keyword['CharityName']] = payload
        else:
            charities[keyword['CharityName']]['donation_options'][keyword['Keyword']]  = '€'+str(int(float(keyword['Amount'])/100.0))
            
    charities = pd.DataFrame.from_dict(charities, orient='index')
    charities['donation_options'] = json.dumps(charities['donation_options'].values.tolist())
    charities['number'] = source_number
    charities['country'] = source_country
    charities['load_time'] = datetime.utcnow()
                
    session.query(Charity).delete()
    session.commit()
    
    # add new ones, replacing old ones
    charities.to_sql(name='charity', con=session.bind, if_exists = 'append', index_label = 'name')
    
    return 0

def get_descriptions(session):
    '''
    Identify charities without descriptions.
    Use google custom search API to find descriptions for them
    Update SQL with new description
    '''
    charities = session.query(Charity.name)\
    .outerjoin(Description, Charity.name == Description.name)\
    .filter(Description.name == None) # left outer join
    
    cx, key = get_google_api_key()

    payloads = []
    for charity in charities:
        try:
            r = requests.get('https://www.googleapis.com/customsearch/v1?q='+charity.name+' charity ireland&cx='+cx+'&key='+key+'M&num=1')
            payloads.append({'name':charity.name, 'description':r.json()['items'][0]['snippet']})
            time.sleep(1) # don't overload API with requests. Need to also bear in mind restriction of 100 reqs a day
        except KeyError:
            break    # must be out of quota, no point in trying for more

    if len(payloads) > 0:
        charities = pd.DataFrame(payloads)
        charities['load_time'] = datetime.utcnow()
        charities.to_sql(name='description', con=session.bind, if_exists = 'append', index=False)

    return len(payloads)

def get_logos(session, faceCascade):
    '''
    Identify charities without images.
    Use google custom search API to find descriptions for them
    Check to see if there is a face in the image (will not actually be used if true)
    Update SQL with new image and boolean has_face
    '''
    charities = session.query(Charity.name)\
    .outerjoin(Logo, Charity.name == Logo.name)\
    .filter(Logo.name == None) # left outer join
    
    cx, key = get_google_api_key()

    payloads = []
    for charity in charities:
        try:
            r = requests.get('https://www.googleapis.com/customsearch/v1?q='+charity.name+' logo&searchType=image&cx='+cx+'&key='+key+'M&num=1')
            link = r.json()['items'][0]['link']
            has_face = check_for_faces(charity.name, link, faceCascade)
            payloads.append({'name':charity.name, 'has_face':has_face, 'logo_url':link})
            time.sleep(1) # don't overload API with requests. Need to also bear in mind restriction of 100 reqs a day
        except KeyError:
            break    # must be out of quota, no point in trying for more

    if len(payloads) > 0:
        charities = pd.DataFrame(payloads)
        charities['load_time'] = datetime.utcnow()
        charities.to_sql(name='logos', con=session.bind, if_exists = 'append', index=False)

    return len(payloads)
        
if __name__ == "__main__":
    
    db = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=db)
    session = Session()
    
    cascPath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)
    
    update_charities(session)
    get_descriptions(session)
    get_logos(session, faceCascade)
    
    session.close()
    db.dispose()
            
