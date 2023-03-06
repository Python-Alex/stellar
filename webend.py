import os
import sys
import time
import flask
import string
import random
import logging
import threading
import datetime
from authorization import active, driver
from flask_login import LoginManager

# reset activity data
active.reset_data()

web_source_path = os.path.join(os.getcwd(), 'websrc')

application = flask.Flask(
    __name__, 
    template_folder=os.path.join(web_source_path, 'pages'), 
    static_folder=os.path.join(web_source_path, 'static')
)
application.secret_key = "123123123" #"".join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

login_manager = LoginManager()
login_manager.init_app(application)

application.jinja_env.globals.update(datetime=datetime, time=time)

application.permanent_session_lifetime = datetime.timedelta(minutes=60)

def webhost_thread():
    if(threading.current_thread().name == "MainThread"):
        raise threading.ThreadError("cannot execute in main thread")

    application.run(
        host="127.0.0.1",
        port=8081
    )


@login_manager.user_loader
def load_user(user_id):
    users = driver.MySQLInterface.GetUsers(driver._mysql, None)
    for user in users:
        if(user.id == user_id):
            recv_messages = driver.MySQLInterface.GetMessages(driver._mysql, lambda message: message.recipient_id == user.id)
            send_messages = driver.MySQLInterface.GetMessages(driver._mysql, lambda message: message.sender_id == user.id)
            notifications = driver.MySQLInterface.GetNotifications(driver._mysql, lambda notification: notification.recipient_id == user.id)
            
            user.recieved_messages = recv_messages
            user.sent_messages = send_messages
            user.notifications = notifications

            return user

# avoid starting thread from other file imports
if(__name__ == '__main__'):
    threading.Thread(target=driver.keep_alive).start()
    threading.Thread(target=webhost_thread).start()

    import shared
    
    shared.web_application = application

    import routes
    import storage_api
    import action_api
    from authorization import driver
