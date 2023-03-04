import time
import json
import flask
import shared
from flask_login import login_required, current_user, login_user, logout_user
from authorization import driver, active

@shared.web_application.route("/get-total-accounts", methods=["GET"])
@login_required
def return_total_accounts():
    users = driver.MySQLInterface.GetUsers(driver._mysql, None)
    
    result = {"timestamps": [n.timestamp for n in users]}
    
    return json.dumps(result), 200

@shared.web_application.route("/get-chat-messages", methods=["GET"])
@login_required
def return_chat_messages():
    t_now = time.time()
    
    messages = driver.MySQLInterface.GetChatMessages(driver._mysql, 
        lambda message: t_now - message.timestamp < 86400
    )

    message_map = {"messages": [{"username": message.sender_name, "content": message.content, "timestamp": message.timestamp} for message in messages]}
    
    return json.dumps(message_map), 200