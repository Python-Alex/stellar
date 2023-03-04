import flask
import shared
from flask_login import login_required, current_user, login_user, logout_user
from authorization import driver, active

@shared.web_application.route("/get-total-accounts", methods=["POST"])
def return_total_accounts():
    post_data = flask.request.form
    
    js_key = post_data['js_key']
    
    cursor = driver.MySQLInterface.GetCursor(driver._mysql)
    
    cursor.execute("select * from users")
    
    result = len(cursor.fetchall())
    
    return result