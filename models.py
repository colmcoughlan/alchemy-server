# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 22:34:18 2017

@author: colmc
"""

from flask_sqlalchemy import SQLAlchemy
import datetime

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

    charity_id = db.Column(db.Integer, primary_key = True)
    has_face = db.Column(db.Boolean)
    logo_url = db.Column(db.String)

    
class Charity(BaseModel, db.Model):
    """Model for the charity table"""
    __tablename__ = 'charity'

    charity_id = db.Column(db.String, primary_key = True)
    name = db.Column(db.String)
    category = db.Column(db.String)
    donation_options = db.Column(db.String)
    
    
class Description(BaseModel, db.Model):
    """Model for the description table"""
    __tablename__ = 'description'

    charity_id = db.Column(db.String, primary_key = True)
    description = db.Column(db.String)