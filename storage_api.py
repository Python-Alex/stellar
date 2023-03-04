import json
import flask
import shared
from flask_login import login_required, current_user, login_user, logout_user
from authorization import driver, active

@shared.web_application.route("/get-total-accounts", methods=["GET"])
def return_total_accounts():
    cursor = driver.MySQLInterface.GetCursor(driver._mysql)
    users = driver.MySQLInterface.GetUsers(driver._mysql, None)
    
    result = {"timestamps": [n.timestamp for n in users]}
    
    return json.dumps(result), 200