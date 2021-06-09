from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
import flask
import requests  # not sure what for
from urllib.parse import urlparse, urljoin
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin,
                         confirm_login, fresh_login_required)  # TODO: why parens?
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators
from passlib.hash import sha256_crypt  # Ali recommended


app = Flask(__name__)

app.secret_key = "K@w@ zhn@ ng!-zh@bw!"

app.config.from_object(__name__)  # what is this?

login_manager = LoginManager()

login_manager.session_protection = "strong"

login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."

login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"

"""
Copied from flaskLogin.py model
Uses flask_wtf
"""


class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    password = StringField("Password",
                           [validators.Length(min=6, max=25,
                                              message=u"Password must have at least 6 characters"),
                            validators.InputRequired(u"Password required")])
    remember = BooleanField('Remember me')


class RegisterForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
                          message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    password = StringField("Password",
                           [validators.Length(min=6, max=25,
                                              message=u"Password must have at least 6 characters"),
                            validators.InputRequired(u"Password required")])


"""
Copied from flaskLogin.py model
For checking if "next" is safe, to avoid cross-site scripting attacks maybe???
used in @app.route("/login)
"""


def is_safe_url(target):
    """
    :source: https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

# TODO: make sure this is right
# see https://passlib.readthedocs.io/en/stable/lib/passlib.hash.sha256_crypt.html for documentation


def hash_password(password):
    # is probably sha256
    return sha256_crypt.using(salt="z1wtag3n").hash(password)


"""
Copied from flaskLogin.py model
Uses flask_login
"""

# TODO: what is this class used for? Sessions?


class User(UserMixin):
    def __init__(self, id, username, token):
        self.id = id
        self.username = username
        self.token = token


@login_manager.user_loader
def load_user(user_id):
    if "username" not in flask.session or "token" not in flask.session:
        return None
    username = flask.session["username"]
    token = flask.session["token"]
    return User(user_id, username, token)


login_manager.init_app(app)


@app.route('/')
@app.route('/index')
def home():
    return render_template('display_times.html')

# TODO: add is_authenticated to this function
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hash_password(password)
        result = requests.get(
            f'http://restapi:5000/token?username={username}&password={hashed_password}').json()
        token = result["token"]
        user_id = result["id"]
        if result["response"] == "success":  # token was successfully returned
            remember = request.form.get("remember", "false") == "true"
            login_user(User(user_id, username, token), remember=remember)
            flash("Logged in!")
            # set sesssions here
            flask.session["username"] = username
            flask.session["token"] = token
            flask.session["user_id"] = user_id
            flash("I'll remember you") if remember else None
            next = request.args.get("next")
            if not is_safe_url(next):
                abort(400)
            # TODO: don't I need to return the token?
            return redirect(next or url_for('home'))
        else:
            flash(u"Sorry, unable to log in.")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hash_password(password)
        post_data = {"username": username, "password": hashed_password}
        result = requests.post(
            'http://restapi:5000/register', data=post_data).json()
        print("result:", result)
        if result["response"] == "success":  # user was successfully registered
            login_result = requests.get(
                f'http://restapi:5000/token/?username={username}&password={hashed_password}').json()
            token = login_result["token"]
            user_id = login_result["id"]
            this_user = User(user_id, username, token)
            login_user(this_user)
            flash("Logged in!")
            # set sesssions here
            flask.session["username"] = username
            flask.session["token"] = token
            flask.session["user_id"] = user_id
            # set sesssions here
            next = request.args.get("next")
            if not is_safe_url(next):
                abort(400)
            return redirect(next or url_for('home'))
        else:
            flash(u"Sorry, unable to log in.")
    return render_template("register.html", form=form)

# TODO: next 3 routes need to know the token


@app.route('/listeverything')
@login_required
def listeverything():
    token = flask.session["token"]
    json_or_csv = request.args.get('format', "json", type=str)
    num_lines = request.args.get('lines', -1, type=int)
    r = requests.get(
        f'http://restapi:5000/listAll/{json_or_csv}?top={num_lines}&token={token}')
    return r.text


@app.route('/listopen')
@login_required
def listopen():
    token = flask.session["token"]
    json_or_csv = request.args.get('format', "json", type=str)
    num_lines = request.args.get('lines', -1, type=int)
    r = requests.get(
        f'http://restapi:5000/listOpenOnly/{json_or_csv}?top={num_lines}&token={token}')
    return r.text


@app.route('/listclose')
@login_required
def listclose():
    token = flask.session["token"]
    json_or_csv = request.args.get('format', "json", type=str)
    num_lines = request.args.get('lines', -1, type=int)
    r = requests.get(
        f'http://restapi:5000/listCloseOnly/{json_or_csv}?top={num_lines}&token={token}')
    return r.text


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
