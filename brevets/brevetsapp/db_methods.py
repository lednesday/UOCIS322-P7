"""
Various methods for MongoDB
"""
import os
from pymongo import MongoClient


class Db:

    def __init__(self):
        self.client = MongoClient(
            'mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
        self.db = self.client.brevetdb  # name of the database we're using

    def drop_all(self, key={}):
        self.db.brevetcoll.drop(key)

    def insert_row(self, doc):
        self.db.brevetcoll.insert_one(doc)

    def find_content(self, key={}):
        return self.db.brevetcoll.find(key)

    def drop_one(self, key={}):
        self.db.brevetcoll.remove(key)
