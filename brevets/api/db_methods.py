"""
Various methods for MongoDB
"""
import os
from pymongo import MongoClient
from passlib.hash import sha256_crypt as pwd_context  # Ali recommended
# from passlib.apps import custom_app_context as pwd_context  # was in the model
from flask import current_app  # for logging


SECRET_KEY = 'g!m0z@b3'


class BrevetDb:

    def __init__(self):
        self.client = MongoClient(
            'mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
        self.db = self.client.brevetdb  # name of the database we're using

    def find_content(self, *args, **kwargs):
        return self.db.brevetcoll.find(*args, **kwargs)


class UserDb:
    def __init__(self):
        self.client = MongoClient(
            'mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
        self.db = self.client.userdb

    """
    Inserts username and hashed password into collection of username/password documents
    Returns True if successful, False if unsuccessful
    Is unsuccessful if username already exists in collection
    """

    def insert_user(self, username, password):
        # check to make sure username doesn't already exist
        already_exists = self.is_in_collection("username", username)
        if already_exists:
            return False
        # hash the password on the api side just in case it's not already hashed
        hashed_pw = self.hash_password(password)
        doc = {"username": username, "password": hashed_pw}
        self.db.usercoll.insert_one(doc)
        return True

    def verify_user(self, username, password):
        # current_app.logger.debug("username: " + username)
        if not self.is_in_collection("username", username):
            return False
        # current_app.logger.debug("made it past false return")
        user_data = self.db.usercoll.find_one({"username": username})
        stored_hash = user_data["password"]
        if self.verify_password(password, stored_hash):
            return user_data["_id"]
        return False

    def is_in_collection(self, key, value):
        already_exists = False
        val_list = list(self.db.usercoll.find({key: value}))
        # current_app.logger.debug("val_list:" + str(val_list))
        if len(val_list) != 0:
            already_exists = True
        return already_exists

    def hash_password(self, password):
        # is probably sha256
        print("password:", password)
        return pwd_context.encrypt(password)

    def verify_password(self, password, hashVal):
        return pwd_context.verify(password, hashVal)
