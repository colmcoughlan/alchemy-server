# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 22:34:42 2017

@author: colmc
"""

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from alchemy_server import app
from models import db


migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()