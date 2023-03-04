#type: ignore

import time
import flask
import shared
import base64
import hashlib
import string
import random
from datetime import timedelta
from flask_login import login_required, current_user, login_user, logout_user

from authorization import driver, active

def get_cookie_id(email: str)->str:
    return hashlib.md5(email.encode()).hexdigest()

@shared.web_application.errorhandler(404)
def handle_404(error):
    return flask.render_template("404.html", **{"error": error}), 404

@shared.web_application.errorhandler(401)
def handle_401(error):
    return flask.render_template("403.html", **{"error": error}), 403

@shared.web_application.route("/", methods=["GET"])
def index_render():
    
    if(current_user.get_id() == None):
        return flask.redirect(flask.url_for("login_render"))
    
    return flask.render_template("index2.html")

@shared.web_application.route("/login", methods=["GET", "POST"])
def login_render():
    request = flask.request
    session = flask.session
    
    rstatus = -1
    
    if(request.method == "POST"):
        credential_form = request.form.to_dict()
        
        cursor = driver.MySQLInterface.GetCursor(driver._mysql)
        users = driver.MySQLInterface.GetUsers(
            driver._mysql, 
            lambda entry: entry.email == credential_form['email'] and \
                entry.password == base64.b64encode(hashlib.md5(credential_form['password'].encode()).hexdigest().encode() + entry.salt.encode()).decode())
        
        if(not users or len(users) > 1):
            rstatus = 1 # FAILED | QUERY ERROR
            
        elif(len(users) == 1 and users[0].session == 0):
            rstatus = 0 # SUCCESS

            cursor.execute("UPDATE users SET session=1 WHERE id=%d " % (users[0].id))
            driver.MySQLInterface.driver.commit()
            
            login_user(users[0], remember=True, duration=timedelta(minutes=60))
            
        elif(users[0].session > 0):
            rstatus = 2 # ALREADY LOGGED IN
        
        return flask.render_template("login2.html", **{"status": rstatus}), 200
    
    elif(request.method == "GET"):
        return flask.render_template("login2.html", **{"status": rstatus}), 200
    
    else:
        return flask.render_template("403.html"), 403

@shared.web_application.route("/logout", methods=["GET", "POST"])
@login_required
def logout_render():
    cursor = driver.MySQLInterface.GetCursor(driver._mysql)
    cursor.execute("UPDATE users SET session=0 WHERE id=%d" % (current_user.get_id()))
    driver.MySQLInterface.driver.commit()
    
    logout_user()
    return flask.render_template("login2.html")

@shared.web_application.route("/register", methods=["GET", "POST"])
def register_render():
    request = flask.request
    session = flask.session
    
    rstatus = -1
    
    if(request.method == "POST"):
        credential_form = request.form.to_dict()

        cursor = driver.MySQLInterface.GetCursor(driver._mysql)
        users = driver.MySQLInterface.GetUsers(
            driver._mysql,
            lambda entry: entry.name == credential_form['username'] or entry.email == credential_form['email']
        )
        
        if(users):
            rstatus = 1
            
        elif(len(users) == 0):
            rstatus = 0
            
            salt = "".join(random.choice(string.ascii_letters) for _ in range(8))
            hash_password = base64.b64encode(hashlib.md5(credential_form['password'].encode()).hexdigest().encode() + salt.encode()).decode()
            cursor.execute(f'INSERT INTO users VALUES (NULL, "{credential_form["username"]}", "{credential_form["email"]}", "{hash_password}", {int(time.time())}, 0, 0, "{salt}")')
            
            driver.MySQLInterface.driver.commit()

        elif(credential_form['password'] != credential_form['password-repeat']):
            rstatus = 2
    
        return flask.render_template("register2.html", **{"status": rstatus}), 200
    
    elif(request.method == "GET"):
        return flask.render_template("register2.html", **{"status": rstatus}), 200
    
@shared.web_application.route("/dashboard", methods=["GET"])
@login_required
def render_dashboard():
    request = flask.request
    session = flask.session

    return flask.render_template("index2.html")
