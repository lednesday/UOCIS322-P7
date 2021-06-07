"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import os  # for environment - TODO: maybe not necessary because of config?
import flask
# borrowed from example
from flask import Flask, redirect, url_for, request, render_template, jsonify
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
from db_methods import Db
import json

from pymongo import MongoClient

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
# app.secret_key = CONFIG.SECRET_KEY

# moved connection with MongoDB to db_methods
# client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
# db = client.brevetdb  # name of the database we're using

db = Db()

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.route("/insert", methods=["POST"])
def insert():
    db.drop_all()
    # TODO: insert distance and start time - only if there's time
    # db.brevetcoll.insert_one(request.form['brevet_distance'])
    # db.brevetcoll.insert_one(request.form['start_time'])
    rows = json.loads(request.form.get("rows"))
    for row in rows:
        # {ident: ident, miles: miles, kms: kms, loc: loc, open: open, close: close, notes: notes}
        item_doc = {
            'row_num': row['ident'],
            'miles': row['miles'],
            'kms': row['kms'],
            'location': row['loc'],
            'open_time': row['open'],
            'close_time': row['close']
        }
        # brevetcoll is the collection we're using to track controles
        db.insert_row(item_doc)
    return jsonify({"status": "success"})


@app.route("/display")
def display():
    items = list(db.find_content())
    for item in items:
        del item["_id"]
    return jsonify(items)


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    # flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    brevet_dist = request.args.get('brevet_dist', 200, type=int)
    start_time_string = request.args.get(
        'start_time', '2021-02-20T14:00', type=str)
    start_time = arrow.get(start_time_string, 'YYYY-MM-DDTHH:mm')
    open_time = acp_times.open_time(
        km, brevet_dist, start_time).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(
        km, brevet_dist, start_time).format('YYYY-MM-DDTHH:mm')
    # TODO: include "success" and possibly "error" in result
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
