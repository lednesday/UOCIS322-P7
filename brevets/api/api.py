# Streaming Service

from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from db_methods import BrevetDb, UserDb
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature,
                          SignatureExpired)
import time
import json

app = Flask(__name__)
api = Api(app)

# make a JSON element to return
brevDb = BrevetDb()
userDb = UserDb()

"""  user functions  """

VALID_SECONDS = 600  # 10 minutes
SECRET_KEY = 'g!m0z@b3'


class RegisterUser(Resource):
    def post(self):
        # form is for POST requests
        username = request.form.get('username', type=str)
        password = request.form.get('password', type=str)
        if userDb.insert_user(username, password):
            # TODO: should error codes be jsonified or defined or something?
            return {"status": "success"}, 201
        else:
            return {"status": "bad request"}, 400


class ReturnToken(Resource):
    def get(self):
        username = request.args.get('username', type=str)
        password = request.args.get('password', type=str)
        if userDb.verify_user(username, password):
            return {"status": "response", "token": self.generate_auth_token(username)}
        return {"response": "unauthorized"}, 401

    def generate_auth_token(self, username, expiration=600):
        # s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        s = Serializer(SECRET_KEY, expires_in=VALID_SECONDS)
        # pass index of user
        # convert to string because tokens are type bytes, which is not JSON
        return str(s.dumps({'username': username}))


"""  brevet functions  """


def verify_auth_token(token):
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    return "Success"


class ListAll(Resource):
    def get(self, dtype="json"):
        token = request.args.get("token", "", type=str)
        if len(token) == 0:
            return {"response": "empty token"}, 401
        if verify_auth_token(token) == "Success":
            data_list = list(brevDb.find_content(
                projection={"open_time": 1, "close_time": 1, "_id": 0}))
            num_lines = request.args.get('top', -1, type=int)
            if num_lines < 0 or num_lines > len(data_list):
                num_lines = len(data_list)
            data_list = data_list[:num_lines]
            if dtype == "json":
                return jsonify(data_list)
            elif dtype == "csv":
                if len(data_list) > 0:
                    csv_string = ", ".join(list(data_list[0].keys())) + '\n'
                    for datum in data_list:
                        csv_string += ", ".join(list(datum.values())) + '\n'
                    return csv_string
                else:
                    return ""
            else:
                return "something went wrong with the API"
        else:
            return {"response": "unauthorized"}, 401


class ListOpenOnly(Resource):
    def get(self, dtype="json"):
        token = request.args.get("token", "", type=str)
        if verify_auth_token(token) == "Success":
            data_list = list(brevDb.find_content(
                projection={"open_time": 1, "_id": 0}))
            num_lines = request.args.get('top', -1, type=int)
            if num_lines < 0 or num_lines > len(data_list):
                num_lines = len(data_list)
            data_list = data_list[:num_lines]
            if dtype == "json":
                return jsonify(data_list)
            elif dtype == "csv":
                if len(data_list) > 0:
                    csv_string = ", ".join(list(data_list[0].keys())) + '\n'
                    for datum in data_list:
                        csv_string += ", ".join(list(datum.values())) + '\n'
                    return csv_string
                else:
                    return ""
            else:
                return "something went wrong with the API"
        else:
            return {"status": "unauthorized"}, 401


class ListCloseOnly(Resource):
    def get(self, dtype="json"):
        token = request.args.get("token", "", type=str)
        if verify_auth_token(token) == "Success":
            data_list = list(brevDb.find_content(
                projection={"close_time": 1, "_id": 0}))
            num_lines = request.args.get('top', -1, type=int)
            if num_lines < 0 or num_lines > len(data_list):
                num_lines = len(data_list)
            data_list = data_list[:num_lines]
            if dtype == "json":
                return jsonify(data_list)
            elif dtype == "csv":
                if len(data_list) > 0:
                    csv_string = ", ".join(list(data_list[0].keys())) + '\n'
                    for datum in data_list:
                        csv_string += ", ".join(list(datum.values())) + '\n'
                    return csv_string
                else:
                    return ""
            else:
                return "something went wrong with the API"
        else:
            return {"status": "unauthorized"}, 401


# Create routes
# Another way, without decorators
api.add_resource(ListAll, '/listAll', '/listAll/<dtype>')
api.add_resource(ListOpenOnly, '/listOpenOnly', '/listOpenOnly/<dtype>')
api.add_resource(ListCloseOnly, '/listCloseOnly', '/listCloseOnly/<dtype>')
api.add_resource(RegisterUser, '/register')
api.add_resource(ReturnToken, '/token')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
