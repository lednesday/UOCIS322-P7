from flask import Flask, render_template, request, redirect, url_for, flash, abort
import requests  # not sure what for
from urllib.parse import urlparse, urljoin
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin,
                         confirm_login, fresh_login_required)  # TODO: why parens?
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, validators


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
    # password = ???
    remember = BooleanField('Remember me')


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


"""
Copied from flaskLogin.py model
Uses flask_login
"""


class User(UserMixin):
    def __init__(self, id, username, hashed_password):
        # TODO: where does id come from? what's it for?
        self.id = id
        self.username = username
        self.hashed_password = ""
        self.token = ""

    def set_username(self, username):
        self.username = username
        return self

    def set_hashed_password(self, hashed_password):
        # TODO: hashed_password? token?
        pass


@login_manager.user_loader
def load_user(user_id):
    # TODO: what to do here?
    return
    # return USERS[int(user_id)]


login_manager.init_app(app)


@app.route('/')
@app.route('/index')
def home():
    return render_template('display_times.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        if username in USER_NAMES:
            remember = request.form.get("remember", "false") == "true"
            if login_user(USER_NAMES[username], remember=remember):
                flash("Logged in!")
                flash("I'll remember you") if remember else None
                next = request.args.get("next")
                if not is_safe_url(next):
                    abort(400)
                return redirect(next or url_for('index'))
            else:
                flash("Sorry, but you could not log in.")
        else:
            flash(u"Invalid username.")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))


@app.route('/listeverything')
@login_required
def listeverything():
    json_or_csv = request.args.get('format', "json", type=str)
    num_lines = request.args.get('lines', -1, type=int)
    r = requests.get(
        f'http://restapi:5000/listAll/{json_or_csv}?top={num_lines}')
    return r.text


@app.route('/listopen')
@login_required
def listopen():
    json_or_csv = request.args.get('format', "json", type=str)
    num_lines = request.args.get('lines', -1, type=int)
    r = requests.get(
        f'http://restapi:5000/listOpenOnly/{json_or_csv}?top={num_lines}')
    return r.text


@app.route('/listclose')
@login_required
def listclose():
    json_or_csv = request.args.get('format', "json", type=str)
    num_lines = request.args.get('lines', -1, type=int)
    r = requests.get(
        f'http://restapi:5000/listCloseOnly/{json_or_csv}?top={num_lines}')
    return r.text


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
