#type: ignore
import time
import json
import flask
import shared
from flask_login import login_required, current_user, login_user, logout_user
from authorization import driver, active

@shared.web_application.route("/submit-ticket", methods=["POST"])
@login_required
def send_ticket_request():
    form = flask.request.form.to_dict()
    
    rstatus = -1
    
    userid = current_user._get_current_object().get_id()
    users = driver.MySQLInterface.GetUsers(driver._mysql, 
            lambda user : user.id == userid)
    
    if(len(users) == 0):
        return flask.render_template("login2.html")
    
    username = users[0].name
    
    tickets = driver.MySQLInterface.GetSupportTickets(driver._mysql,
        lambda ticket : ticket.sender_id == userid)
    
    t_now = time.time()
    
    for ticket in tickets:
        if(t_now - ticket.timestamp < 600):
            rstatus = 1 # too fast sending tickets
            
        if(ticket.header == form['header']):
            rstatus = 2 # ticket already exists with header name
            
    if(rstatus == -1): # everything ok
        rstatus = 0
        priority = 0 if(form['priority'] == 'off') else 1 if(form['priority'] == 'on') else 0
        cursor = driver.MySQLInterface.GetCursor(driver._mysql)
        cursor.execute('INSERT INTO tickets VALUES (NULL, %d, "%s", "%s", "%s", "%s", %d, %d)' % (userid, username, form['header'], form['body'], "", priority, int(time.time())))
        driver.MySQLInterface.driver.commit()
        
        cursor.close()
    
    return flask.render_template("supporttickets.html", **{"status": rstatus})

@shared.web_application.route("/send-chat-message", methods=["POST"])
@login_required
def send_chat_message():
    form = json.loads(flask.request.data.decode())

    userid = form['userid']
    message = form['content']
    
    users = driver.MySQLInterface.GetUsers(driver._mysql, 
            lambda user: user.id == userid)
    
    if(len(users) == 0):
        return json.dumps({"error": "no user found"})
    
    user = users[0]
    
    cursor = driver.MySQLInterface.GetCursor(driver._mysql)
    
    cursor.execute('INSERT INTO chatlounge VALUES (NULL, %d, "%s", "%s", %d)' % (userid, user.name, message, int(time.time())))
    driver.MySQLInterface.driver.commit()
    
    cursor.close()
    
    return json.dumps({"error": 0})