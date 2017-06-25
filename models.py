# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 22:34:18 2017

@author: colmc
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    """Base data model for all objects"""
    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self._to_dict().items()
        })

    def json(self):
        """
                Define a base way to jsonify models, dealing with datetime objects
        """
        return {
            column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
            for column, value in self._to_dict().items()
        }


class Logo(BaseModel, db.Model):
    """Model for the logos table"""
    __tablename__ = 'logos'

    name = db.Column(db.String, primary_key = True)
    has_face = db.Column(db.Boolean)
    logo_url = db.Column(db.String)
    load_time = db.Column(db.DateTime)

    
class Charity(BaseModel, db.Model):
    """Model for the charity table"""
    __tablename__ = 'charity'

    name = db.Column(db.String, primary_key = True)
    category = db.Column(db.String)
    country = db.Column(db.String)
    number = db.Column(db.Integer)
    donation_options = db.Column(db.String)
    load_time = db.Column(db.DateTime)
    
    
class Description(BaseModel, db.Model):
    """Model for the description table"""
    __tablename__ = 'description'

    name = db.Column(db.String, primary_key = True)
    description = db.Column(db.String)
    load_time = db.Column(db.DateTime)