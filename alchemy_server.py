#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 01:14:12 2017

@author: colm
"""

from flask import Flask, jsonify
import os
from models import Charity, Logo, Description
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
db = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=db)
session = Session()



@app.route("/gci")
def gci():
    global session

    query = session.query(Charity.name, Charity.category, Charity.number, Charity.donation_options, Description.description, Logo.logo_url, Logo.has_face)\
    .join(Logo, Charity.name == Logo.name)\
    .join(Description, Charity.name == Description.name)

    charities = pd.read_sql(query.statement, con=session.bind, index_col = 'name')
    charities.loc[charities['has_face'], 'logo_url'] = '' # set logos of charities that appear to have faces to an emtpy string
    charities.drop('has_face', axis=1, inplace=True)

    query = session.query(Charity.category).distinct()
    categories = pd.read_sql(query.statement, con = session.bind)
    categories = categories[~categories['category'].str.contains(',')]

    payload = {'categories':categories.values.tolist(), 'charities':charities.to_dict('index')}
    return jsonify(payload)

if __name__ == "__main__":

    app.run(host='0.0.0.0')