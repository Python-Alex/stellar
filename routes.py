#type: ignore


import re
import os
import time
import flask
import shared
import base64
import hashlib
import string
import random
import shutil
from datetime import timedelta
from flask_login import login_required, current_user, login_user, logout_user

from authorization import driver, active


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
def is_valid_email(email):
 
    if(re.fullmatch(regex, email)):
        return True

    return False

def get_cookie_id(email: str)->str:
    return hashlib.md5(email.encode()).hexdigest()

"""
@shared.web_application.before_request
def before_request_func():
    if(not flask.request.headers.get('CF-Connecting-Ip')):
        return flask.render_template("403.html", **{"error": "Cloudflare unable to resolve address"})
    
    connecting_address = flask.request.headers.get('CF-Connecting-Ip')
    if(not active.ActiveStack.users.get(connecting_address)):
        active.ActiveStack.new_connection(connecting_address)

    active.ActiveStack.request_callback(connecting_address)
"""

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
    rstatus = -1
    address = flask.request.headers.get('CF-Connecting-Ip')

    if(request.method == "POST"):
        credential_form = request.form.to_dict()

        users = driver.MySQLInterface.GetUsers(
            driver._mysql, 
            lambda entry: entry.email == credential_form['email'] and entry.password == hashlib.md5(credential_form['password'].encode() + entry.salt.encode()).hexdigest())


        if(not users or len(users) > 1):
            rstatus = 1 # FAILED | QUERY ERROR

        elif(len(users) == 1 and users[0].session == 0):
            rstatus = 0 # SUCCESS

            login_user(users[0], remember=True, duration=timedelta(days=(365 * 10)))
            
            if(address):
                active.ActiveStack.users[address]["userobject"] = current_user

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

    cursor.close()

    logout_user()
    return flask.render_template("login2.html")

@shared.web_application.route("/register", methods=["GET", "POST"])
def register_render():
    request = flask.request
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
            hash_password = hashlib.md5(credential_form['password'].encode() + salt.encode()).hexdigest()
            cursor.execute(f'INSERT INTO users VALUES (NULL, "{credential_form["username"]}", "{credential_form["email"]}", "{hash_password}", {int(time.time())}, 0, 0, "{salt}")')

            driver.MySQLInterface.driver.commit()

            cursor.execute("SELECT MAX(id) FROM users")

            shutil.copyfile(os.path.join(os.getcwd(), 'websrc', 'static', 'user_avatars', 'unset.png'), 
                            os.path.join(os.getcwd(), 'websrc', 'static', 'user_avatars', '%d.png' % (cursor.fetchall()[0])))

        elif(credential_form['password'] != credential_form['password-repeat']):
            rstatus = 2

        cursor.close()

        return flask.render_template("register2.html", **{"status": rstatus}), 200

    elif(request.method == "GET"):
        return flask.render_template("register2.html", **{"status": rstatus}), 200

@shared.web_application.route("/dashboard", methods=["GET"])
@login_required
def render_dashboard():
    return flask.render_template("index2.html")

@shared.web_application.route("/chat", methods=["GET"])
@login_required
def render_chatlounge():
    return flask.render_template("chatlounge.html")

@shared.web_application.route("/profile", methods=["GET"])
@login_required
def profile_render():
    return flask.render_template("profile.html")

@shared.web_application.route("/cp", methods=["GET"])
@login_required
def controlpanel_render():
    if(current_user.permission < 80):
        return flask.render_template("index2.html")

    return flask.render_template("controlpanel.html")

@shared.web_application.route("/tickets")
@login_required
def tickets_render():
    tickets = driver.MySQLInterface.GetSupportTickets(driver._mysql,
            lambda ticket: ticket.sender_id == current_user.get_id())

    print(tickets)

    return flask.render_template("supporttickets.html", **{"tickets": tickets})

@shared.web_application.route("/edit-profile", methods=["POST"])
@login_required
def profile_edit():
    request = flask.request
    form = request.form.to_dict()
    
    rstatus = -1
    a_upload = 0
    
    if(request.files['avatar_image']):
        request.files['avatar_image'].save(os.path.join(os.getcwd(), 'websrc', 'static', 'user_avatars', '%d.png' % (current_user.get_id())))
        a_upload = 1
    
    if(len(form['set_username']) < 4):
        rstatus = 1 # bad username length
        
    elif(not is_valid_email(form['set_email'])):
        rstatus = 2 # invalid email
        
        
    elif( hashlib.md5(form['password'].encode() + current_user.salt.encode()).hexdigest() != current_user.password):
        rstatus = 3 # bad password
        
    else:
        rstatus = 0
        cursor = driver.MySQLInterface.GetCursor(driver._mysql)
        cursor.execute('UPDATE users SET username="%s", email="%s" WHERE id=%d' % (form['set_username'], form['set_email'], current_user.get_id()))
        cursor.close()
        
        driver.MySQLInterface.driver.commit()
    
    return flask.render_template("profile.html", **{"status": rstatus, "uploaded": a_upload})